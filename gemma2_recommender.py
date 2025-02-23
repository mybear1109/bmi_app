import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import pandas as pd

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

# InferenceClient 객체 생성 (provider: hf-inference)
client = InferenceClient(
    provider="hf-inference",
    api_key=HF_API_KEY
)

def clean_control_characters(text):
    """
    텍스트 내의 제어문자(ASCII 0~31 등)를 제거합니다.
    """
    return re.sub(r'[\x00-\x1F]+', ' ', text)

def extract_json_from_message(message):
    """
    메시지가 "🚨 JSON 변환 오류:"로 시작하면 이를 제거하고,
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
    백틱 블록이 있으면 해당 부분만 파싱합니다.
    제어문자 제거와 외국어 사용 제한을 위한 후처리를 수행합니다.
    """
    try:
        if isinstance(response_json, dict):
            content = response_json['choices'][0]['message']['content']
        else:
            content = response_json.choices[0].message.content

        # 제어문자 제거 및 좌우 공백 정리
        content = clean_control_characters(content.strip())
        if not content:
            st.error("🚨 응답 내용이 비어 있습니다.")
            return {"메시지": "응답 내용이 비어 있습니다."}
        
        # 만약 백틱 블록이 있다면 그 내부만 사용
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

def get_user_info_with_default(user_data):
    """
    사용자 정보 중 '미측정' 항목을 기본값으로 채워 반환합니다.
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

def expand_allergies(allergies):
    """
    입력된 알레르기 목록을 미리 정의된 매핑을 통해 확장하여,
    관련 모든 식품 목록을 반환합니다.
    """
    allergy_mapping = {
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
        '기타': ['초콜릿', '카카오', '커피', '알코올', '인공감미료', '방부제']
    }
    
    expanded_allergies = set()
    for allergy in allergies:
        if allergy.lower() in allergy_mapping:
            expanded_allergies.update(allergy_mapping[allergy.lower()])
        else:
            expanded_allergies.add(allergy)
    
    return list(expanded_allergies)


def generate_text_via_api(prompt, model_name="google/gemma-2b-it"):
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

def get_gemma_recommendation(category, user_info, allergies=[], excluded_foods=[]):
    """
    카테고리에 따라 운동 또는 식단 추천 요청 프롬프트를 구성하여 API 호출을 수행합니다.
    식단의 경우, 다이어트 및 저탄수화물 목표를 강조하며 기피 음식 정보를 추가합니다.
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"
    
    if category == "운동":
        prompt += (
            "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요. "
            "모든 대답은 반드시 한국어로 작성해 주세요. 한국어 외의 다른 언어는 사용하지 마세요.\n"
            "- 예시:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': ['달리기 30분', '자전거 45분', '수영 30분', '휴식', '웨이트 60분', '달리기 45분', '휴식'], '칼로리 소모': [300, 400, 350, 0, 500, 450, 0]}]\n"
        )
    elif category == "식단":
        prompt += (
            "사용자의 건강 상태와 체중 감량, 저탄수화물, 다이어트 목표에 맞는 7일 식단 계획을 JSON 형식으로 제공해 주세요. "
            "모든 대답은 반드시 한국어로 작성해 주세요. 다이어트 식단은 칼로리 조절과 균형 잡힌 영양소 구성이 반영되어야 합니다.\n"
            "- 예시:\n"
            "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '아침': ['계란 + 오트밀', '그릭 요거트', '과일 + 견과류'], '점심': ['닭가슴살 샐러드', '연어 샐러드', '현미밥 + 야채'], '저녁': ['구운 채소', '찐 생선', '닭가슴살'], '총칼로리 (kcal)': [1500, 1550, 1600, 1500, 1550, 1600, 1500]}]\n"
        )
        expanded_allergies = expand_allergies(allergies)
        all_excluded_foods = set(expanded_allergies + excluded_foods)
        if all_excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(all_excluded_foods)}**"
    else:
        return {"메시지": "🚨 올바른 카테고리를 입력하세요: '운동' 또는 '식단'"}
    
    return generate_text_via_api(prompt)
