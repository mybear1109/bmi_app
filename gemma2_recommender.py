import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import pandas as pd
import logging
import time
from typing import List, Dict, Set, Tuple

# 로깅 설정 (관리자용 로그는 콘솔에 출력되고, 사용자에게는 간략한 메시지만 표시)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

# InferenceClient 객체 생성 (provider: hf-inference)
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_KEY
)

def clean_control_characters(text: str) -> str:
    """텍스트 내의 제어문자(ASCII 0~31 등)를 제거합니다."""
    return re.sub(r'[\x00-\x1F]+', ' ', text)

def extract_json_from_message(message: str) -> str:
    """
    메시지가 "🚨 JSON 변환 오류:"로 시작하면 해당 접두사를 제거하고,
    백틱 블록이 있으면 그 내부만 추출합니다.
    """
    prefix = "🚨 JSON 변환 오류:"
    if message.startswith(prefix):
        message = message[len(prefix):].strip()
    if "```json" in message:
        message = message.split("```json")[-1].split("```")[0].strip()
    return message

def parse_json_response(response_json):
    """
    API 응답 객체에서 choices -> message -> content를 추출하여,
    백틱 블록 내의 JSON이 있으면 해당 부분만 파싱합니다.
    제어문자 제거와 후처리를 수행하여 JSON 데이터를 반환합니다.
    """
    try:
        # ChatML 형식 응답 처리 (올바른 인덱싱 사용)
        if isinstance(response_json, dict):
            content = response_json['choices'][0]['message']['content']
        else:
            content = response_json.choices[0].message.content

        # 제어문자 제거 및 좌우 공백 정리
        content = clean_control_characters(content.strip())
        if not content:
            st.error("🚨 응답 내용이 비어 있습니다.")
            return {"메시지": "응답 내용이 비어 있습니다."}
        
        # 백틱 블록이 있으면 그 내부만 사용, 없으면 전체 사용
        if "```json" in content:
            json_text = content.split("```json")[-1].split("```")[0].strip()
        else:
            json_text = content
        
        json_text = extract_json_from_message(json_text)
        try:
            # 작은따옴표를 큰따옴표로 치환 후 JSON 파싱 시도
            json_text = json_text.replace("'", '"')
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            st.error(f"🚨 JSON 변환 오류 발생:\n{json_text}\n오류: {e}")
            # 파싱 오류 발생 시 원시 텍스트를 반환 (디버깅용)
            return {"메시지": json_text}
    except (json.JSONDecodeError, KeyError) as e:
        st.error(f"🚨 응답 처리 오류: {e}")
        return {"메시지": "🚨 응답 처리 오류"}

def exponential_backoff(retry_count, base=1, factor=2):
    """지수 백오프 시간 계산 함수"""
    return base * (factor ** retry_count)

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """
    Hugging Face API의 chat completions를 사용하여 텍스트를 생성합니다.
    prompt를 메시지 리스트로 변환하여 API 호출 후 응답을 파싱합니다.
    재시도 로직을 포함하여 서버 오류에 대해 지수 백오프를 적용합니다.
    """
    messages = [{"role": "user", "content": prompt}]
    max_retries = 3
    retry_count = 0
    while retry_count <= max_retries:
        try:
            response_json = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return parse_json_response(response_json)
        except requests.exceptions.RequestException as e:
            sleep_time = exponential_backoff(retry_count)
            logger.error(f"Request failed: {str(e)}. Waiting {sleep_time} seconds before retry.")
            time.sleep(sleep_time)
            retry_count += 1
        # 재시도 횟수 초과 시
        if retry_count > max_retries:
            logger.error(f"Max retries ({max_retries}) exceeded for model: {model_name}")
            st.error("🚨 API 호출 오류: 최대 재시도 횟수를 초과했습니다.")
            return {"메시지": "🚨 API 호출 오류 발생"}
    return {"메시지": "🚨 API 호출 오류 발생"}

def get_gemma_recommendation(category: str, user_info: dict, additional_info: List[Tuple[str, List[str]]] = []):
    """
    카테고리에 따라 운동 또는 식단 추천 요청 프롬프트를 구성하여 API 호출을 수행합니다.
    추가 정보는 튜플 리스트로 전달되며, 예를 들어:
      - ("알레르기 및 기피 음식", allergen_foods)
      - ("선호하는 음식", preferred_foods)
      - ("식이 요법", [diet_restriction])
      - ("체력 수준", [fitness_level])
      - ("선호하는 운동 유형", exercise_preference)
      - ("제한된 운동", restricted_exercises)
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n\n"
    
    common_instructions = (
        "- 모든 응답은 반드시 한국어로 작성해 주세요.\n"
        "- 사용자의 현재 건강 상태와 목표에 맞춘 상세한 7일 계획을 제공해야 합니다.\n"
        "- 결과는 JSON 형식으로 제공해 주세요.\n"
        "- 각 날짜별로 구체적인 계획을 포함해야 합니다.\n"
        "- 개인화된 추천을 제공하세요.\n"
    )

    if category == "운동":
        prompt += (
            "당신은 전문적인 AI 피트니스 코치입니다. 다음 지침을 따라 7일 운동 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 사용자의 BMI, 체중, 활동 수준에 따라 운동 강도를 조정하세요.\n"
            "- 매일의 운동 계획에는 운동 종류, 시간(분), 예상 소모 칼로리를 포함하세요.\n"
            "- 상체, 하체, 코어 등 다양한 부위의 운동을 균형 있게 포함하세요.\n"
            "- 유산소 운동과 근력 운동을 적절히 조합하세요.\n"
            "- 스트레칭과 휴식일도 계획에 포함하세요.\n"
            "- 초보자를 위한 간단한 운동 방법 설명이나 주의사항을 포함하세요.\n"
            "- 운동의 이점과 권장 이유를 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 권장 운동량을 계산하여 제시하세요.\n"
            "- 각 운동의 소모 칼로리, 일일 총소모 칼로리, 주간 총소모 칼로리를 포함하세요.\n"
            "- 예시 형식:\n"
            "[{'요일': '월', '운동': [{'종류': '달리기', '시간': 30, '칼로리 소모': 300}, {'종류': '스트레칭', '시간': 15, '칼로리 소모': 50}], '일일 총소모 칼로리': 350, '설명': '유산소 운동과 스트레칭으로 체지방 감소 및 유연성 향상'}]\n"
        )
        for info_type, info_value in additional_info:
            if info_type == "체력 수준":
                prompt += f"- 사용자의 체력 수준은 {info_value[0]}입니다.\n"
            elif info_type == "선호하는 운동 유형":
                prompt += f"- 선호하는 운동 유형: {', '.join(info_value)}\n"
            elif info_type == "제한된 운동":
                prompt += f"- 다음 운동은 제외: {', '.join(info_value)}\n"
    elif category == "식단":
        prompt += (
            "당신은 전문 영양사입니다. 다음 지침을 따라 7일 식단 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 사용자의 체중 감량, 저탄수화물, 다이어트 목표에 맞는 식단을 구성하세요.\n"
            "- 매일의 식단 계획에는 아침, 점심, 저녁 메뉴와 각 끼니별 칼로리를 포함하세요.\n"
            "- 다양한 영양소가 균형 잡힌 식단을 구성하세요.\n"
            "- 칼로리 조절과 함께 단백질, 탄수화물, 지방의 적절한 비율을 고려하세요.\n"
            "- 식사 간 간식이나 야식에 대한 제안도 포함할 수 있습니다.\n"
            "- 각 음식의 영양적 이점을 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 일일 권장 칼로리를 계산하여 제시하세요.\n"
            "- 각 끼니별 칼로리, 일일 총칼로리, 주간 총칼로리를 포함하세요.\n"
            "- 예시 형식:\n"
            "[{'요일': '월', '아침': {'메뉴': '계란 + 오트밀', '칼로리': 300}, '점심': {'메뉴': '닭가슴살 샐러드', '칼로리': 400}, '저녁': {'메뉴': '구운 채소 + 연어', '칼로리': 450}, '간식': {'메뉴': '그릭 요거트', '칼로리': 150}, '일일 총칼로리': 1300, '설명': '고단백 저탄수화물 식단으로 체지방 감소 도움'}]\n"
        )
        # 추가 식단 정보 처리
        allergen_foods = []
        preferred_foods = []
        diet_restriction = ""
        for info_type, info_value in additional_info:
            if info_type == "알레르기 및 기피 음식":
                allergen_foods.extend(info_value)
            elif info_type == "선호하는 음식":
                preferred_foods.extend(info_value)
            elif info_type == "식이 요법":
                if info_value:
                    diet_restriction = info_value[0]
        if allergen_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(allergen_foods)}**"
        if preferred_foods:
            prompt += f"\n🚨 **선호하는 음식: {', '.join(preferred_foods)}**"
        if diet_restriction:
            prompt += f"\n🚨 **식이 요법: {diet_restriction}**"
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)

