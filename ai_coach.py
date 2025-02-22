import json
import streamlit as st
import pandas as pd
import re
from gemma2_recommender import get_gemma_recommendation


def parse_text_to_dict(response_text):
    """📌 AI 응답 텍스트를 JSON 구조의 딕셔너리로 변환"""
    structured_data = {"운동": [], "식단": []}
    current_section = None

    # 텍스트 라인별로 분할하여 처리
    for line in response_text.split("\n"):
        line = line.strip()

        # 📌 운동 및 식단 섹션 감지
        if "운동 계획 추천" in line:
            current_section = "운동"
        elif "식단 계획 추천" in line:
            current_section = "식단"

        # 📌 운동 데이터 처리 (요일 | 운동 | 시간 | 칼로리)
        elif current_section == "운동" and "|" in line and "요일" not in line:
            parts = line.split("|")
            if len(parts) >= 4:
                structured_data["운동"].append({
                    "요일": parts[1].strip(),
                    "운동 종류": parts[2].strip(),
                    "시간 (분)": parts[3].strip(),
                    "칼로리 소모": parts[4].strip() if len(parts) > 4 else "N/A"
                })

        # 📌 식단 데이터 처리 (요일 | 아침 | 점심 | 저녁 | 간식 | 총 칼로리)
        elif current_section == "식단" and "|" in line and "요일" not in line:
            parts = line.split("|")
            if len(parts) >= 5:
                structured_data["식단"].append({
                    "요일": parts[1].strip(),
                    "아침": parts[2].strip(),
                    "점심": parts[3].strip(),
                    "저녁": parts[4].strip(),
                    "간식": parts[5].strip() if len(parts) > 5 else "N/A",
                    "총 칼로리": parts[6].strip() if len(parts) > 6 else "N/A"
                })

    return structured_data


# ✅ AI 건강 코치 페이지
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")

    # ✅ 사용자 데이터 불러오기 및 처리
    user_data = load_user_data()
    user_info = process_user_info(user_data)

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
# ✅ 운동과 식단을 구분하여 표시하는 함수
def display_separate_recommendations(response):
    """운동 및 식단을 구분하여 출력"""
    if isinstance(response, dict) and "운동" in response and "식단" in response:
        exercise_plan = response["운동"]
        diet_plan = response["식단"]

        # ✅ 운동 계획 출력
        st.subheader("🏋️ 7일 맞춤형 운동 계획")
        if isinstance(exercise_plan, list) and exercise_plan:
            df_exercise = pd.DataFrame(exercise_plan)
            st.dataframe(df_exercise, use_container_width=True)
        else:
            st.warning("🚨 운동 계획을 불러오는 데 실패했습니다.")

        # ✅ 식단 계획 출력
        st.subheader("🥗 7일 맞춤형 식단 계획")
        if isinstance(diet_plan, list) and diet_plan:
            df_diet = pd.DataFrame(diet_plan)
            st.dataframe(df_diet, use_container_width=True)
        else:
            st.warning("🚨 식단 계획을 불러오는 데 실패했습니다.")
    else:
        st.error("🚨 예상치 못한 응답 형식입니다.")

# ✅ 사용자 입력 받기
st.subheader("⚙️ 개인화 설정")
goal = st.selectbox("🎯 목표 설정", ["체중 감량", "근력 향상", "혈압 관리", "일반 건강 관리"])
excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)").split(',')


# ✅ 운동 및 식단 추천 생성 (하나의 버튼에서 실행)
def generate_recommendation(user_info, goal, excluded_foods):
    with st.spinner("AI가 운동 및 식단 계획을 추천하는 중...⏳"):
        # ✅ 운동 및 식단 추천을 동시에 요청
        exercise_plan = get_gemma_recommendation("운동", user_info)
        diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)

        # ✅ AI 응답이 문자열일 경우 변환
        if isinstance(exercise_plan, str):
            exercise_plan = parse_text_to_dict(exercise_plan)["운동"]
        if isinstance(diet_plan, str):
            diet_plan = parse_text_to_dict(diet_plan)["식단"]

        st.success("✅ 맞춤형 식단 & 운동 추천이 완료되었습니다!")
        st.table(exercise_plan)
       


