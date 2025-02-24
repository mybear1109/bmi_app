from openai import OpenAI
import json
import re
import os
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict, Set

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

def get_gemma2_recommender(prompt: str):
    """
    AI 모델을 활용하여 운동 또는 식단을 추천합니다.
    """
    client = OpenAI(
        base_url="https://router.huggingface.co/novita",
        api_key=HF_API_KEY
    )
    
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="google/gemma-2-9b-it",
        messages=messages,
    )
    
    return completion.choices[0].message.content

def extract_json_from_message(message: str) -> str:
    """메시지에서 JSON 부분을 추출합니다."""
    match = re.search(r'```json\n(.*?)\n```', message, re.DOTALL)
    return match.group(1) if match else message

def get_exercise_recommendation(user_info: dict):
    """
    운동 추천 프롬프트를 생성하고 AI 응답을 받습니다.
    """
    prompt = f"사용자 건강 상태: {json.dumps(user_info, ensure_ascii=False)}\n\n"
    prompt += "운동 계획을 위한 7일 맞춤형 일정을 제공해 주세요.\n"
    prompt += "각 날짜마다 운동 종류, 시간(분), 예상 소모 칼로리를 포함해야 합니다."
    
    return get_gemma2_recommender(prompt)

def get_meal_recommendation(user_info: dict, allergies: List[str] = []):
    """
    식단 추천 프롬프트를 생성하고 AI 응답을 받습니다.
    """
    expanded_allergies = expand_allergies(allergies)
    prompt = f"사용자 건강 상태: {json.dumps(user_info, ensure_ascii=False)}\n\n"
    prompt += f"알러지 고려: {', '.join(expanded_allergies)}\n"
    prompt += "식단 계획을 위한 7일 맞춤형 일정을 제공해 주세요.\n"
    prompt += "각 날짜마다 아침, 점심, 저녁, 간식과 예상 칼로리를 포함해야 합니다."
    
    return get_gemma2_recommender(prompt)

def load_allergy_mapping() -> Dict[str, List[str]]:
    """알러지 매핑 데이터를 로드합니다."""
    return {
        '계란': ['계란', '계란노른자', '계란흰자', '달걀', '마요네즈'],
        '생선': ['생선', '연어', '참치', '고등어', '멸치'],
        '우유': ['우유', '유제품', '치즈', '요구르트', '버터'],
        '밀': ['밀', '밀가루', '글루텐', '파스타', '빵'],
        '콩': ['콩', '두부', '된장', '간장'],
        '견과류': ['아몬드', '호두', '땅콩', '캐슈넛'],
        '갑각류': ['새우', '게', '랍스터'],
        '과일': ['복숭아', '사과', '배', '키위'],
        '육류': ['닭고기', '소고기', '돼지고기'],
    }

def expand_allergies(allergies: List[str]) -> Set[str]:
    """입력된 알러지 목록을 확장하여 관련 모든 식품 목록을 반환합니다."""
    allergy_mapping = load_allergy_mapping()
    expanded_allergies: Set[str] = set()
    for allergy in allergies:
        expanded_allergies.update(allergy_mapping.get(allergy, [allergy]))
    return expanded_allergies
