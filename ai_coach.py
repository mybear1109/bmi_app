import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import logging
from typing import List, Dict, Set

# 로깅 설정 (관리자용 로그는 콘솔에 출력되고, 사용자에게는 보이지 않음)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

# InferenceClient 객체 생성 (provider: hf-inference)
client = InferenceClient(
    provider="hf-inference",
    token=HF_API_KEY
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
        # ChatML 형식 응답 처리
        if isinstance(response_json, dict):
            content = response_json['choices'][0]['message']['content']
        else:
            content = response_json.choices[0].message.content

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
            json_text = json_text.replace("'", '"')
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            st.error(f"🚨 JSON 변환 오류 발생:\n{json_text}\n오류: {e}")
            # 변환 오류 발생 시 원시 텍스트를 반환하여 디버깅 정보를 함께 제공
            return {"메시지": json_text}
    except (json.JSONDecodeError, KeyError) as e:
        st.error(f"🚨 응답 처리 오류: {e}")
        return {"메시지": "🚨 응답 처리 오류"}

def get_user_info_with_default(user_data):
    """
    사용자 정보 중 '미측정' 항목은 기본값으로 채워 반환합니다.
    """
    default_info = {
        "BMI": 24.5,
        "허리둘레": "80cm",
        "수축기혈압(최고 혈압)": 120,
        "이완기혈압(최저 혈압)": 80,
        "혈압 차이": 40,
        "총콜레스테롤": 190,
        "고혈당 위험": "낮음",
        "간 지표": "정상",
        "성별": "남성",
        "연령대": "30대",
        "비만 위험 지수": "보통",
        "흡연상태": "비흡연",
        "음주여부": "비음주"
    }
    for key, value in user_data.items():
        if value == "미측정":
            user_data[key] = default_info.get(key, "미측정")
    return user_data

def expand_allergies(allergies: List[str]) -> Set[str]:
    """
    입력된 알레르기 목록을 미리 정의된 매핑을 통해 확장하여,
    관련 모든 식품 목록을 반환합니다.
    """
    allergy_mapping = {
        '계란': ['계란', '계란노른자', '계란흰자', '달걀', '노른자', '흰자'],
        '생선': ['생선', '연어', '참치', '광어'],
        '우유': ['우유', '요구르트', '치즈'],
        '콩': ['콩', '두부', '콩나물'],
        '밀가루': ['밀가루', '빵', '면'],
        '아몬드': ['아몬드', '호두', '땅콩'],
        '닭고기': ['닭고기', '닭가슴살', '닭날개'],
        '소고기': ['소고기', '소불고기', '소양지'],
        '돼지고기': ['돼지고기', '삼겹살', '목살'],
        '새우': ['새우', '게', '랍스터']
    }
    expanded = set()
    for allergy in allergies:
        if allergy in allergy_mapping:
            expanded.update(allergy_mapping[allergy])
        else:
            expanded.add(allergy)
    return expanded

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """
    Hugging Face API의 chat completions를 사용하여 텍스트를 생성합니다.
    prompt를 메시지 리스트로 변환하여 API 호출 후 응답을 파싱합니다.
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response_json = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return parse_json_response(response_json)
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 API 호출 오류: {e}")
        return {"메시지": "🚨 API 호출 오류 발생"}

def get_gemma_recommendation(category, user_info, additional_info=[]):
    """
    카테고리에 따라 운동 또는 식단 추천 요청 프롬프트를 구성하여 API 호출을 수행합니다.
    추가 정보(알레르기, 기호 등)는 튜플 리스트로 전달하며, 이를 프롬프트에 포함합니다.
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n\n"
    
    common_instructions = (
        "- 모든 응답은 반드시 한국어로 작성해 주세요.\n"
        "- 사용자의 건강 상태와 목표에 맞춘 상세한 7일 계획을 제공해야 합니다.\n"
        "- 결과는 JSON 형식으로 제공해 주세요.\n"
        "- 각 날짜별로 구체적인 계획을 포함해야 합니다.\n"
        "- 개인화된 추천을 제공하세요.\n"
    )
    
    if category == "운동":
        prompt += (
            "당신은 전문적인 AI 피트니스 코치입니다. 다음 지침을 따라 7일 운동 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 예시 형식:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': [{'종류': '달리기', '시간': 30, '칼로리 소모': 300}, {'종류': '스트레칭', '시간': 15, '칼로리 소모': 50}], '일일 총소모 칼로리': 350, '설명': '유산소 운동과 스트레칭으로 체지방 감소 및 유연성 향상'}]\n"
        )
        for info_type, info_value in additional_info:
            if info_type == "체력 수준":
                prompt += f"- 사용자의 체력 수준은 {info_value}입니다.\n"
            elif info_type == "선호하는 운동 유형":
                prompt += f"- 선호하는 운동 유형: {', '.join(info_value)}\n"
            elif info_type == "제한된 운동":
                prompt += f"- 다음 운동은 제외: {', '.join(info_value)}\n"
    elif category == "식단":
        prompt += (
            "당신은 전문 영양사입니다. 다음 지침을 따라 7일 식단 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 다이어트를 위한 식단은 칼로리 조절과 균형 잡힌 영양소(단백질, 탄수화물, 지방 비율)가 반영되어야 합니다.\n"
            "- 아침, 점심, 저녁 3끼 식단을 구체적으로 작성해 주세요.\n"
            "- 예시 형식:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '아침': {'메뉴': '계란 + 오트밀', '칼로리': 300}, '점심': {'메뉴': '닭가슴살 샐러드', '칼로리': 400}, '저녁': {'메뉴': '구운 채소 + 연어', '칼로리': 450}, '간식': {'메뉴': '그릭 요거트', '칼로리': 150}, '일일 총칼로리': 1300, '설명': '고단백 저탄수화물 식단으로 체지방 감소 도움'}]\n"
        )
        for info_type, info_value in additional_info:
            if info_type == "알레르기 및 기피 음식":
                prompt += f"- 제외할 음식: {', '.join(info_value)}\n"
            elif info_type == "선호하는 음식":
                prompt += f"- 선호하는 음식: {', '.join(info_value)}\n"
            elif info_type == "식이 요법":
                prompt += f"- 식이 요법: {info_value}\n"
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)
