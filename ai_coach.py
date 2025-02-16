import streamlit as st
import pandas as pd
import os
from kogpt2_recommender import load_kogpt2_model, get_recommendations, parse_recommendation_to_table

# ✅ 상수 정의
PREDICTION_FILE = "data/predictions.csv"

# ✅ 사용자 데이터 로드 함수
def load_user_data(user_id):
    if user_id and os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        user_data = df[df['user_id'] == user_id]
        return user_data.iloc[-1].to_dict() if not user_data.empty else {}
    return {}

# ✅ 사용자 정보 표 출력 함수
def display_user_info_table(user_info):
    df_info = pd.DataFrame(list(user_info.items()), columns=["항목", "정보"])
    st.table(df_info)

# ✅ 추천 결과 표시 함수
def display_recommendation_table(title, text, filter_items=None, plan_type=None):
    df = parse_recommendation_to_table(text)
    st.subheader(title)
    if df is not None and not df.empty:
        if filter_items and plan_type:
            df = filter_recommendation(df, filter_items, plan_type)
        st.table(df)
    else:
        st.write(text)

# ✅ 추천 결과 필터링 함수
def filter_recommendation(df, filter_items, plan_type):
    if plan_type == "운동":
        return df[~df.apply(lambda row: any(item.lower() in row.to_string().lower() for item in filter_items), axis=1)]
    elif plan_type == "식단":
        return filter_allergy_ingredients(df, filter_items)
    return df

# ✅ 식단에서 알러지 음식 제거
def filter_allergy_ingredients(df, excluded_foods):
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
        '새우': ['새우', '게', '랍스터'],
    }
    
    excluded_items = set()
    for food in excluded_foods:
        food = food.strip().lower()
        excluded_items.update(allergy_mapping.get(food, [food]))

    return df[~df.apply(lambda row: any(item in row.to_string().lower() for item in excluded_items), axis=1)]

# ✅ AI 건강 코치 페이지
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치 페이지")

    tokenizer, model = load_kogpt2_model()
    if tokenizer is None or model is None:
        st.error("🚨 모델 로딩 실패로 AI 건강 코치를 사용할 수 없습니다.")
        return
  
    user_data = st.session_state.get("user_data", {})
    user_id = user_data.get("user_id")
    existing_user_data = load_user_data(user_id)

    user_info = {
        "키": existing_user_data.get("키", user_data.get("키", 170)),
        "현재 체중 (kg)": existing_user_data.get("체중", user_data.get("현재 체중 (kg)", 70)),
        "목표 체중 (kg)": existing_user_data.get("목표 체중", user_data.get("목표 체중 (kg)", 65)),
        "나이": existing_user_data.get("나이", user_data.get("나이", 25)),
        "성별": existing_user_data.get("성별", user_data.get("성별", "남성")),
        "활동 수준": existing_user_data.get("활동 수준", user_data.get("활동 수준", "중간활동")),
        "BMI": existing_user_data.get("BMI", "미측정"),
        "체지방률": existing_user_data.get("체지방률", "미측정"),
    }

    with st.expander("📌 사용자 정보 보기", expanded=True):
        display_user_info_table(user_info)

    col1, col2 = st.columns(2)
    with col1:
        excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "").split(',')
    with col2:
        restricted_exercises = st.text_input("🏋️ 제한해야 할 운동 (쉼표 구분)", "").split(',')

    if st.button("🏋️ 운동 계획 추천"):
        workout_plan_text = get_recommendations("운동", user_info, tokenizer, model)
        display_recommendation_table("🏋️ 운동 계획", workout_plan_text, restricted_exercises, "운동")

    if st.button("🥗 식단 계획 추천"):
        diet_plan_text = get_recommendations("식단", user_info, tokenizer, model)
        display_recommendation_table("🥗 식단 계획", diet_plan_text, excluded_foods, "식단")

    if st.button("🤖 AI 건강 상담"):
        consultation_text = get_recommendations("건강 상담", user_info, tokenizer, model)
        display_recommendation_table("🤖 AI 건강 상담", consultation_text)

