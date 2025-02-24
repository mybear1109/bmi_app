import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict, Set

# 로깅 설정
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
    """메시지에서 JSON 부분을 추출합니다."""
    prefix = "🚨 JSON 변환 오류:"
    if message.startswith(prefix):
        message = message[len(prefix):].strip()
    if "```json" in message:
        message = message.split("```json")[-1].split("```")[0].strip()
    return message

def parse_json_response(response_json):
    """
    API 응답 객체에서 choices -> message -> content를 추출하여,
    백틱 블록이 있으면 해당 부분만 파싱합니다.
    제어문자 제거와 외국어 사용 제한을 위한 후처리를 수행합니다.
    """
    try:
        if isinstance(response_json, dict):
            content = response_json['choices']['message']['content']
        else:
            content = response_json.choices.message.content

        content = clean_control_characters(content.strip())
        if not content:
            st.error("🚨 응답 내용이 비어 있습니다.")
            return {"메시지": "응답 내용이 비어 있습니다."}
        
        json_text = extract_json_from_message(content)
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

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """Hugging Face API를 사용하여 텍스트를 생성합니다."""
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
        "- 모든 응답은 반드시 한국어로 작성해주세요.\n"
        "- 사용자의 현재 건강 상태와 목표에 맞춘 상세한 7일 계획을 제공해야 합니다.\n"
        "- 결과는 JSON 형식으로 제공해 주세요.\n"
        "- 각 날짜별로 구체적인 계획을 포함해야 합니다.\n"
        "- 사용자의 건강 정보를 기반으로 개인화된 추천을 제공하세요.\n"
    )

    if category == "운동":
        prompt += (
            "당신은 전문적인 AI 피트니스 코치입니다. 다음 지침을 따라 7일 운동 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 사용자의 BMI, 체중, 활동 수준에 따라 운동 강도를 조정하세요.\n"
            "- 매일의 운동 계획에는 운동 종류, 시간(분), 예상 소모 칼로리를 포함하세요.\n"
            "- 상체, 하체, 코어 등 다양한 부위의 운동을 균형있게 포함하세요.\n"
            "- 유산소 운동과 근력 운동을 적절히 조합하세요.\n"
            "- 스트레칭과 휴식일도 계획에 포함하세요.\n"
            "- 초보자를 위한 간단한 운동 방법 설명이나 주의사항을 포함하세요.\n"
            "- 운동의 이점과 권장 이유를 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 권장 운동량을 계산하여 제시하세요.\n"
            "- 각 운동의 소모 칼로리, 일일 총소모 칼로리, 주간 총소모 칼로리를 포함하세요.\n"
        )
        
        # 추가 운동 정보 처리
        for info_type, info_value in additional_info:
            if info_type == "체력 수준":
                prompt += f"- 사용자의 체력 수준은 {info_value}입니다. 이에 맞는 운동 강도를 제안해주세요.\n"
            elif info_type == "선호하는 운동 유형":
                prompt += f"- 사용자가 선호하는 운동 유형은 {', '.join(info_value)}입니다. 이를 고려하여 계획을 세워주세요.\n"
            elif info_type == "제한된 운동":
                prompt += f"- 다음 운동은 제외해주세요: {', '.join(info_value)}\n"
        
        prompt += (
            "예시 형식:\n"
            """
            [
              {
                "요일": "월",
                "운동": [
                  {"종류": "달리기", "시간": 30, "칼로리 소모": 300},
                  {"종류": "스트레칭", "시간": 15, "칼로리 소모": 50}
                ],
                "일일 총소모 칼로리": 350,
                "설명": "유산소 운동으로 체지방 감소, 스트레칭으로 유연성 향상"
              },
              // 화요일부터 토요일까지 같은 형식으로 반복
              {
                "요일": "일",
                "운동": [
                  {"종류": "요가", "시간": 60, "칼로리 소모": 200},
                  {"종류": "가벼운 산책", "시간": 30, "칼로리 소모": 100}
                ],
                "일일 총소모 칼로리": 300,
                "설명": "요가로 근력과 유연성 향상, 가벼운 산책으로 회복 촉진"
              },
              {"주간 총소모 칼로리": 2450}
            ]
            """
        )
    elif category == "식단":
        prompt += (
            "당신은 전문 영양사입니다. 다음 지침을 따라 7일 식단 계획을 작성해 주세요:\n"
            f"{common_instructions}"
            "- 사용자의 체중 감량, 저탄수화물, 다이어트 목표에 맞는 식단을 구성하세요.\n"
            "- 매일의 식단 계획에는 아침, 점심, 저녁 메뉴와 각 끼니별 칼로리를 포함하세요.\n"
            "- 다양한 영양소가 균형잡힌 식단을 구성하세요.\n"
            "- 칼로리 조절과 함께 단백질, 탄수화물, 지방의 적절한 비율을 고려하세요.\n"
            "- 식사 간 간식이나 야식에 대한 제안도 포함할 수 있습니다.\n"
            "- 각 음식의 영양적 이점을 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 일일 권장 칼로리를 계산하여 제시하세요.\n"
            "- 각 끼니별 칼로리, 일일 총칼로리, 주간 총칼로리를 포함하세요.\n"
        )
        
        # 추가 식단 정보 처리
        for info_type, info_value in additional_info:
            if info_type == "알레르기 및 기피 음식":
                prompt += f"- 다음 음식은 제외해주세요: {', '.join(info_value)}\n"
            elif info_type == "선호하는 음식":
                prompt += f"- 사용자가 선호하는 음식은 {', '.join(info_value)}입니다. 이를 고려하여 계획을 세워주세요.\n"
            elif info_type == "식이 요법":
                prompt += f"- 사용자의 식이 요법은 {info_value}입니다. 이에 맞는 식단을 구성해주세요.\n"
        
        prompt += (
            "예시 형식:\n"
            """
            [
              {
                "요일": "월",
                "아침": {"메뉴": "계란 + 오트밀", "칼로리": 300},
                "점심": {"메뉴": "닭가슴살 샐러드", "칼로리": 400},
                "저녁": {"메뉴": "구운 채소 + 연어", "칼로리": 450},
                "간식": {"메뉴": "그릭 요거트", "칼로리": 150},
                "일일 총칼로리": 1300,
                "설명": "고단백 저탄수화물 식단으로 체지방 감소 도움"
              },
              // 화요일부터 토요일까지 같은 형식으로 반복
              {
                "요일": "일",
                "아침": {"메뉴": "과일 스무디", "칼로리": 250},
                "점심": {"메뉴": "현미밥 + 두부 스테이크", "칼로리": 450},
                "저녁": {"메뉴": "닭가슴살 + 퀴노아", "칼로리": 400},
                "간식": {"메뉴": "견과류 믹스", "칼로리": 200},
                "일일 총칼로리": 1300,
                "설명": "다양한 영양소를 균형있게 섭취하는 식단"
              },
              {"주간 총칼로리": 9100}
            ]
            """
        )
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)

