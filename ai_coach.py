import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation

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
    return {
        key: user_data.get(key, "미측정") for key in [
            "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)",
            "혈압 차이", "총콜레스테롤", "고혈당 위험", "간 지표",
            "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
        ]
    }

# 원시 응답을 깔끔하게 마크다운으로 출력하는 함수
def display_raw_markdown(raw_text):
    st.markdown("---")
    st.markdown("**원시 응답 (마크다운):**")
    # > 로 인용하여 보기 좋게 표시
    st.markdown(f"> {raw_text}")

# 식단 추천 결과를 표 또는 JSON으로 예쁘게 표시하는 함수
def display_diet_plan(diet_plan):
    if isinstance(diet_plan, dict) and "메시지" in diet_plan:
        st.error(f"🚨 식단 추천 생성 중 문제가 발생했습니다.")
        st.markdown("**원시 응답 (JSON):**")
        st.code(json.dumps(diet_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(diet_plan, dict):
        diet_plan = [diet_plan]
    if isinstance(diet_plan, list):
        df = pd.DataFrame(diet_plan)
        expected_cols = ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]
        if all(col in df.columns for col in expected_cols):
            styled_df = (
                df[expected_cols]
                .style
                .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                .background_gradient(cmap='Blues', subset=["총칼로리 (kcal)"])
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]}
                ])
            )
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("예상 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
            st.json(diet_plan)
            display_raw_markdown(diet_plan[0].get("메시지", ""))
    else:
        st.error("🚨 응답 형식 오류: 식단 추천 결과가 리스트 형식이 아닙니다.")

# 운동 추천 결과를 표 또는 JSON으로 예쁘게 표시하는 함수
def display_exercise_plan(exercise_plan):
    if isinstance(exercise_plan, dict) and "메시지" in exercise_plan:
        st.error(f"🚨 운동 추천 생성 중 문제가 발생했습니다.")
        st.markdown("**원시 응답 (JSON):**")
        st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(exercise_plan, dict):
        exercise_plan = [exercise_plan]
    # 만약 응답 데이터에 "weekly_exercise_plan" 키가 있다면 변환
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
        expected_cols = ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]
        if all(col in df.columns for col in expected_cols):
            styled_df = (
                df[expected_cols]
                .style
                .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                .background_gradient(cmap='Oranges', subset=["칼로리 소모량(kcal)"])
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#FF5722'), ('color', 'white')]}
                ])
            )
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("예상 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
            st.json(exercise_plan)
            display_raw_markdown(exercise_plan[0].get("메시지", ""))
    else:
        st.error("🚨 응답 형식 오류: 운동 추천 결과가 리스트 형식이 아닙니다.")

# --- 메인 페이지 표시 함수 ---
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 사용자 데이터 불러오기 및 처리
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
            display_diet_plan(diet_plan)
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동을 추천하는 중...⏳"):
                exercise_plan = get_gemma_recommendation("운동", user_info)
            display_exercise_plan(exercise_plan)
