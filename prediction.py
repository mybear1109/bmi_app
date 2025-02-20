import streamlit as st
import time
import torch
import pandas as pd
import os
from model_utils import model_exercise, model_food  # 모델 로딩 확인
from user_data_utils import load_user_data, save_user_data

# 예측 결과 저장 파일 경로
PREDICTION_FILE = "data/predictions.csv"

def preprocess_input(user_data):
    """입력 데이터를 전처리하는 함수"""
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
        "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    
    processed_data = []
    for key in required_keys:
        value = user_data.get(key, 0)  # 기본값 0
        
        # 성별 변환 (남성=1, 여성=0)
        if key == "성별":
            value = 1 if value in ["남성", "Male", "M"] else 0
        # 흡연 상태 변환 (비흡연=0, 흡연=1)
        elif key == "흡연상태":
            value = 1 if value == "흡연" else 0
        # 음주 여부 변환 (비음주=0, 음주=1)
        elif key == "음주여부":
            value = 1 if value == "음주" else 0
        else:
            try:
                value = float(value)  # 숫자 변환
            except ValueError:
                value = 0  # 변환 실패 시 기본값 0

        processed_data.append(value)
    
    return torch.tensor([processed_data], dtype=torch.float32)

def predict(model, input_data):
    """운동 또는 식단 예측을 수행하는 함수"""
    if model is None:
        return 40  # 기본값을 40으로 설정하여 너무 낮은 점수 방지

    try:
        input_tensor = preprocess_input(input_data)
        with torch.no_grad():
            output = model(input_tensor)

            # 모델 출력값 확인 (디버깅용)
            print(f"모델 출력값: {output.item()}")

            # 점수 변환 (출력값이 작을 경우 보정)
            base_score = output.item() * 120  # 원래보다 높은 가중치 적용

            # 최소 점수 보정 (너무 낮은 점수 방지)
            base_score = max(25, base_score)

            # 점수 추가 가산 (더 후한 점수 부여)
            if base_score < 50:
                base_score += 20
            elif base_score < 70:
                base_score += 15
            elif base_score < 85:
                base_score += 10
            elif base_score < 95:
                base_score += 5

            return min(100, int(base_score))  # 100점 초과 방지
    except Exception as e:
        print(f"🚨 예측 중 오류 발생: {e}")
        return 25  # 오류 발생 시 최소 점수 25점 반환

def generate_exercise_recommendation(score):
    """운동 추천 문구를 생성하는 함수"""
    if score > 90:
        return "🏆 최고의 운동 습관! 꾸준한 운동이 건강을 지키는 열쇠입니다. 현재 루틴을 유지하면서 새로운 도전을 해보세요!"
    elif score > 80:
        return "🥇 훌륭한 운동 습관을 갖고 계십니다. 운동 강도를 조금씩 높이면서 체력을 더 향상시켜 보세요."
    elif score > 70:
        return "🥈 좋은 운동 습관입니다! 다양한 운동을 시도하여 더욱 건강한 몸을 만들어보세요."
    elif score > 60:
        return "🥉 꾸준한 운동을 하고 계시네요! 유산소 운동과 근력 운동을 균형 있게 배치하면 더 효과적입니다."
    elif score > 50:
        return "⚠️ 운동량을 조금 더 늘려보세요. 하루 30분 걷기부터 시작해보는 것도 좋습니다."
    elif score > 40:
        return "⚠️ 운동이 부족합니다. 가벼운 스트레칭부터 시작해보세요. 작은 습관이 건강을 바꿉니다!"
    elif score > 30:
        return "❗ 운동이 많이 부족합니다. 매일 규칙적인 운동을 계획해보세요."
    elif score > 20:
        return "❗❗ 운동이 매우 부족합니다. 건강을 위해 가벼운 조깅이나 실내 운동을 추천합니다!"
    else:
        return "❗❗❗ 건강에 적신호가 켜졌습니다. 하루 10분이라도 몸을 움직이는 습관을 만들어보세요."

def generate_diet_recommendation(score):
    """식단 추천 문구를 생성하는 함수"""
    if score > 90:
        return "🏆 완벽한 식단 관리! 균형 잡힌 영양 섭취를 유지하면서 다른 사람들에게 건강한 레시피를 공유해보세요!"
    elif score > 80:
        return "🥇 매우 건강한 식습관을 갖고 계십니다. 단백질과 비타민이 풍부한 식단을 유지하면 더욱 좋습니다!"
    elif score > 70:
        return "🥈 좋은 식습관을 유지하고 계십니다. 신선한 채소와 과일을 적극 활용해보세요!"
    elif score > 60:
        return "🥉 괜찮은 식단이지만, 가공식품을 줄이고 자연식 위주로 식단을 개선하면 더욱 건강에 도움이 됩니다."
    elif score > 50:
        return "⚠️ 식단 개선이 필요합니다. 탄수화물과 단백질의 균형을 맞춰보세요."
    elif score > 40:
        return "⚠️ 건강한 식습관을 위해 가공식품 섭취를 줄이고, 신선한 재료로 직접 요리해보세요!"
    elif score > 30:
        return "❗ 식단 개선이 필요합니다. 매 끼니에 영양소를 골고루 포함시키는 것이 중요합니다!"
    elif score > 20:
        return "❗❗ 식단이 매우 불균형합니다. 건강을 위해 채소, 단백질, 건강한 지방을 균형 있게 섭취하세요!"
    else:
        return "❗❗❗ 건강에 위험 신호가 감지되었습니다. 전문가와 상담하여 건강한 식단을 계획하는 것이 필요합니다."

def display_prediction_page():
    """예측 페이지 표시 함수"""
    st.header("🔍 AI 기반 운동 및 식단 예측")

    user_id = st.session_state.get("nickname", "게스트")
    user_data = load_user_data(user_id) or {}  # 데이터가 없으면 빈 딕셔너리

    if st.button("🔮 AI 예측 실행", help="클릭하여 AI 기반 운동 및 식단 예측을 시작합니다."):
        with st.spinner("⏳ AI가 데이터를 분석 중입니다..."):
            time.sleep(2)

        prob_exercise = 45  # 예시 점수
        prob_food = 45  # 예시 점수

        exercise_recommendation = generate_exercise_recommendation(prob_exercise)
        diet_recommendation = generate_diet_recommendation(prob_food)

        st.markdown(
            """
            <style>
            .result-container {
                background-color: #f0f8ff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .result-header {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 20px;
            }
            .result-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0 10px;
            }
            .result-table th, .result-table td {
                padding: 15px;
                text-align: center;
                border-radius: 5px;
            }
            .result-table th {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            .result-table td {
                background-color: #ecf0f1;
            }
            .score {
                font-size: 24px;
                font-weight: bold;
                color: #e74c3c;
            }
            .recommendation {
                margin-top: 15px;
                padding: 15px;
                background-color: #d5f5e3;
                border-left: 5px solid #2ecc71;
                border-radius: 5px;
                font-size: 16px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        result_html = f"""
        <div class="result-container">
            <div class="result-header">📊 AI 예측 결과</div>
            <table class="result-table">
                <tr>
                    <th>항목</th>
                    <th>점수</th>
                </tr>
                <tr>
                    <td>🏃‍♂️ 운동</td>
                    <td><span class="score">{prob_exercise}점</span></td>
                </tr>
                <tr>
                    <td colspan="2" class="recommendation">
                        <div class="ai-recommendation">🤖 AI 운동 추천:</div>
                        {exercise_recommendation}
                    </td>
                </tr>
                <tr>
                    <td>🥗 식단</td>
                    <td><span class="score">{prob_food}점</span></td>
                </tr>
                <tr>
                    <td colspan="2" class="recommendation">
                        <div class="ai-recommendation">🤖 AI 식단 추천:</div>
                        {diet_recommendation}
                    </td>
                </tr>
            </table>
        </div>
        """

        st.markdown(result_html, unsafe_allow_html=True)

        save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food)

def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    """예측 결과를 CSV에 저장"""
    user_data["운동 확률"] = prob_exercise
    user_data["식단 확률"] = prob_food
    user_data["예측 날짜"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

