import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation
import re

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
def generate_recommendation(user_info, goal, excluded_foods=None):
    with st.spinner("AI가 운동 및 식단 계획을 추천하는 중...⏳"):
        # ✅ 운동 및 식단 추천을 동시에 요청
        exercise_plan = get_gemma_recommendation("운동", user_info)
        diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)

    st.success("✅ 맞춤형 식단 & 운동 추천이 완료되었습니다!")

    # ✅ 운동 계획 표시
    if isinstance(exercise_plan, list):
        df_exercise = pd.DataFrame(exercise_plan)
        st.subheader("🏋️ 7일 맞춤형 운동 계획")
        st.table(df_exercise)
    else:
        st.error("🚨 운동 계획 응답이 예상된 형식이 아닙니다.")

    # ✅ 식단 계획 표시
    if isinstance(diet_plan, list):
        df_diet = pd.DataFrame(diet_plan)
        st.subheader("🥗 7일 맞춤형 식단 계획")
        st.table(df_diet)
    else:
        st.error("🚨 식단 계획 응답이 예상된 형식이 아닙니다.")

# ✅ 사용자 정보를 테이블 형식으로 표시
def parse_ai_response(response_text):
    """AI 응답을 자동 감지하여 JSON 또는 Markdown 테이블로 변환"""
    try:
        # ✅ JSON 형식으로 응답했는지 확인
        response_json = json.loads(response_text)
        if isinstance(response_json, list):
            return response_json  # 바로 반환
    except json.JSONDecodeError:
        pass  # JSON이 아니면 계속 진행

    # ✅ Markdown 테이블 형식 확인
    if "|" in response_text:
        return parse_markdown_table(response_text)

    # ✅ 일반 텍스트 포맷 (요일: 내용) 감지
    return parse_text_based_response(response_text)

def parse_markdown_table(text):
    """Markdown 형식의 표를 DataFrame으로 변환"""
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return None

    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    data = [row.split("|")[1:-1] for row in lines[2:]]
    df = pd.DataFrame(data, columns=headers)
    return df.to_dict(orient="records")

def parse_text_based_response(text):
    """일반 텍스트에서 운동 및 식단 정보를 리스트로 변환"""
    lines = text.split("\n")
    result = []
    for line in lines:
        match = re.match(r"(\w+):\s*(.+)", line)
        if match:
            요일, 내용 = match.groups()
            result.append({"요일": 요일, "내용": 내용})
    return result if result else None


  
