import streamlit as st
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import os
import json
from model_loader import model_exercise, model_food  # 모델 로더에서 모델 불러오기
from user_data_utils import load_user_data, save_user_data


# 예측 결과 저장 경로
PREDICTION_FILE = "data/predictions.csv"

# 모델을 평가 모드로 설정

model_exercise.eval()
model_food.eval()

def preprocess_input(user_data):
    """
    입력 데이터 전처리:
    필수 키 값들을 숫자형 데이터로 변환하여 Tensor로 반환합니다.
    """
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)",
        "혈압 차이", "총콜레스테롤", "고혈당 위험", "간 지표",
        "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    processed_data = []
    for key in required_keys:
        value = user_data.get(key, 0)
        if key == "성별":
            value = 1 if value in ["남성", "Male", "M"] else 0
        elif key == "흡연상태":
            value = 1 if value == "흡연" else 0
        elif key == "음주여부":
            value = 1 if value == "음주" else 0
        else:
            try:
                value = float(value)
            except ValueError:
                value = 0
        processed_data.append(value)
    return torch.tensor([processed_data], dtype=torch.float32)

def predict_health_score(model, input_data):
    """
    모델을 사용하여 예측 점수를 산출합니다.
    만약 모델 출력이 스칼라인 경우 그대로 사용하고, 여러 요소가 있으면 평균값을 사용합니다.
    """
    if model is None:
        return 50  # 모델이 없으면 기본 점수 50
    try:
        input_tensor = preprocess_input(input_data)
        with torch.no_grad():
            output = model(input_tensor)
        # 출력값이 다수의 요소이면 평균값을 취함
        if output.numel() > 1:
            base_value = output.mean().item()
        else:
            base_value = output.item()
        # 모델 출력값에 60을 곱하여 0~100 사이의 점수로 보정
        base_score = base_value
        base_score = max(25, min(100, base_score))
        return int(base_score)
    except Exception as e:
        st.error(f"🚨 예측 중 오류 발생: {e}")
        return 25

def calculate_health_score(user_info):
    """
    건강 정보 기반 점수 계산:
    - 예를 들어, BMI가 18.5~23이면 10점, 그렇지 않으면 6점 등 정상 범위일 경우 높은 점수를 부여합니다.
    """
    score_components = {
        "BMI": 10 if 18.5 <= user_info.get("BMI", 0) <= 23 else 6,
        "허리둘레": 8 if user_info.get("허리둘레", 0) <= 85 else 5,
        "혈압": 10 if 90 <= user_info.get("수축기혈압(최고 혈압)", 0) <= 120 and 60 <= user_info.get("이완기혈압(최저 혈압)", 0) <= 80 else 7,
        "총 콜레스테롤": 10 if user_info.get("총콜레스테롤", 0) < 200 else 6,
        "고혈당 위험": 8 if user_info.get("고혈당 위험", "낮음") == "낮음" else 5,
        "간 지표": 10 if user_info.get("간 지표", "정상") == "정상" else 7,
        "흡연/음주": 10 if user_info.get("흡연상태", "비흡연") == "비흡연" and user_info.get("음주여부", "비음주") == "비음주" else 6,
        "연령/성별": 8
    }
    return sum(score_components.values())

def get_final_health_score(model, user_info, rec_type):
    """
    최종 건강 점수를 산출합니다.
    rec_type에 따라 모델 예측 점수와 건강 정보 점수의 가중치를 다르게 적용합니다.
      - 운동: 모델 예측 30%, 건강 정보 70%
      - 식단: 모델 예측 20%, 건강 정보 80%
    또한, calibration_factor(보정 계수)를 적용하여 모델 예측 점수를 보정합니다.
    """
    predicted = predict_health_score(model, user_info)
    health = calculate_health_score(user_info)
    # 보정 계수: 필요 시 조정 (예: 모델의 기본 치수와 실제 사용자 차이를 보정)
    calibration_factor = 1.0
    calibrated_predicted = predicted * calibration_factor
    
    if rec_type == "운동":
        final = int((calibrated_predicted * 0.3) + (health * 0.7))
    elif rec_type == "식단":
        final = int((calibrated_predicted * 0.2) + (health * 0.8))
    else:
        final = int((calibrated_predicted * 0.3) + (health * 0.7))
    return final

def generate_recommendation(final_score, recommendation_type):
    """추천 메시지 생성 함수"""
    if recommendation_type == "운동":
        if final_score > 90:
            return "🏆 최고의 운동 습관! 꾸준한 운동이 건강을 지키는 열쇠입니다."
        elif final_score > 80:
            return "🥇 훌륭한 운동 습관입니다. 조금 더 강도 있는 운동을 고려해 보세요."
        elif final_score > 70:
            return "🥈 좋은 운동 습관입니다! 다양한 운동을 시도해 보세요."
        elif final_score > 60:
            return "🥉 꾸준한 운동을 하고 계시네요! 유산소와 근력 운동을 균형 있게 조합해 보세요."
        elif final_score > 50:
            return "⚠️ 운동량을 늘려보세요. 하루 30분 정도의 걷기부터 시작해 보세요."
        elif final_score > 40:
            return "⚠️ 운동 부족입니다. 가벼운 스트레칭부터 시작하세요."
        elif final_score > 30:
            return "❗ 규칙적인 운동 계획이 필요합니다. 매일 조금씩 시작해 보세요."
        elif final_score > 20:
            return "❗❗ 운동이 매우 부족합니다. 가능한 한 매일 몸을 움직이세요."
        else:
            return "❗❗❗ 건강에 적신호입니다! 즉시 전문가와 상담하세요."
    elif recommendation_type == "식단":
        if final_score > 90:
            return "🏆 완벽한 식단 관리! 균형 잡힌 영양 섭취를 유지하세요."
        elif final_score > 80:
            return "🥇 매우 건강한 식습관입니다. 식단을 계속 유지하세요!"
        elif final_score > 70:
            return "🥈 좋은 식습관입니다. 신선한 채소와 과일을 더 늘려 보세요."
        elif final_score > 60:
            return "🥉 괜찮은 식단입니다. 가공식품을 줄이고 자연식 위주로 개선해 보세요."
        elif final_score > 50:
            return "⚠️ 식단 개선이 필요합니다. 탄수화물과 단백질의 균형을 맞춰 보세요."
        elif final_score > 40:
            return "⚠️ 건강한 식습관을 위해 더 많은 신선한 재료를 섭취해 보세요."
        elif final_score > 30:
            return "❗ 식단 개선이 필요합니다. 매 끼니에 영양소를 골고루 포함시키세요!"
        elif final_score > 20:
            return "❗❗ 식단이 매우 불균형합니다. 전문가의 상담이 필요합니다."
        else:
            return "❗❗❗ 건강에 위험 신호가 감지됩니다. 즉시 전문가와 상담하세요."
    else:
        return "🚨 알 수 없는 추천 유형입니다."

def display_prediction_page():
    st.header("🔍 AI 기반 운동 및 식단 예측")
    user_id = st.session_state.get("nickname", "게스트")
    user_data = load_user_data(user_id)
    
    if user_data:
        st.subheader("📌 사용자 정보")
        display_columns = [
            "user_id", "성별", "연령대", "허리둘레", "BMI", "총콜레스테롤",
            "혈압 차이", "식전혈당(공복혈당)", "간 지표", "비만 위험 지수", "활동 수준"
        ]
        column_descriptions = {
            "user_id": "사용자 ID",
            "성별": "성별",
            "연령대": "연령대",
            "허리둘레": "허리둘레 (cm)",
            "BMI": "체질량지수 (kg/m^2)",
            "총콜레스테롤": "총 콜레스테롤 (mg/dL)",
            "혈압 차이": "혈압 차이 (mmHg)",
            "식전혈당(공복혈당)": "식전혈당 (mg/dL)",
            "간 지표": "간 건강 지표",
            "비만 위험 지수": "비만 위험 지수",
            "활동 수준": "활동 수준"
        }
        user_info_df = pd.DataFrame([{column_descriptions.get(col, col): user_data.get(col, 'N/A') for col in display_columns}])
        
    else:
        st.error("사용자 정보가 없어 예측을 실행할 수 없습니다. 먼저 사용자 정보를 입력해주세요.")
    
    if st.button("🔮 AI 예측 실행", help="클릭하여 AI 기반 운동 및 식단 예측을 시작합니다."):
        with st.spinner("⏳ AI가 데이터를 분석 중입니다..."):
            time.sleep(2)
    
    if user_data:
        prob_exercise = get_final_health_score(model_exercise, user_data, "운동")
        prob_food = get_final_health_score(model_food, user_data, "식단")
        
        exercise_recommendation = generate_recommendation(prob_exercise, "운동")
        diet_recommendation = generate_recommendation(prob_food, "식단")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6e8efb, #a777e3); border-radius: 15px; padding: 20px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 30px;">
            <h2 style="text-align: center;"><span style="font-size: 36px;">🏋️‍♂️</span> 운동 건강 점수</h2>
            <div style="font-size: 48px; font-weight: bold; text-align: center;">{prob_exercise}</div>
            <div style="background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin-top: 15px; font-size: 18px; text-align: center;">{exercise_recommendation}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6e8efb, #a777e3); border-radius: 15px; padding: 20px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 30px;">
            <h2 style="text-align: center;"><span style="font-size: 36px;">🥗</span> 식단 건강 점수</h2>
            <div style="font-size: 48px; font-weight: bold; text-align: center;">{prob_food}</div>
            <div style="background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin-top: 15px; font-size: 18px; text-align: center;">{diet_recommendation}</div>
        </div>
        """, unsafe_allow_html=True)
        
        save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food)
    else:
        st.error("사용자 정보가 없어 예측을 실행할 수 없습니다. 먼저 사용자 정보를 입력해주세요.")

def calculate_age_group(age):
    """
    나이를 10년 단위의 연령대로 변환하는 함수입니다.
    """
    try:
        age = int(age)
    except ValueError:
        return "알 수 없음"
    if age < 10:
        return "0-9세"
    elif age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    elif age < 70:
        return "60대"
    else:
        return "70대 이상"        

def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    """
    예측 결과를 CSV 파일에 저장합니다.
    """
    user_data["운동 점수"] = prob_exercise
    user_data["식단 점수"] = prob_food
    user_data["연령대"] = calculate_age_group(user_data.get("나이", 0))
    user_data["예측 날짜"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([user_data])
    PREDICTION_FILE = "data/predictions.csv"
    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(PREDICTION_FILE, index=False)
    st.success("🎉 분석이 완료되었습니다! 아래 버튼을 클릭하여 상세한 맞춤 계획을 받아보세요.")
    if st.button("📋 맞춤 건강 계획 받기"):
        st.balloons()
        st.info("🚀 축하합니다! 당신만의 맞춤 건강 여정이 시작되었습니다. 함께 건강해져 봐요!")
    else:
        st.error("⚠️ 사용자 정보가 없습니다. 먼저 기본 정보를 입력해주세요.")
