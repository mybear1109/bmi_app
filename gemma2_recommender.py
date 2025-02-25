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
    else:
        return "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"
    
    for info_type, info_value in additional_info:
        if info_value:
            prompt += f"\n- {info_type}: {', '.join(info_value)}"
    
    return generate_text_via_api(prompt)
