import streamlit as st
import json
import pandas as pd
from gemma2_recommender import get_gemma_recommendation

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
    
    # 건강 목표 설정
    goals = st.multiselect("🎯 건강 목표 (복수 선택 가능)", 
                           ["체중 감량", "체중 증가", "근력 증진", "유연성 향상", "심혈관 건강 개선", 
                            "스트레스 관리", "수면 개선", "전반적 웰빙 향상", "특정 질병 관리"])
    if "특정 질병 관리" in goals:
        specific_condition = st.text_input("관리하고자 하는 특정 질병이나 건강 상태를 입력해주세요:")
        goals.append(f"특정 질병 관리: {specific_condition}")
    user_data["목표"] = goals
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # 식단 관련 설정
        allergen_foods = st.text_input("🚫 식품 알레르기 및 기피 항목 (쉼표로 구분)", "", key="allergen_foods", placeholder="예: 달걀, 땅콩, 오이")
        allergen_foods = [food.strip() for food in allergen_foods.split(',') if food.strip()]
        
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods", placeholder="예: 달걀, 당근, 면")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        
        diet_restriction = st.selectbox("🍽️ 주요 식이 요법 유형", 
                                        ["선택 안함", "일반식", "채식", "비건", "페스코 베지테리언", "플렉시테리언",
                                         "저탄수화물", "케토제닉", "저지방", "지중해식", "글루텐 프리", "팔레오"])
        
        meal_frequency = st.slider("🕒 하루 식사 횟수", min_value=1, max_value=6, value=3)
        
        cooking_skill = st.select_slider("👨‍🍳 요리 실력", options=["초보", "중급", "고급"])
        
        meal_prep_time = st.slider("⏱️ 식사 준비에 할애할 수 있는 시간 (분)", min_value=10, max_value=120, value=30, step=5)

    with col2:
        # 운동 관련 설정
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        
        restricted_exercises = st.text_input("⚠️ 운동 제한 사항 (쉼표로 구분)", "", key="restricted_exercises", placeholder="예: 허리, 무릎, 발목")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]
        
        exercise_preference = st.multiselect("🏃‍♀️ 선호하는 운동 유형", 
                                             ["유산소 운동", "근력 트레이닝", "유연성 운동", "균형 및 코어", "링피트",
                                              "피트니스 댄스", "싸이클링", "수영", "러닝", "등산",
                                              "고강도 인터벌 트레이닝", "요가", "필라테스", "크로스핏"])
        
        workout_frequency = st.slider("🗓️ 주간 운동 가능 일수", min_value=1, max_value=7, value=3)
        
        workout_duration = st.slider("⏱️ 1회 운동 가능 시간 (분)", min_value=10, max_value=120, value=45, step=5)
        
        workout_location = st.multiselect("🏠 주로 운동하는 장소", ["집", "헬스장", "공원", "수영장", "실외"])
        
    # 추가 정보
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("추가 정보")
    sleep_hours = st.slider("😴 평균 수면 시간", min_value=4, max_value=12, value=7, step=0.5)
    stress_level = st.select_slider("😰 평소 스트레스 수준", options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"])
    water_intake = st.slider("💧 하루 평균 물 섭취량 (리터)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
    
    user_data.update({
        "allergen_foods": allergen_foods,
        "preferred_foods": preferred_foods,
        "diet_restriction": diet_restriction,
        "meal_frequency": meal_frequency,
        "cooking_skill": cooking_skill,
        "meal_prep_time": meal_prep_time,
        "restricted_exercises": restricted_exercises,
        "fitness_level": fitness_level,
        "exercise_preference": exercise_preference,
        "workout_frequency": workout_frequency,
        "workout_duration": workout_duration,
        "workout_location": workout_location,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "water_intake": water_intake
    })
   
    additional_info = [
        ("건강 목표", goals),
        ("알레르기 식품", allergen_foods),
        ("선호 식품", preferred_foods),
        ("식이 제한", [diet_restriction]),
        ("하루 식사 횟수", [meal_frequency]),
        ("요리 실력", [cooking_skill]),
        ("식사 준비 시간", [f"{meal_prep_time}분"]),
        ("운동 제한", restricted_exercises),
        ("체력 수준", [fitness_level]),
        ("선호 운동", exercise_preference),
        ("주간 운동 횟수", [workout_frequency]),
        ("운동 시간", [f"{workout_duration}분"]),
        ("운동 장소", workout_location),
        ("수면 시간", [f"{sleep_hours}시간"]),
        ("스트레스 수준", [stress_level]),
        ("물 섭취량", [f"{water_intake}L"])
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
