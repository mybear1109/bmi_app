import json
import re
import requests
import os
import streamlit as st
import logging
from typing import List, Dict, Set, Tuple
import pandas as pd
from huggingface_hub import InferenceClient

def get_huggingface_token():
    """환경 변수 또는 Streamlit secrets에서 Hugging Face API 토큰을 가져옵니다."""
    return st.secrets.get("HUGGINGFACE_API_TOKEN")

def clean_input(text: str) -> str:
    """불필요한 단어(해줘, 알려줘 등)를 제거한 사용자 입력을 반환"""
    return re.sub(r"\b(해줘|알려줘|설명해 줘|말해 줘)\b", "", text, flags=re.IGNORECASE).strip()

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """Hugging Face API를 사용하여 텍스트를 생성합니다."""
    token = get_huggingface_token()
    client = InferenceClient(model=model_name, api_key=token)
    response = client.text_generation(prompt=prompt)
    return response

def get_user_info_with_default(user_data: Dict[str, str]) -> Dict[str, str]:
    """사용자 정보 중 '미측정' 항목은 기본값으로 채워 반환합니다."""
    default_info = {
        "BMI": "23",
        "허리둘레": "80cm",
        "수축기혈압(최고 혈압)": "120",
        "이완기혈압(최저 혈압)": "80",
        "혈압 차이": "40",
        "총콜레스테롤": "190",
        "고혈당 위험": "낮음",
        "간 지표": "정상",
        "성별": "남성",
        "연령대": "30대",
        "비만 위험 지수": "보통",
        "흡연상태": "비흡연",
        "음주여부": "비음주"
    }
    return {key: user_data.get(key, default_info.get(key, "미측정")) for key in default_info}

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



def get_gemma_recommendation(category: str, user_info: Dict[str, str], additional_info: List[Tuple[str, List[str]]] = []) -> str:
    """
        - 모든 응답은 반드시 한국어로 작성해주세요.\n
        - 사용자의 현재 건강 상태와 목표에 맞춘 상세한 7일 계획을 제공해야 합니다.\n
        - 각 날짜별로 구체적인 계획을 포함해야 합니다.\n
        - 사용자의 건강 정보를 기반으로 개인화된 추천을 제공하세요.\n
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False)
    prompt = f"사용자 건강 상태: {user_info_text}\n\n"
    
    if category == "운동":
        prompt += (
            "당신은 전문적인 AI 피트니스 코치입니다. 다음 지침을 따라 7일 운동 계획을 작성해 주세요:\n"
            "- 전문가나 전문의사와 상담을 받기를 권장해주세요 "
            "- 사용자의 BMI, 체중, 활동 수준에 따라 운동 강도를 조정하세요.\n"
            "- 매일의 운동 계획에는 운동 종류, 시간(분), 예상 소모 칼로리를 포함하세요.\n"
            "- 상체, 하체, 코어 등 다양한 부위의 운동을 균형있게 포함하세요.\n"
            "- 유산소 운동과 근력 운동을 적절히 조합하세요.\n"
            "- 스트레칭과 휴식일도 계획에 포함하세요.\n"
            "- 각 운동의 이점과 권장 빈도, 시간을 설명하세요.\n"
            "- 운동제한사항 또는 선호하는 운동 유형을 고려하세요.\n"
            "- 목표 체중 달성을 위한 일일 권장 운동량을 계산하여 제시하세요.\n"
            "- 초보자를 위한 간단한 운동 방법 설명이나 주의사항을 포함하세요.\n"
            "- 운동의 이점과 권장 이유를 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 권장 운동량을 계산하여 제시하세요.\n"
            "- 각 운동의 소모 칼로리, 일일 총소모 칼로리, 주간 총소모 칼로리를 포함하세요.\n"
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
            "- 사용자의 체중 감량, 저탄수화물, 다이어트 목표에 맞는 식단을 구성하세요.\n"
            "- 매일의 식단 계획에는 아침, 점심, 저녁 메뉴와 각 끼니별 칼로리를 포함하세요.\n"
            "- 다양한 영양소가 균형잡힌 식단을 구성하세요.\n"
            "- 칼로리 조절과 함께 단백질, 탄수화물, 지방의 적절한 비율을 고려하세요.\n"
            "- 식사 간 간식이나 야식에 대한 제안도 포함할 수 있습니다.\n"
            "- 각 음식의 영양적 이점을 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 일일 권장 칼로리를 계산하여 제시하세요.\n"
            "- 각 끼니별 칼로리, 일일 총칼로리, 주간 총칼로리를 포함하세요.\n"
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
        return "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"
    
    for info_type, info_value in additional_info:
        if info_value:
            prompt += f"\n- {info_type}: {', '.join(info_value)}"
    
    return generate_text_via_api(prompt)