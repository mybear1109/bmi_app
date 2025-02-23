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

def generate_text_via_api(prompt, model_name="google/gemma-2-9b-it"):
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
            return {"메시지": f"🚨 JSON 변환 오류: {json_text}"}
    except (json.JSONDecodeError, KeyError) as e:
        st.error(f"🚨 응답 처리 오류: {e}")
        return {"메시지": "🚨 응답 처리 오류"}

def get_user_info_with_default(user_data):
    """
    사용자 정보에 대해 미측정된 항목은 기본값으로 채워 반환합니다.
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
    식단의 경우 다이어트 목표, 저탄수화물 등을 명시하고 기피 음식 정보를 추가합니다.
    """
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"
    
    if category == "운동":
        prompt += "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요. 모든 대답은 반드시 한국어로 작성해주세요."
    elif category == "식단":
        prompt += ("사용자의 건강 상태와 체중 감량, 저탄수화물, 다이어트 목표에 맞는 7일 식단 계획을 JSON 형식으로 제공해 주세요. "
                   "모든 대답은 반드시 한국어로 작성해주세요. 다이어트 식단은 칼로리 조절과 균형 잡힌 영양소 구성이 반영되어야 합니다.")
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
        "- 모든 대답은 반드시 한국어로 작성해주세요.\n"
        "- 운동 계획은 구체적이어야 하며, 매일의 운동 내용과 소요 시간(분)을 포함해야 합니다.\n"
        "- 예시와 같이 7일치 운동 계획을 제공해 주세요.\n"
        "- 아래 예시를 참고하여 한국어로 작성해 주세요.\n"
        "- 운동 예시:\n"
        "[{'요일': ['월', '화', '수', '목', '금', '토', '일'], '운동': ['달리기 30분', '자전거 45분', '수영 30분', '휴식', '웨이트 60분', '달리기 45분', '휴식'], '칼로리 소모': [300, 400, 350, 0, 500, 450, 0]}]\n"
    )
    return generate_text_via_api(prompt)

def get_diet_recommendation(user_info, excluded_foods):
    """
    사용자의 건강 정보와 제외할 음식 목록을 포함한 7일 식단 계획 프롬프트를 구성하고,
    AI API를 호출하여 식단 추천 결과를 반환합니다.
    """
    prompt = f"사용자의 건강 상태를 고려한 7일 식단 계획을 JSON 형식으로 제공해 주세요.\n"
    prompt += f"사용자 정보: {json.dumps(user_info, ensure_ascii=False)}\n"
    prompt += f"제외할 음식: {', '.join(excluded_foods)}\n"
    prompt += (
        "- 모든 대답은 반드시 한국어로 작성해주세요.\n"
        "- 다이어트를 위한 식단은 칼로리 조절과 균형 잡힌 영양소(단백질, 탄수화물, 지방 비율)가 반영되어야 합니다.\n"
        "- 아침, 점심, 저녁 3끼 식단을 구체적으로 작성해 주세요.\n"
        "- 아래 예시를 참고하여 한국어로 작성해 주세요.\n"
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

# --- 결과 표시 함수 ---

def display_diet_plan(diet_plan):
    if isinstance(diet_plan, dict) and "메시지" in diet_plan:
        st.error(f"🚨 식단 추천 생성 중 문제가 발생했습니다: {diet_plan['메시지']}")
        st.markdown("**원시 응답:**")
        st.code(json.dumps(diet_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(diet_plan, dict):
        diet_plan = [diet_plan]
    if isinstance(diet_plan, list):
        df = pd.DataFrame(diet_plan)
        required_cols = ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]
        if not all(col in df.columns for col in required_cols):
            st.error("🚨 응답에 필요한 열이 없습니다. (요일, 아침, 점심, 저녁, 총칼로리 (kcal))")
            st.markdown("**원시 응답 데이터:**")
            st.json(diet_plan)
            if isinstance(diet_plan, list) and len(diet_plan) > 0 and isinstance(diet_plan[0], dict):
                raw_md = diet_plan[0].get("메시지", "")
                if raw_md:
                    display_raw_markdown(raw_md)
            return
        styled_df = (
            df[required_cols]
            .style
            .set_properties(**{'text-align': 'center', 'font-size': '16px'})
            .background_gradient(cmap='Blues', subset=["총칼로리 (kcal)"])
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.error("🚨 응답 형식 오류: 식단 추천 결과가 리스트 형식이 아닙니다.")

def display_exercise_plan(exercise_plan):
    if isinstance(exercise_plan, dict) and "메시지" in exercise_plan:
        st.error(f"🚨 운동 추천 생성 중 문제가 발생했습니다: {exercise_plan['메시지']}")
        st.markdown("**원시 응답:**")
        st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(exercise_plan, dict):
        exercise_plan = [exercise_plan]
    
    if (isinstance(exercise_plan, list) and exercise_plan and 
        isinstance(exercise_plan[0], dict) and "weekly_exercise_plan" in exercise_plan[0]):
        weekly_plan = exercise_plan[0].get("weekly_exercise_plan", [])
        transformed = []
        for day in weekly_plan:
            transformed.append({
                "요일": day.get("day", ""),
                "운동": day.get("focus", ""),
                "시간(분)": day.get("duration", ""),
                "칼로리 소모량(kcal)": "정보 없음"
            })
        exercise_plan = transformed
    
    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        required_cols = ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]
        if not all(col in df.columns for col in required_cols):
            st.error("🚨 응답에 필요한 열이 없습니다. (요일, 운동, 시간(분), 칼로리 소모량(kcal))")
            st.markdown("**원시 응답 데이터:**")
            st.json(exercise_plan)
            if isinstance(exercise_plan, list) and len(exercise_plan) > 0 and isinstance(exercise_plan[0], dict):
                raw_md = exercise_plan[0].get("메시지", "")
                if raw_md:
                    display_raw_markdown(raw_md)
            return
        styled_df = (
            df[required_cols]
            .style
            .set_properties(**{'text-align': 'center', 'font-size': '16px'})
            .background_gradient(cmap='Oranges', subset=["칼로리 소모량(kcal)"])
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#FF5722'), ('color', 'white')]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.error("🚨 응답 형식 오류: 운동 추천 결과가 리스트 형식이 아닙니다.")

# --- 메인 페이지 표시 함수 ---
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_data = load_user_data()
    user_info = process_user_info(user_data)
    
    st.subheader("🎛️ 맞춤 건강 프로필 설정")
    st.markdown("<br>", unsafe_allow_html=True)
    goal = st.selectbox("🎯 건강 목표", ["체중 관리", "근력 증진", "심혈관 건강 개선", "전반적 웰빙 향상"])
    user_info["목표"] = goal
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        excluded_foods = st.text_input("🚫 식품 알레르기 및 기피 항목 (쉼표로 구분)", "", key="excluded_foods")
        excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        diet_restriction = st.selectbox("🍽️ 식이 요법 유형", ["일반식", "채식", "육류 중심", "저탄수화물", "저지방", "글루텐 프리"])
    with col2:
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        st.markdown("<br>", unsafe_allow_html=True)
        restricted_exercises = st.text_input("⚠️ 운동 제한 사항 (쉼표로 구분)", "", key="restricted_exercises")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        exercise_preference = st.multiselect("🏃‍♀️ 선호하는 운동 유형", 
                                             ["유산소 운동", "근력 트레이닝", "유연성 운동", "균형 및 코어", 
                                              "고강도 인터벌 트레이닝", "요가", "필라테스"])
        st.markdown("<br>", unsafe_allow_html=True)
    
    user_info.update({
        "excluded_foods": excluded_foods,
        "preferred_foods": preferred_foods,
        "diet_restriction": diet_restriction,
        "restricted_exercises": restricted_exercises,
        "fitness_level": fitness_level,
        "exercise_preference": exercise_preference
    })
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 식단 계획 추천", key="diet_button"):
            with st.spinner("AI가 식단을 추천하는 중...⏳"):
                diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)
            display_diet_plan(diet_plan)
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동 계획을 추천하는 중...⏳"):
                exercise_plan = get_gemma_recommendation("운동", user_info)
            display_exercise_plan(exercise_plan)
