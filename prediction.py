import streamlit as st
import time
import pandas as pd
import numpy as np
import torch
import os
import uuid
from model_loader import model_exercise, model_food, load_model
from user_input import get_user_input
from user_data_utils import load_user_data, save_user_data

# ✅ 예측 데이터 저장 파일 경로
PREDICTION_FILE = "data/predictions.csv"

# ✅ 모델 로드 (없으면 로드)
if model_exercise is None:
    model_exercise = load_model("models/model_exercise.pth", input_dim=13)
if model_food is None:
    model_food = load_model("models/model_food.pth", input_dim=13)

def preprocess_input(user_data):
    """📌 모델 입력을 위해 데이터를 변환"""
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
        "콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]

    # ✅ 데이터가 없는 경우 기본값 0으로 설정
    processed_data = [user_data.get(key, 0) for key in required_keys]

    # ✅ 성별을 숫자로 변환 (남성 = 1, 여성 = 0)
    processed_data[0] = 1 if user_data.get("성별", "남성") in ["남성", "Male", "M"] else 0
    
    return torch.tensor([processed_data], dtype=torch.float32)
    
# ✅ 예측 함수
def predict(model, input_data):
    """📌 운동 또는 식단 예측 수행"""
    if model is None:
        return "🚨 모델이 로드되지 않았습니다!", 0
    try:
        input_tensor = preprocess_input(input_data)
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output, dim=1)
            prediction_score = int(probabilities[:, 1].item() * 100)
        return prediction_score
    except Exception as e:
        return f"🚨 예측 중 오류 발생: {e}", 0
        
# ✅ 운동 추천 로직
def generate_exercise_recommendation(score):
    if score > 90:
        return "🏆 최고의 운동 습관! 다른 사람들에게 동기부여가 되는 운동 루틴을 공유해보세요."
    elif score > 80:
        return "🥇 훌륭한 운동 습관! 새로운 운동에 도전하여 다양성을 더해보세요."
    elif score > 70:
        return "🥈 좋은 운동 패턴입니다. 운동 강도나 시간을 조금씩 늘려 체력을 향상시켜보세요."
    elif score > 60:
        return "🥉 꾸준히 운동하고 계시네요. 운동의 다양성을 높여 전신 운동 효과를 노려보세요."
    elif score > 50:
        return "⚠️ 운동량을 조금 더 늘려보세요. 일상 속 활동량부터 늘려가는 것이 좋습니다."
    elif score > 40:
        return "⚠️ 운동이 부족합니다. 규칙적인 운동 습관을 만들어보세요. 가벼운 조깅이나 홈트레이닝부터 시작해보는 것은 어떨까요?"
    elif score > 30:
        return "❗ 운동이 많이 부족합니다. 매일 30분 걷기부터 시작해보세요. 작은 변화가 큰 차이를 만듭니다."
    elif score > 20:
        return "❗❗ 운동이 매우 부족합니다. 엘리베이터 대신 계단 이용하기 등 일상 속 작은 운동부터 시작해보세요."
    else:
        return "❗❗❗ 건강에 적신호가 켜졌습니다. 지금 당장 가벼운 스트레칭이라도 시작해보세요. 작은 움직임이 건강의 시작입니다."

# ✅ 식단 추천 로직
def generate_diet_recommendation(score):
    if score > 90:
        return "🏆 완벽한 식단 관리! 현재의 균형 잡힌 식습관을 유지하면서, 다른 사람들과 건강한 레시피를 공유해보세요."
    elif score > 80:
        return "🥇 매우 건강한 식습관입니다. 다양한 슈퍼푸드를 시도해보며 영양의 질을 더욱 높여보세요."
    elif score > 70:
        return "🥈 좋은 식습관을 가지고 계십니다. 계절별 신선한 식재료를 활용해 식단에 변화를 주어보세요."
    elif score > 60:
        return "🥉 괜찮은 식단이에요. 단백질 섭취를 조금 더 늘리고 정제된 탄수화물은 줄여보세요."
    elif score > 50:
        return "⚠️ 식단 개선이 필요합니다. 영양 균형을 위해 다양한 색깔의 과일과 채소를 섭취해보세요."
    elif score > 40:
        return "⚠️ 식습관 개선이 필요합니다. 패스트푸드와 가공식품 섭취를 줄이고 홈쿡을 늘려보세요."
    elif score > 30:
        return "❗ 영양 섭취가 불균형합니다. 매 끼니에 단백질, 탄수화물, 지방, 비타민을 골고루 섭취하도록 노력해보세요."
    elif score > 20:
        return "❗❗ 식단이 매우 불균형합니다. 영양사와 상담을 통해 개인에게 맞는 식단 계획을 세워보는 것은 어떨까요?"
    else:
        return "❗❗❗ 건강에 위험 신호입니다. 전문가의 도움을 받아 식단을 전면 개선해야 합니다. 지금 바로 건강한 한 끼부터 시작해보세요."

def display_prediction_page():
    """📌 예측 페이지 표시"""
    st.header("🔍 운동 및 식단 예측")
    
    if not st.session_state.get("logged_in", False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 로그인/회원가입"):
                st.session_state["show_auth"] = True
                st.rerun()
        with col2:
            if st.button("🚀 게스트로 입장"):
                st.session_state.update({"logged_in": True, "nickname": "게스트", "guest_mode": True})
                st.rerun()
        st.stop()
    
    user_id = st.session_state["nickname"]
    existing_user_data = load_user_data(user_id)
    
    # ✅ 사용자 정보 미리 보기 및 수정 가능
    with st.expander("📋 사용자 정보 미리 보기 및 수정"):
        if existing_user_data:
            st.write(pd.DataFrame([existing_user_data]))

        modify_data = st.button("📝 정보 수정")
        if existing_user_data is None or modify_data:
            user_data = get_user_input(user_id=user_id, default_values=existing_user_data)
            if user_data is None:
                st.warning("사용자 정보를 입력해주세요.")
                return
            save_user_data(user_id, user_data)
            st.success("✅ 사용자 정보가 저장되었습니다!")
            st.rerun()
        else:
            user_data = existing_user_data

    if st.button("🔍 예측 실행") and user_data is not None:
        with st.spinner("⏳ 예측 중..."):
            time.sleep(2)
        
        prob_exercise = predict(model_exercise, user_data)
        prob_food = predict(model_food, user_data)

        st.success("✅ 예측 완료!")
        st.subheader("📋 예측 결과")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🏃 운동 예측")
            st.markdown(f"**운동 확률:** {prob_exercise}%")
        with col2:
            st.markdown("### 🍎 식단 예측")
            st.markdown(f"**식단 개선 필요 확률:** {prob_food}%")

        save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food)

def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    """📌 기존 예측 데이터를 기존 컬럼에 저장"""
    user_data["운동 확률"] = prob_exercise
    user_data["식단 확률"] = prob_food
    user_data["예측 날짜"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    new_data = pd.DataFrame([user_data])

    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data

    df.to_csv(PREDICTION_FILE, index=False)
    st.success("✅ 예측 결과가 저장되었습니다!")
