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
    token=HF_API_KEY
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

def get_gemma_recommendation(category: str, user_info: Dict, allergies: List[str] = [], excluded_foods: List[str] = []):
    """카테고리에 따라 운동 또는 식단 추천을 생성합니다."""
    user_info_text = json.dumps(user_info, ensure_ascii=False)
    prompt = f"사용자 건강 상태: {user_info_text}\n"
    
    if category == "운동":
        prompt += (
            "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요. "
            "모든 대답은 반드시 한국어로 작성해 주세요. 한국어 외의 다른 언어는 사용하지 마세요.\n"
            "- 예시:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': ['달리기 30분', '자전거 45분', '수영 30분', '휴식', '웨이트 60분', '달리기 45분', '휴식'], '칼로리 소모':[300][400][350][500][450]}]\n"
        )
    elif category == "식단":
        prompt += (
            "사용자의 건강 상태와 체중 감량, 저탄수화물, 다이어트 목표에 맞는 7일 식단 계획을 JSON 형식으로 제공해 주세요. "
            "모든 대답은 반드시 한국어로 작성해 주세요. 다이어트 식단은 칼로리 조절과 균형 잡힌 영양소 구성이 반영되어야 합니다.\n"
            "- 예시:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '아침': ['계란 + 오트밀', '그릭 요거트', '과일 + 견과류','칼로리 (kcal)':[500]], '점심': ['닭가슴살 샐러드', '연어 샐러드', '현미밥 + 야채','칼로리 (kcal)':[500]], '저녁': ['구운 채소', '찐 생선', '닭가슴살','칼로리 (kcal)':[500]], '총칼로리 (kcal)':[1500][1550][1600][1500][1550][1600][1500]}]\n"
        )
        all_excluded_foods = set(expand_allergies(allergies) | set(excluded_foods))
        if all_excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(all_excluded_foods)}**"
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)