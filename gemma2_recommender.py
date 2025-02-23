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

def generate_text_via_api(prompt, model_name="google/gemma-2b-it"):
    """
    Hugging Face API의 chat completions를 사용하여 텍스트 생성.
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
    JSON 형식의 블록이 있으면 해당 부분만 파싱하여 반환합니다.
    """
    try:
        if isinstance(response_json, dict):
            content = response_json['choices'][0]['message']['content']
        else:
            content = response_json.choices[0].message.content

        content = content.strip()
        if not content:
            st.error("🚨 응답 내용이 비어 있습니다.")
            return {"메시지": "응답 내용이 비어 있습니다."}
        
        # 백틱으로 감싼 JSON 블록이 있으면 그 내부만 추출
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
            # 변환 오류가 발생해도 원시 텍스트를 반환하여 사용자에게 보여줌
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
    return list(expanded)

def get_gemma_recommendation(category, user_info, allergies=[], excluded_foods=[]):
    """
    카테고리에 따라 운동 또는 식단 추천 요청 프롬프트를 구성하여 API 호출을 수행합니다.
    식단의 경우, 다이어트 목표와 저탄수화물 식단 등을 명시하고 기피 음식 정보를 추가합니다.
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"
    
    if category == "운동":
        prompt += "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요. 모든 대답은 반드시 한국어로 작성해 주세요. " \
                  "한국어 외의 다른 언어는 사용하지 마세요.\n"
    elif category == "식단":
        prompt += ("사용자의 건강 상태와 체중 감량, 저탄수화물, 다이어트 목표에 맞는 7일 식단 계획을 JSON 형식으로 제공해 주세요. "
                   "모든 대답은 반드시 한국어로 작성해 주세요. 다이어트 식단은 칼로리 조절과 균형 잡힌 영양소 구성이 반영되어야 합니다.")
        expanded_allergies = expand_allergies(allergies)
        all_excluded_foods = set(expanded_allergies + excluded_foods)
        if all_excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(all_excluded_foods)}**"
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
        "- 모든 대답은 반드시 한국어로 작성해 주세요. 한국어 외의 다른 언어는 사용하지 마세요.\n"
        "- 운동 계획은 구체적이어야 하며, 매일의 운동 내용과 소요 시간(분)을 포함해야 합니다.\n"
        "- 아래 예시를 참고하여 한국어로 7일치 운동 계획을 제공해 주세요.\n"
        "- 운동 예시:\n"
        "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': ['달리기 30분', '자전거 45분', '수영 30분', '휴식', '웨이트 60분', '달리기 45분', '휴식'], '칼로리 소모': [300, 400, 350, 0, 500, 450, 0]}]\n"
    )
    return generate_text_via_api(prompt)

def get_diet_recommendation(user_info, excluded_foods):
    """
    사용자의 건강 정보와 제외할 음식 목록을 포함한 7일 식단 계획 프롬프트를 구성하고,
    AI API를 호출하여 식단 추천 결과를 반환합니다.
    """
    prompt = f"사용자의 건강 상태를 고려한 7일 식단 계획을 JSON 형식으로 제공해 주세요. 모든 대답은 반드시 한국어로 작성해 주세요. " \
             "한국어 외의 다른 언어는 사용하지 마세요.\n"
    prompt += f"사용자 정보: {json.dumps(user_info, ensure_ascii=False)}\n"
    prompt += f"제외할 음식: {', '.join(excluded_foods)}\n"
    prompt += (
        "- 다이어트를 위한 식단은 칼로리 조절과 균형 잡힌 영양소(단백질, 탄수화물, 지방 비율)가 반영되어야 합니다.\n"
        "- 아침, 점심, 저녁 3끼 식단을 구체적으로 작성해 주세요.\n"
        "- 아래 예시를 참고하여 한국어로 7일 식단 계획을 제공해 주세요.\n"
        "- 예시:\n"
        "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '아침': ['계란 + 오트밀', '그릭 요거트', '과일 + 견과류', '계란 + 토스트', '오트밀', '그릭 요거트', '과일 스무디'], '점심': ['닭가슴살 샐러드', '연어 샐러드', '현미밥 + 야채', '닭가슴살 샐러드', '연어 샐러드', '현미밥 + 야채', '닭가슴살 샐러드'], '저녁': ['구운 채소', '찐 생선', '닭가슴살', '구운 채소', '찐 생선', '닭가슴살', '구운 채소'], '총칼로리 (kcal)': [1500, 1550, 1600, 1500, 1550, 1600, 1500]}]\n"
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
