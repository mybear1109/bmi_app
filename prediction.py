import streamlit as st
import time
import pandas as pd
import numpy as np
import torch
import os
import uuid
from user_input import get_user_input
from model_loader import model_exercise, model_food
from login import login

# ✅ 예측 데이터 저장 파일 경로
PREDICTION_FILE = "data/predictions.csv"


def load_user_data(user_id):
    """📌 기존 유저 데이터를 불러오는 함수"""
    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        user_data = df[df['user_id'] == user_id]
        if not user_data.empty:
            return user_data.iloc[-1].to_dict()  # 가장 최근 데이터 반환
    return None

# ✅ 데이터 전처리 함수
def preprocess_input(user_data):
    """📌 모델 입력을 위해 데이터를 변환"""
    user_data["성별 코드"] = 1 if user_data.get("성별", "남성") in ["남성", "Male", "M"] else 0

    required_keys = [
        "성별 코드", "연령대코드(5세단위)", "허리둘레 (cm)", 
        "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", 
        "콜레스테롤 지수", "BMI"
    ]
    
    missing_keys = [key for key in required_keys if key not in user_data or pd.isna(user_data[key])]
    if missing_keys:
        raise ValueError(f"🚨 입력 데이터에 필요한 키가 없습니다: {missing_keys}")

    try:
        input_array = np.array([[user_data.get(key, 0) for key in required_keys]], dtype=np.float32)
        input_tensor = torch.tensor(input_array)
        return input_tensor
    except Exception as e:
        raise ValueError(f"🚨 데이터 변환 중 오류 발생: {e}")

# ✅ 예측 함수
def predict(model, input_data):
    """📌 운동 또는 식단 예측 수행"""
    if model is None:
        return "🚨 모델이 로드되지 않았습니다!", 0

    try:
        input_tensor = preprocess_input(input_data)
        with torch.no_grad():
            output = model(input_tensor)
            if output is None or not isinstance(output, torch.Tensor):
                raise ValueError("🚨 모델 출력이 유효하지 않습니다.")

            probabilities = torch.nn.functional.softmax(output, dim=1)
            prediction_prob = probabilities[:, 1].item()  # 예측 확률
            prediction_score = int(prediction_prob * 100)

        if model == model_exercise:
            return generate_exercise_recommendation(prediction_score), prediction_score
        else:
            return generate_diet_recommendation(prediction_score), prediction_score

    except Exception as e:
        return f"🚨 예측 중 오류 발생: {str(e)}", 0

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
            if st.button("🔐 로그인/회원가입", key="login_btn"):
                login()
                st.rerun()
        with col2:
            if st.button("🚀 게스트로 입장", key="guest_btn"):
                st.session_state["logged_in"] = True
                st.session_state["nickname"] = f"게스트_{uuid.uuid4().hex[:8]}"
                st.session_state["guest_mode"] = True
                st.rerun()
        st.stop()

    user_id = st.session_state["nickname"]

    # ✅ 기존 사용자 데이터 로드
    existing_user_data = load_user_data(user_id)

    if existing_user_data:
        st.subheader("📋 기존 입력 정보")
        st.write(f"**성별:** {existing_user_data.get('성별', '미입력')}")
        st.write(f"**나이:** {existing_user_data.get('나이', '미입력')}")
        st.write(f"**키:** {existing_user_data.get('키 (cm)', '미입력')} cm")
        st.write(f"**체중:** {existing_user_data.get('현재 체중 (kg)', '미입력')} kg")

        if st.button("📝 기존 정보 수정"):
            updated_data = get_user_input(default_values=existing_user_data)  # ✅ 기존 데이터 기반 수정 가능
            save_user_data(user_id, updated_data)  # ✅ 수정된 데이터를 저장
            st.success("✅ 사용자 정보가 업데이트되었습니다. 다시 로그인하면 변경된 정보가 반영됩니다.")
            st.rerun()
        else:
            user_data = existing_user_data  # ✅ 기존 데이터 그대로 사용
    else:
        user_data = get_user_input()  # ✅ 새 사용자 데이터 입력 요청

    # ✅ 예측 실행 버튼
    if st.button("🔍 예측 실행"):
        with st.spinner("⏳ 예측 중..."):
            time.sleep(2)
            
        prediction_exercise, prob_exercise = predict(model_exercise, user_data)
        prediction_food, prob_food = predict(model_food, user_data)

        st.success("✅ 예측 완료!")
        st.subheader("📋 예측 결과")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 운동 예측")
            st.markdown(f"**점수:** {int(prob_exercise)}")
            st.markdown(f"**추천:** {prediction_exercise}")
        with col2:
            st.markdown("### 식단 예측")
            st.markdown(f"**점수:** {int(prob_food)}")
            st.markdown(f"**추천:** {prediction_food}")

        st.markdown("📊 **예측 데이터를 바탕으로 데이터 시각화 및 운동 및 식단 추천이 가능합니다!**")

        save_prediction_for_visualization(user_id, user_data, prediction_exercise, prob_exercise, prediction_food, prob_food)


def save_user_data(user_id, user_data):
    """📌 사용자의 정보를 저장 (기존 데이터 업데이트)"""
    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)

        # ✅ 기존 데이터가 있는 경우 업데이트
        if user_id in df["user_id"].values:
            df.loc[df["user_id"] == user_id, list(user_data.keys())] = user_data.values()
        else:
            new_data = pd.DataFrame([user_data])
            df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = pd.DataFrame([user_data])

    df.to_csv(PREDICTION_FILE, index=False)
    st.success("✅ 사용자 정보가 저장되었습니다.")
def save_prediction_for_visualization(user_id, user_data, prediction_exercise, prob_exercise, prediction_food, prob_food):
    """📌 기존 예측과 비교할 데이터를 저장"""
    new_data = pd.DataFrame([{
        "user_id": user_id,
        "이름": user_data.get("이름", "미입력"),
        "성별": user_data.get("성별", "미입력"),
        "운동 가능성": prediction_exercise if prediction_exercise else "N/A",
        "운동 확률": prob_exercise if prob_exercise else 0.0,
        "식단 개선 필요성": prediction_food if prediction_food else "N/A",
        "식단 확률": prob_food if prob_food else 0.0,
        "나이": user_data.get("나이", "N/A"),
        "현재 체중 (kg)": user_data.get("현재 체중 (kg)", "N/A"),
        "목표 체중 (kg)": user_data.get("목표 체중 (kg)", "N/A"),
        "연령대코드(5세단위)": user_data.get("연령대코드(5세단위)", "N/A"),
        "예측 날짜": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data

    df.to_csv(PREDICTION_FILE, index=False)
    st.success("✅ 예측 결과가 저장되었습니다!")
