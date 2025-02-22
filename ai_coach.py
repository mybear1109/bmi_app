import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation

def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")

    # 사용자 데이터 불러오기
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except json.JSONDecodeError:
            user_data = {}

    user_id = user_data.get("user_id", "게스트")

    # 사용자 건강 정보 변환
    user_info = {
        key: user_data.get(key, "미측정") for key in [
            "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
            "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
        ]
    }

    # 사용자 입력
    st.subheader("⚙️ 개인화 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal = st.selectbox("🎯 목표 설정", ["체중 감량", "근력 향상", "혈압 관리", "일반 건강 관리"])
        user_info["목표"] = goal

        excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "", key="excluded_foods")
        excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]
        
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        
        diet_restriction = st.selectbox("🥗 식단 제한", ["없음", "채식", "육식", "저탄수화물", "저지방", "글루텐 프리"])
    
    with col2:
        restricted_exercises = st.text_input("🏋️ 제한해야 할 운동 (쉼표 구분)", "", key="restricted_exercises")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]
        
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        
        exercise_preference = st.multiselect("🏃‍♀️ 선호하는 운동 유형", 
                                             ["유산소", "근력", "유연성", "균형", "고강도 인터벌", "요가", "필라테스"])

    # 사용자 정보 업데이트
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
            if diet_plan and "메시지" not in diet_plan:
                display_diet_plan(diet_plan)
            else:
                st.error("🚨 식단 추천 생성 중 문제가 발생했습니다.")
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동 계획을 추천하는 중...⏳"):
                exercise_plan = get_gemma_recommendation("운동", user_info)
            if exercise_plan and "메시지" not in exercise_plan:
                display_exercise_plan(exercise_plan)
            else:
                st.error("🚨 운동 추천 생성 중 문제가 발생했습니다.")

def display_diet_plan(diet_plan):
    st.success("✅ 맞춤형 식단 추천이 완료되었습니다!")
    st.subheader("🥗 7일 맞춤형 식단 계획")
    if isinstance(diet_plan, list):
        df = pd.DataFrame(diet_plan)
        required_cols = ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]
        if not all(col in df.columns for col in required_cols):
            st.error("🚨 응답에 필요한 열이 없습니다. (요일, 아침, 점심, 저녁, 총칼로리 (kcal))")
            return
        
        # DataFrame 스타일링 적용
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
        st.error("🚨 응답 형식 오류: 리스트 형식이 아닙니다.")


def display_exercise_plan(exercise_plan):
    st.success("✅ 맞춤형 운동 추천이 완료되었습니다!")
    st.subheader("🏋️ 7일 맞춤형 운동 계획")
    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        required_cols = ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]
        if not all(col in df.columns for col in required_cols):
            st.error("🚨 응답에 필요한 열이 없습니다. (요일, 운동, 시간(분), 칼로리 소모량(kcal))")
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
        st.error("🚨 응답 형식 오류: 리스트 형식이 아닙니다.")

