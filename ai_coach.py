from openai import OpenAI
import json
import re
import os
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict, Set
from gemma2_recommender import get_gemma2_recommender, get_exercise_recommendation, get_meal_recommendation

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

# 사용자 데이터 불러오기 함수
def load_user_data():
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            return json.loads(user_data)
        except json.JSONDecodeError:
            return {}
    return user_data

# 사용자 건강 정보 처리 함수
def process_user_info(user_data):
    """
    사용자 데이터에서 필요한 건강 정보를 추출합니다.
    """
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)",
        "혈압 차이", "총콜레스테롤", "간 지표", "성별", "나이", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    
    return {key: user_data.get(key, None) for key in required_keys}

# 식단 추천 결과 표시 함수
def display_diet_plan(diet_plan):
    if isinstance(diet_plan, dict) and "메시지" in diet_plan:
        st.error("🚨 식단 추천 생성 중 문제가 발생했습니다. (관리자 로그 참조)")
        st.code(json.dumps(diet_plan, indent=4, ensure_ascii=False))
        return
    
    df = pd.DataFrame(diet_plan)
    st.dataframe(df, use_container_width=True)

# 운동 추천 결과 표시 함수
def display_exercise_plan(exercise_plan):
    if isinstance(exercise_plan, dict) and "메시지" in exercise_plan:
        st.error("🚨 운동 추천 생성 중 문제가 발생했습니다. (관리자 로그 참조)")
        st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    
    df = pd.DataFrame(exercise_plan)
    st.dataframe(df, use_container_width=True)

# Streamlit 메인 페이지
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
        allergen_foods = st.text_input("🚫 식품 알레르기 및 기피 항목 (쉼표로 구분)", "", key="allergen_foods")
        allergen_foods = [food.strip() for food in allergen_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
    with col2:
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["선택 안함", "매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        st.markdown("<br>", unsafe_allow_html=True)
    
    user_info.update({
        "allergen_foods": allergen_foods,
        "preferred_foods": preferred_foods,
        "fitness_level": fitness_level
    })
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 식단 계획 추천", key="diet_button"):
            with st.spinner("AI가 식단을 추천하는 중...⏳"):
                diet_plan = get_meal_recommendation(user_info, allergen_foods)
            display_diet_plan(diet_plan)
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동을 추천하는 중...⏳"):
                exercise_plan = get_exercise_recommendation(user_info)
            display_exercise_plan(exercise_plan)
