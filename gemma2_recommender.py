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
        "고혈당 위험": "보통",
        "간 지표": "정상",
        "성별": "남성",
        "연령대": "30대",
        "비만 위험 지수": "보통",
        "흡연상태": "비흡연",
        "음주여부": "비음주"
    }
    return {key: user_data.get(key, default_info.get(key, "미측정")) for key in default_info}
def expand_allergies(allergen_foods: List[str]) -> Set[str]:
    """
    입력된 알레르기 목록을 미리 정의된 매핑을 통해 확장하여,
    관련 모든 식품 목록을 반환합니다.
    """
    allergen_foods_mapping = {
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
    expanded = set()
    for allergen_foods in allergen_foods:
        if allergen_foods in allergen_foods_mapping:
            expanded.update(allergen_foods_mapping[allergen_foods])
        else:
            expanded.add(allergen_foods)
    return expanded

def get_gemma_recommendation(category: str, user_info: Dict[str, str], additional_info: List[Tuple[str, List[str]]] = []) -> str:
    """
    운동 또는 식단 추천을 위한 프롬프트를 구성하고 API를 호출합니다.
    모든 응답은 반드시 한국어로 작성해주세요.
    사용자의 건강 정보를 기반으로 개인화된 추천을 제공하세요
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False)
    prompt = f"사용자 건강 상태: {user_info_text}\n\n"
    
    if category == "운동":
        prompt += (
            "당신은 AI 피트니스 코치입니다. 사용자의 건강 상태를 고려한 7일 운동 계획을 작성해 주세요.\n"
            "운동 예시:\n"
            "[{'요일': '월', '운동': [{'종류': '달리기', '시간': 30, '칼로리 소모': 300}, {'종류': '스트레칭', '시간': 15, '칼로리 소모': 50}], '설명': '유산소 운동과 스트레칭으로 체지방 감소 및 유연성 향상'}]"
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
            "당신은 AI 영양사입니다. 사용자의 건강 상태를 고려한 7일 식단 계획을 작성해 주세요.\n"
            "- 사용자의 체중 감량, 저탄수화물, 다이어트 목표에 맞는 식단을 구성하세요.\n"
            "- 매일의 식단 계획에는 아침, 점심, 저녁 메뉴와 각 끼니별 칼로리를 포함하세요.\n"
            "- 다양한 영양소가 균형잡힌 식단을 구성하세요.\n"
            "- 칼로리 조절과 함께 단백질, 탄수화물, 지방의 적절한 비율을 고려하세요.\n"
            "- 식사 간 간식이나 야식에 대한 제안도 포함할 수 있습니다.\n"
            "- 각 음식의 영양적 이점을 간략히 설명하세요.\n"
            "- 목표 체중 달성을 위한 일일 권장 칼로리를 계산하여 제시하세요.\n"
            "식단 예시:\n"
            "[{'요일': '월', '아침': {'메뉴': '계란 + 오트밀', '칼로리': 300}, '점심': {'메뉴': '닭가슴살 샐러드', '칼로리': 400}, '저녁': {'메뉴': '구운 채소 + 연어', '칼로리': 450}, '설명': '고단백 저탄수화물 식단으로 체지방 감소 도움'}]"
        )
        for info_type, info_value in additional_info:
            if info_type == "알레르기 및 기피 음식":
                prompt += f"- 제외할 음식: {', '.join(info_value)}\n"
            elif info_type == "선호하는 음식":
                prompt += f"- 선호하는 음식: {', '.join(info_value)}\n"
            elif info_type == "식이 요법":
                prompt += f"- 식이 요법: {info_value}\n"
    else:
        return "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"
    
    for info_type, info_value in additional_info:
        if info_value:
            prompt += f"\n- {info_type}: {', '.join(info_value)}"
    
    return generate_text_via_api(prompt)
