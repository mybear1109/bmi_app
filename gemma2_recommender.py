import json
import re
import requests
import os
import streamlit as st
import logging
from typing import List, Dict, Set, Tuple
import pandas as pd


# Hugging Face API 토큰 가져오기

def get_huggingface_token():
    """환경 변수 또는 Streamlit secrets에서 Hugging Face API 토큰을 가져옵니다."""
    return st.secrets.get("HUGGINGFACE_API_TOKEN")


# 텍스트 생성 함수 (HTTP 에러 핸들링 추가)

def generate_text_via_api(
    prompt: str,
    model_name: str = "mistralai/Mistral-Small-24B-Instruct-2501",
    system_msg: str = "You are a helpful AI assistant."
) -> str:
    """Hugging Face Together API를 사용하여 대화형 텍스트를 생성합니다."""
    token = get_huggingface_token()
    api_url = "https://router.huggingface.co/together/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 메시지 구성
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 1024
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        # 사용자에게 에러 표시
        st.error(f"❌ API 요청 실패 (HTTP {response.status_code})")
        st.code(response.text, language="json")
        # 로깅
        logging.error(f"HuggingFace API HTTP error: {http_err}, response: {response.text}")
        return "죄송합니다. 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
    except Exception as err:
        st.error(f"❌ API 요청 중 오류 발생: {err}")
        logging.error(f"HuggingFace API unexpected error: {err}")
        return "죄송합니다. 예기치 못한 오류가 발생했습니다."

    data = response.json()
    # 첫 번째 응답 메시지 내용 반환
    return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


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
        '계란': ['계란', '계란노른자', '계란흰자', '에그', '스크램블 에그', '달걀', '노른자', '흰자', '마요네즈', '메렝게', '타르타르 소스'],
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
        '기타': ['초콜릿', '카카오', '커피', '알코올', '알콜', '인공감미료', '방부제']
    }
    expanded = set()
    for allergen in allergen_foods:
        key = allergen.lower().strip()
        if key in allergen_foods_mapping:
            expanded.update(allergen_foods_mapping[key])
        else:
            for k, values in allergen_foods_mapping.items():
                if key in values:
                    expanded.update(values)
                    break
            else:
                expanded.add(allergen)
    return expanded


def get_gemma_recommendation(
    category: str,
    user_info: Dict[str, str],
    additional_info: List[Tuple[str, List[str]]] = []
) -> str:
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
            "- 상체, 하체, 코어 등 다양한 부위의 운동을 균형있게 포함하세요.\n"
            "- 유산소 운동과 근력 운동을 적절히 조합하세요.\n"
            "- 스트레칭과 휴식일도 계획에 포함하세요.\n"
            "- 링피트의 경우 사용자의 체력 수준과 선호 운동 유형을 고려하여 운동을 추천하세요.\n"
            "- 운동의 난이도와 시간을 적절히 조절하여 사용자에게 부담이 되지 않도록 하세요.\n"
            "- 1회 운동 시간과 주간 운동 가능 일수를 고려하여 운동 계획을 작성하세요.\n"
            "- 주로 운동하는 장소와 선호하는 운동 유형을 고려하여 운동을 추천하세요.\n"
            "- 초보자를 위한 간단한 운동 방법 설명이나 주의사항을 포함하세요.\n"
            "운동 예시:\n"
            "[{'요일': '월', '운동': [{'종류': '달리기', '시간': 30, '칼로리 소모': 300}, {'종류': '스트레칭', '시간': 15, '칼로리 소모': 50}], '설명': '유산소 운동과 스트레칭으로 체지방 감소 및 유연성 향상'}]"
        )
        for info_type, info_value in additional_info:
            if info_type == "체력 수준":
                prompt += f"- 사용자의 체력 수준은 {info_value[0]}입니다.\n"
            elif info_type == "선호 운동":
                prompt += f"- 선호하는 운동 유형: {', '.join(info_value)}\n"
            elif info_type == "운동 제한":
                prompt += f"- 다음 운동은 제외하고 대체 운동을 제안하세요: {', '.join(info_value)}\n"

    elif category == "식단":
        prompt += (
            "당신은 AI 영양사입니다. 사용자의 건강 상태를 고려한 7일 식단 계획을 작성해 주세요.\n"
            "- 사용자의 체중 감량, 저탄수화물, 다이어트 목표에 맞는 식단을 구성하세요.\n"
            "- 매일의 식단 계획에는 아침, 점심, 저녁 메뉴와 각 끼니별 칼로리를 포함하세요.\n"
            "- 다양한 영양소가 균형잡힌 식단을 구성하세요.\n"
            "- 요리실력에 맞게 간단하고 쉽게 준비할 수 있는 요리를 포함하세요.\n"
            "- 식사 준비 시간이 짧은 사용자를 위한 레시피를 포함하세요.\n"
            "- 식사 준비에 할애할 수 있는 시간을 고려하여 식단을 계획하세요.\n"
            "- 칼로리 조절과 함께 단백질, 탄수화물, 지방의 적절한 비율을 고려하세요.\n"
            "- 식사 간 간식이나 야식에 대한 제안도 포함할 수 있습니다.\n"
            "- 목표 체중 달성을 위한 일일 권장 칼로리를 계산하여 제시하세요.\n"
            "식단 예시:\n"
            "[{'요일': '월', '아침': {'메뉴': '계란 + 오트밀', '칼로리': 300}, '점심': {'메뉴': '닭가슴살 샐러드', '칼로리': 400}, '저녁': {'메뉴': '구운 채소 + 연어', '칼로리': 450}, '설명': '고단백 저탄수화물 식단으로 체지방 감소 도움'}]"
        )
        allergen_foods = []
        for info_type, info_value in additional_info:
            if info_type == "알레르기 식품":
                allergen_foods.extend(info_value)
                allergen_foods_mapping = [f"{food}({', '.join(expand_allergies([food]))})" for food in info_value]
            elif info_type == "선호 식품":
                prompt += f"- 선호하는 음식: {', '.join(info_value)}\n"
            elif info_type == "식이 제한":
                prompt += f"- 식이 요법: {info_value[0]}\n"
        
        if allergen_foods:
            expanded_allergies = expand_allergies(allergen_foods)
            prompt += f"- 주의: 다음 음식은 완전히 제외하고 대체 식품을 사용하세요: {', '.join(expanded_allergies)}\n"
            prompt += f"- 알레르기 식품이 포함된 모든 요리와 재료를 피하고, 교차 오염에 주의하세요.{', '.join(allergen_foods_mapping)}\n"
            prompt += "- 각 끼니마다 알레르기 식품이 포함되지 않았는지 다시 한 번 확인하세요.\n"  
            prompt += f"- 운동 제한 사항에 대해 다시 한 번 확인하세요{', '.join(allergen_foods_mapping)}\n"

    else:
        return "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"
    
    return generate_text_via_api(prompt)
