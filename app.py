import streamlit as st
import pandas as pd
import os
import torch
import json
from user_data_utils import load_user_data, save_user_data
from gemma2_recommender import get_gemma_recommendation  # 수정된 부분

# 데이터 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
PREDICTION_FILE = os.path.join(BASE_DIR, "data", "predictions.csv")

# Hugging Face API Key 설정
HF_API_KEY = os.getenv("HF_API_KEY")  # Streamlit Secrets을 사용할 경우 `st.secrets["HF_API_KEY"]`

# 사용자 입력 폼 관련 코드
def display_ai_coach_page():
    """AI 건강 코치 페이지"""
    st.header("🏋️‍♂️ AI 건강 코치")

    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except json.JSONDecodeError:
            user_data = {}

    user_id = user_data.get("user_id", "게스트")
    user_info = {key: user_data.get(key, "미측정") for key in ["BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이", "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"]}

    st.subheader("⚙️ 개인화 설정")
    excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력", "")
    restricted_exercises = st.text_input("🏋️ 제한해야 할 운동", "")

    col1, col2 = st.columns(2)

    if st.button("🥗 식단 계획 추천", key="diet_button"):
        with st.spinner("AI가 식단을 추천하는 중...⏳"):
            diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)

        if diet_plan:
            st.success("✅ 맞춤형 식단 추천이 완료되었습니다!")
            st.subheader("🥗 7일 맞춤형 식단 계획")
            st.dataframe(pd.DataFrame(diet_plan), use_container_width=True)

    if st.button("🏋️ 운동 계획 추천", key="workout_button"):
        with st.spinner("AI가 운동 계획을 추천하는 중...⏳"):
            exercise_plan = get_gemma_recommendation("운동", user_info)

        if exercise_plan:
            st.success("✅ 맞춤형 운동 추천이 완료되었습니다!")
            st.subheader("🏋️ 7일 맞춤형 운동 계획")
            st.dataframe(pd.DataFrame(exercise_plan), use_container_width=True)

