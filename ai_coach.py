import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation
import re

def parse_text_to_dict(response_text):
    """📌 응답 텍스트를 JSON 구조의 딕셔너리로 변환"""
    structured_data = {"운동": [], "식단": []}
    current_section = None
    current_day = None

    # 줄 단위로 텍스트 파싱
    for line in response_text.split("\n"):
        line = line.strip()

        # 📌 운동 및 식단 섹션 감지
        if "**운동 추천:**" in line:
            current_section = "운동"
        elif "**식단 추천:**" in line:
            current_section = "식단"

        # 📌 운동 데이터 처리
        elif current_section == "운동" and re.match(r"\* \*\*.*:\*\*", line):
            current_day, content = re.findall(r"\*\*\s?(.*?):\*\*", line)[0], line.split(":")[1].strip()
            structured_data["운동"].append({"요일": current_day, "운동 내용": content})

        # 📌 식단 데이터 처리
        elif current_section == "식단" and re.match(r"\* \*\*.*:\*\*", line):
            meal_type, meal_content = re.findall(r"\*\*\s?(.*?):\*\*", line)[0], line.split(":")[1].strip()
            if len(structured_data["식단"]) == 0 or structured_data["식단"][-1]["요일"] != current_day:
                structured_data["식단"].append({"요일": current_day, meal_type: meal_content})
            else:
                structured_data["식단"][-1][meal_type] = meal_content

    return structured_data




# ✅ AI 건강 코치 페이지
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")

    # ✅ 사용자 데이터 불러오기 및 처리
    user_data = load_user_data()
    user_info = process_user_info(user_data)

    # ✅ 사용자 입력 (알러지 및 제한된 운동)
    goal, excluded_foods, restricted_exercises = get_user_inputs()

    # ✅ 운동 및 식단 추천 버튼 (하나로 통합)
    if st.button("🏋️🥗 운동 및 식단 계획 추천 받기", key="recommend_button"):
        generate_recommendation(user_info, goal, excluded_foods)

# ✅ 사용자 데이터 불러오기
def load_user_data():
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            return json.loads(user_data)
        except json.JSONDecodeError:
            return {}
    return user_data

# ✅ 사용자 건강 정보 처리
def process_user_info(user_data):
    return {
        key: user_data.get(key, "미측정") for key in [
            "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
            "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
        ]
    }

# ✅ 사용자 입력 받기 (목표 + 알러지 및 제한된 운동)
def get_user_inputs():
    st.subheader("⚙️ 개인화 설정")
    
    goal = st.selectbox("🎯 목표 설정", ["체중 감량", "근력 향상", "혈압 관리", "일반 건강 관리"])

    excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "", key="excluded_foods")
    excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]
    restricted_exercises = st.text_input("🏋️ 제한된 운동 입력 (쉼표 구분)", "", key="restricted_exercises")
    restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]

    return goal, excluded_foods, restricted_exercises

# ✅ 운동 및 식단 추천 생성 (하나의 버튼에서 실행)
def generate_recommendation(user_info, goal, excluded_foods):
    with st.spinner("AI가 운동 및 식단 계획을 추천하는 중...⏳"):
        # ✅ 운동 및 식단 추천을 동시에 요청
        exercise_plan = get_gemma_recommendation("운동", user_info)
        diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)
        all_excluded_foods = exercise_plan, diet_plan
        
    st.success("✅ 맞춤형 식단 & 운동 추천이 완료되었습니다!")



    # 스타일이 적용된 테이블로 표시
    st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
        color: #333;
        border-collapse: collapse;
        width: 100%;
    }
    .dataframe th, .dataframe td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .dataframe tr:hover {background-color: #f5f5f5;}
    </style>
    """, unsafe_allow_html=True)
    
    st.table(all_excluded_foods)   


# ✅ 식단 계획 시각화
def display_diet_plan(diet_plan):
    st.success("✅ 맞춤형 식단 추천이 완료되었습니다!")
    st.subheader("🥗 7일 맞춤형 식단 계획")

    if isinstance(diet_plan, list):
        df = pd.DataFrame(diet_plan)
        if not all(col in df.columns for col in ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]):
            st.error("🚨 필요한 열이 응답에 없습니다. (요일, 아침, 점심, 저녁, 총칼로리 (kcal))")
            return

        st.dataframe(df[["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]], use_container_width=True)
    else:
        st.error(f"🚨 잘못된 응답 형식: 리스트 형식이 아닙니다.")


# ✅ 운동 계획 시각화
def display_exercise_plan(exercise_plan):
    st.success("✅ 맞춤형 운동 추천이 완료되었습니다!")
    st.subheader("🏋️ 7일 맞춤형 운동 계획")

    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        if not all(col in df.columns for col in ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]):
            st.error("🚨 필요한 열이 응답에 없습니다. (요일, 운동, 시간(분), 칼로리 소모량(kcal))")
            return

        st.dataframe(df[["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]], use_container_width=True)
    else:
        st.error(f"🚨 잘못된 응답 형식: 리스트 형식이 아닙니다.")

