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
    goal = st.selectbox("🎯 목표 설정", ["체중 감량", "근력 향상", "혈압 관리", "일반 건강 관리"])
    goal = [goal.strip() for goal in goal.split(',') if goal.strip()]
    user_info["목표"] = goal

    col1, col2 = st.columns(2)

    with col1:
        excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "", key="excluded_foods")
        excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]
    with col2:
        restricted_exercises = st.text_input("🏋️ 제한해야 할 운동 (쉼표 구분)", "", key="restricted_exercises")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]

    # 추천 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 식단 계획 추천", key="diet_button"):
            with st.spinner("AI가 식단을 추천하는 중...⏳"):
                diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)
            if diet_plan and "메시지" not in diet_plan:
                display_diet_plan(diet_plan)
            else:
                st.error(f"🚨 식단 추천을 생성하는 데 문제가 발생했습니다: {diet_plan.get('알 수 없는 오류')}")
                st.table(diet_plan)
                

    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동 계획을 추천하는 중...⏳"):
                exercise_plan = get_gemma_recommendation("운동", user_info)
            if exercise_plan and "메시지" not in exercise_plan:
                display_exercise_plan(exercise_plan)
            else:
                st.error(f"🚨 운동 추천을 생성하는 데 문제가 발생했습니다: {exercise_plan.get('메시지', '알 수 없는 오류')}")
                st.table(exercise_plan)
                
def display_diet_plan(diet_plan):
    st.success("✅ 맞춤형 식단 추천이 완료되었습니다!")
    st.subheader("🥗 7일 맞춤형 식단 계획")


    if isinstance(diet_plan, list):
        df = pd.DataFrame(diet_plan)
        if not all(col in df.columns for col in ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]):
            st.error("🚨 필요한 열이 응답에 없습니다. (요일, 아침, 점심, 저녁, 총칼로리 (kcal))")
            return
        
        # 스타일링을 적용한 DataFrame을 표시합니다.
        st.dataframe(
            df[["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]].style.set_properties(**{'text-align': 'center'}),
            column_config={
                "요일": st.column_config.TextColumn("요일", width="small"),
                "아침": st.column_config.TextColumn("아침", width="medium"),
                "점심": st.column_config.TextColumn("점심", width="medium"),
                "저녁": st.column_config.TextColumn("저녁", width="medium"),
                "총칼로리 (kcal)": st.column_config.NumberColumn("총칼로리 (kcal)", width="small", format="%d"),
            },
            height=350,
            use_container_width=True
        )

    else:
        st.error(f"🚨 잘못된 응답 형식: 리스트 형식이 아닙니다. (Diet_plan)")

def display_exercise_plan(exercise_plan):
    st.success("✅ 맞춤형 운동 추천이 완료되었습니다!")
    st.subheader("🏋️ 7일 맞춤형 운동 계획")


    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        if not all(col in df.columns for col in ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]):
            st.error("🚨 필요한 열이 응답에 없습니다. (요일, 운동, 시간(분), 칼로리 소모량(kcal))")
            return

        # 스타일링을 적용한 DataFrame을 표시합니다.
        st.dataframe(
            df[["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]].style.set_properties(**{'text-align': 'center'}),
            column_config={
                "요일": st.column_config.TextColumn("요일", width="small"),
                "운동": st.column_config.TextColumn("운동", width="medium"),
                "시간(분)": st.column_config.NumberColumn("시간 (분)", width="small", format="%d"),
                "칼로리 소모량(kcal)": st.column_config.NumberColumn("칼로리 소모량 (kcal)", width="small", format="%d"),
            },
            height=350,
            use_container_width=True
        )
    else:
        st.error(f"🚨 잘못된 응답 형식: 리스트 형식이 아닙니다. (exercise_plan)")
