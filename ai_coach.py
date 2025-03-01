import streamlit as st
import json
import pandas as pd
from google_gemma_2b_it import get_gemma_recommendation

def load_user_data():
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            return json.loads(user_data)
        except json.JSONDecodeError:
            return {}
    return user_data

def display_recommendation(recommendation, title):
    if not recommendation:
        st.error(f"🚨 {title} 추천 생성 중 문제가 발생했습니다.")
        st.text(recommendation)
        return
    
    if isinstance(recommendation, str):
        st.subheader(f"{title} 추천 결과")
        st.text(recommendation)
        return
    
    if isinstance(recommendation, list):
        try:
            df = pd.DataFrame(recommendation)
            st.subheader(f"{title} 추천 결과")
            st.dataframe(df, use_container_width=True)
        except ValueError:
            st.error(f"🚨 {title} 추천 데이터를 테이블로 변환하는 중 오류 발생")
            st.text(recommendation)
            return

def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")
    user_data = load_user_data()
    
    st.subheader("맞춤 건강 프로필 설정")
    goal = st.selectbox("🎯 건강 목표", ["체중 관리", "근력 증진", "심혈관 건강 개선", "전반적 웰빙 향상"])
    user_data["목표"] = goal
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        allergen_foods = st.text_input("🚫 식품 알레르기 및 기피 항목 (쉼표로 구분)", "", key="allergen_foods",placeholder="예: 달걀, 땅콩,오이")
        allergen_foods = [food.strip() for food in allergen_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods",placeholder="예: 달걀, 당근, 면")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        diet_restriction = st.selectbox("🍽️ 식이 요법 유형", ["선택 안함", "일반식", "채식", "육류 중심", "저탄수화물", "저지방", "글루텐 프리"])
    with col2:
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["선택 안함", "매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        st.markdown("<br>", unsafe_allow_html=True)
        restricted_exercises = st.text_input("⚠️ 운동 제한 사항 (쉼표로 구분)", "", key="restricted_exercises",placeholder="예: 허리, 무릎, 발목")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        exercise_preference = st.multiselect("🏃‍♀️ 선호하는 운동 유형", 
                                             ["유산소 운동", "근력 트레이닝", "유연성 운동", "균형 및 코어", "링피트",
                                              "피트니스 댄스", "싸이클링", "수영", "러닝",
                                              "고강도 인터벌 트레이닝", "요가", "필라테스"])
        st.markdown("<br>", unsafe_allow_html=True)
    
    user_data.update({
        "allergen_foods": allergen_foods,
        "preferred_foods": preferred_foods,
        "diet_restriction": diet_restriction,
        "restricted_exercises": restricted_exercises,
        "fitness_level": fitness_level,
        "exercise_preference": exercise_preference
    })
   
    additional_info = [
        ("알레르기 식품", allergen_foods),
        ("선호 식품", preferred_foods),
        ("식이 제한", [diet_restriction]),
        ("운동 제한", restricted_exercises),
        ("체력 수준", [fitness_level]),
        ("선호 운동", exercise_preference)
    ]

# 두 개의 열을 생성하여 버튼을 나란히 배치
    col1, col2 = st.columns(2)

    with col1:
        diet_button = st.button("🥗 식단 계획 추천", key="diet_button")

    with col2:
        exercise_button = st.button("🏋️ 운동 계획 추천", key="workout_button")

    # 선택된 계획을 표시
    if diet_button:
        with st.spinner("AI가 식단을 추천하는 중...⏳"):
            diet_plan = get_gemma_recommendation("식단", user_data, additional_info)
        st.subheader("🥗 맞춤형 식단 계획")
        display_recommendation(diet_plan, "식단")

    elif exercise_button:
        with st.spinner("AI가 운동을 추천하는 중...⏳"):
            exercise_plan = get_gemma_recommendation("운동", user_data, additional_info)
        st.subheader("🏋️ 맞춤형 운동 계획")
        display_recommendation(exercise_plan, "운동")
