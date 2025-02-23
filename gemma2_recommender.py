import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import logging
from typing import List, Dict, Set
import pandas as pd

# 로깅 설정 (개발자용, 사용자에게는 노출되지 않음)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    백틱 블록 내의 JSON이 있으면 해당 부분만 파싱하고,
    제어문자 제거 및 후처리를 수행하여 JSON 데이터를 반환합니다.
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
            return {"메시지": json_text}
    except (json.JSONDecodeError, KeyError) as e:
        st.error(f"🚨 응답 처리 오류: {e}")
        return {"메시지": "🚨 응답 처리 오류"}

def load_allergy_mapping() -> Dict[str, List[str]]:
    """알러지 매핑 데이터를 로드합니다."""
    return {
        '계란': ['계란', '계란노른자', '계란흰자', '달걀', '노른자', '흰자', '마요네즈', '메렝게', '타르타르 소스'],
        '생선': ['생선', '연어', '참치', '광어', '고등어', '멸치', '오징어', '문어', '조개', '굴', '홍합'],
        '우유': ['우유', '유제품', '우유단백질', '우유당', '치즈', '요구르트', '버터', '크림', '아이스크림', '카제인'],
        '밀': ['밀', '밀가루', '글루텐', '파스타', '빵', '과자', '케이크', '시리얼', '맥주'],
        '콩': ['콩', '두부', '콩나물', '된장', '간장', '미소', '템페', '에다마메'],
        '견과류': ['아몬드', '호두', '땅콩', '캐슈넛', '피스타치오', '마카다미아', '헤이즐넛', '피칸'],
        '갑각류': ['새우', '게', '랍스터', '가재', '크랩스틱'],
        '과일': ['복숭아', '사과', '배', '키위', '망고', '파인애플', '딸기', '오렌지'],
        '육류': ['닭고기', '소고기', '돼지고기', '양고기', '오리고기'],
        '해산물': ['조개류', '굴', '홍합', '전복', '오징어', '문어'],
        '견과류 및 씨앗': ['참깨', '들깨', '해바라기씨', '호박씨', '아마씨'],
        '채소': ['셀러리', '당근', '토마토', '시금치', '브로콜리'],
        '향신료': ['마늘', '양파', '생강', '고추', '후추'],
        '기타': ['초콜릿', '카카오', '커피', '알코올', '알콜','인공감미료', '방부제']
    }

def validate_allergy(allergy: str) -> str:
    """알러지 입력값을 검증하고 표준화합니다."""
    return allergy.lower().strip()

def expand_allergies(allergies: List[str]) -> Set[str]:
    """입력된 알러지 목록을 확장하여 관련 모든 식품 목록을 반환합니다."""
    allergy_mapping = load_allergy_mapping()
    expanded_allergies: Set[str] = set()
    unknown_allergies: Set[str] = set()

    for allergy in allergies:
        validated_allergy = validate_allergy(allergy)
        if validated_allergy in allergy_mapping:
            expanded_allergies.update(allergy_mapping[validated_allergy])
        else:
            unknown_allergies.add(validated_allergy)
            expanded_allergies.add(validated_allergy)
    
    if unknown_allergies:
        logging.warning(f"알 수 없는 알러지 항목: {', '.join(unknown_allergies)}")
    
    return expanded_allergies

def get_allergy_info(allergies: List[str]) -> Dict[str, Set[str]]:
    """알러지 정보를 확장하고 카테고리별로 분류합니다."""
    allergy_mapping = load_allergy_mapping()
    expanded = expand_allergies(allergies)
    categorized: Dict[str, Set[str]] = {category: set() for category in allergy_mapping.keys()}
    
    for item in expanded:
        categorized_flag = False
        for category, items in allergy_mapping.items():
            if item in items:
                categorized[category].add(item)
                categorized_flag = True
        if not categorized_flag:
            if '기타' not in categorized:
                categorized['기타'] = set()
            categorized['기타'].add(item)
    
    return {k: v for k, v in categorized.items() if v}

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2b-it"):
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
                prompt += f"- 사용자의 체력 수준은 {info_value[0]}입니다.\n"
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
                prompt += f"- 식이 요법: {info_value[0]}\n"
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)

def get_exercise_recommendation(user_info):
    """
    사용자의 건강 정보와 목표에 기반하여 7일 운동 계획 프롬프트를 구성하고,
    AI API를 호출하여 운동 계획 추천 결과를 반환합니다.
    """
    prompt = f"사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요.\n"
    prompt += f"사용자 정보: {json.dumps(user_info, ensure_ascii=False)}\n\n"
    prompt += (
        "- 모든 응답은 반드시 한국어로 작성해 주세요. 한국어 외의 다른 언어는 사용하지 마세요.\n"
        "- 운동 계획은 구체적이어야 하며, 매일의 운동 내용과 소요 시간(분)을 포함해야 합니다.\n"
        "- 아래 예시를 참고하여 한국어로 7일치 운동 계획을 제공해 주세요.\n"
        "- 운동 예시:\n"
        "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': [{'종류': '달리기', '시간': 30, '칼로리 소모': 300}, {'종류': '스트레칭', '시간': 15, '칼로리 소모': 50}], '일일 총소모 칼로리': 350, '설명': '유산소 운동과 스트레칭으로 체지방 감소 및 유연성 향상'}]\n"
    )
    return generate_text_via_api(prompt)

def get_diet_recommendation(user_info, excluded_foods):
    """
    사용자의 건강 정보와 제외할 음식 목록을 포함한 7일 식단 계획 프롬프트를 구성하고,
    AI API를 호출하여 식단 추천 결과를 반환합니다.
    """
    prompt = f"사용자의 건강 상태를 고려한 7일 식단 계획을 JSON 형식으로 제공해 주세요. 모든 응답은 반드시 한국어로 작성해 주세요. " \
             "한국어 외의 다른 언어는 사용하지 마세요.\n"
    prompt += f"사용자 정보: {json.dumps(user_info, ensure_ascii=False)}\n"
    prompt += f"제외할 음식: {', '.join(excluded_foods)}\n"
    prompt += (
        "- 다이어트를 위한 식단은 칼로리 조절과 균형 잡힌 영양소(단백질, 탄수화물, 지방 비율)가 반영되어야 합니다.\n"
        "- 아침, 점심, 저녁 3끼 식단을 구체적으로 작성해 주세요.\n"
        "- 아래 예시를 참고하여 한국어로 7일 식단 계획을 제공해 주세요.\n"
        "- 예시:\n"
        "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '아침': {'메뉴': '계란 + 오트밀', '칼로리': 300}, '점심': {'메뉴': '닭가슴살 샐러드', '칼로리': 400}, '저녁': {'메뉴': '구운 채소 + 연어', '칼로리': 450}, '간식': {'메뉴': '그릭 요거트', '칼로리': 150}, '일일 총칼로리': 1300, '설명': '고단백 저탄수화물 식단으로 체지방 감소 도움'}]\n"
    )
    return generate_text_via_api(prompt)

def handle_ai_response(response):
    """
    AI 응답을 JSON, Markdown 테이블 또는 일반 텍스트로 변환합니다.
    """
    if isinstance(response, dict) and "메시지" in response:
        response_text = response["메시지"]
        try:
            parsed_response = json.loads(response_text)
            if isinstance(parsed_response, list):
                return parsed_response
        except json.JSONDecodeError:
            pass
        if "|" in response_text:
            return parse_markdown_table(response_text)
        return response_text
    elif isinstance(response, list):
        return response
    else:
        return None

def display_formatted_data(response):
    """
    응답 데이터를 적절한 형태로 변환하여 표시합니다.
    """
    parsed_data = handle_ai_response(response)
    if isinstance(parsed_data, pd.DataFrame):
        st.dataframe(parsed_data, use_container_width=True)
    elif isinstance(parsed_data, list):
        df = pd.DataFrame(parsed_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.markdown(f"```\n{parsed_data}\n```")

def parse_markdown_table(text):
    """
    Markdown 형식의 표를 DataFrame으로 변환 (빈 열 자동 제거)
    """
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return None
    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    data = [row.split("|")[1:-1] for row in lines[2:]]
    filtered_data = [row for row in data if len(row) == len(headers)]
    if not filtered_data:
        return None
    df = pd.DataFrame(filtered_data, columns=headers)
    return df.to_dict(orient="records")
