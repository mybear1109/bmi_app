import streamlit as st
import pandas as pd
import torch
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from user_data_utils import load_user_data, save_user_data
from gemma2_recommender import load_gemma_model, get_gemma_recommendation 
from transformers import pipeline # type: ignore # ✅ 올바른 모듈 import

# ✅ 데이터 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
PREDICTION_FILE = os.path.join(BASE_DIR, "data", "predictions.csv")

# ✅ Hugging Face API Key 설정 (secrets.toml에서 가져오기)
HF_API_KEY = os.getenv("HF_API_KEY")  # Streamlit Secrets을 사용할 경우 `st.secrets["HF_API_KEY"]`

# 모델 로드 시도
def load_gemma_model(model_name):
    """모델을 로드하는 함수"""
    try:
        pipe = pipeline(
            "text-generation",
            model=model_name,
            model_kwargs={"torch_dtype": torch.bfloat16, "use_auth_token": HF_API_KEY},  # API Key 인증 추가
            device="mps",  # Mac에서 MPS 사용
        )
        print(f"✅ {model_name} 모델 로드 성공")
        return pipe
    except Exception as e:
        print(f"🚨 {model_name} 모델 로드 실패: {e}")
        return None

# ✅ AI 건강 코치 페이지
def display_ai_coach_page():
    """📌 AI 건강 코치 메인 페이지"""
    st.header("🏋️‍♂️ AI 건강 코치")

    # ✅ 사용자 데이터 불러오기 (기본값: `{}`)
    user_data = st.session_state.get("user_data", {})

    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)  # 문자열을 JSON 형태로 변환
        except json.JSONDecodeError:
            user_data = {}  # 변환 실패 시 기본값 설정

    # ✅ 사용자 ID 가져오기 (기본값: "게스트")
    user_id = user_data.get("user_id", "게스트")

    # ✅ 사용자 건강 정보 변환
    user_info = {
        key: user_data.get(key, "미측정") for key in [
            "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
            "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
        ]
    }

    # ✅ 사용자 입력 (제한 음식 및 운동)
    st.subheader("⚙️ 개인화 설정")

    col1, col2 = st.columns(2)
    with col1:
        excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "", key="excluded_foods")
        excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]  # ✅ 공백 제거
    with col2:
        restricted_exercises = st.text_input("🏋️ 제한해야 할 운동 (쉼표 구분)", "", key="restricted_exercises")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]  # ✅ 공백 제거

    # ✅ 추천 버튼 UI 개선
    col1, col2 = st.columns(2)

    # ✅ 식단 추천 버튼
    with col1:
        if st.button("🥗 식단 계획 추천", key="diet_button"):
            with st.spinner("AI가 식단을 추천하는 중...⏳"):
                diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)

            if diet_plan:
                st.success("✅ 맞춤형 식단 추천이 완료되었습니다!")
                st.subheader("🥗 7일 맞춤형 식단 계획")
                st.dataframe(pd.DataFrame(diet_plan), use_container_width=True)
            else:
                st.error("🚨 식단 추천을 생성하는 데 문제가 발생했습니다.")

    # ✅ 운동 추천 버튼
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동 계획을 추천하는 중...⏳"):
                exercise_plan = get_gemma_recommendation("운동", user_info)

            if exercise_plan:
                st.success("✅ 맞춤형 운동 추천이 완료되었습니다!")
                st.subheader("🏋️ 7일 맞춤형 운동 계획")
                st.dataframe(pd.DataFrame(exercise_plan), use_container_width=True)
            else:
                st.error("🚨 운동 추천을 생성하는 데 문제가 발생했습니다.")

