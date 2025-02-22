import streamlit as st
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import os
from model_loader import model_exercise, model_food  # ✅ 올바르게 import 확인
from user_data_utils import load_user_data, save_user_data


st.markdown(
    """
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .stButton>button {
        color: #4F8BF9;
        border-radius: 50px;
        height: 3em;
        width: 100%;
    }
    .user-info {
        margin-bottom: 15px;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    .health-score {
        font-size: 24px;
        font-weight: bold;
    }
    .recommendation {
        font-size: 16px;
        margin-top: 5px;
        padding: 8px;
        background-color: #f0f8ff;
        border-left: 3px solid #4F8BF9;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ 예측 데이터 저장 경로
PREDICTION_FILE = "data/predictions.csv"

# ✅ 모델을 평가 모드로 설정
model_exercise.eval()
model_food.eval()



def preprocess_input(user_data):
    """📌 입력 데이터 전처리"""
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
        "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]

    processed_data = []
    for key in required_keys:
        value = user_data.get(key, 0)  # 기본값 0

        # ✅ 데이터 변환
        if key == "성별":
            value = 1 if value in ["남성", "Male", "M"] else 0
        elif key == "흡연상태":
            value = 1 if value == "흡연" else 0
        elif key == "음주여부":
            value = 1 if value == "음주" else 0
        else:
            try:
                value = float(value)  # 숫자 변환
            except ValueError:
                value = 0  # 변환 실패 시 기본값 0

        processed_data.append(value)

    return torch.tensor([processed_data], dtype=torch.float32)  # ✅ Tensor 반환


def predict_health_score(model, input_data):
    """📌 모델을 사용하여 운동 또는 식단 점수를 예측"""
    if model is None:
        return 50  # 모델이 없을 경우 기본값 설정

    try:
        input_tensor = preprocess_input(input_data) # ✅ Tensor 변환
        with torch.no_grad():
            output = model(input_tensor)

        # ✅ 출력값을 점수로 변환
        base_score = output.item() * 120
        base_score = max(25, min(100, base_score))  # 25 ~ 100 사이로 보정

        return int(base_score)
    except Exception as e:
        print(f"🚨 예측 중 오류 발생: {e}")
        return 25  # 오류 발생 시 최소 점수 반환
    
def calculate_health_score(user_info):
    """📌 사용자의 건강 정보를 기반으로 종합 점수 계산"""
    score_components = {
        "BMI": 10 if 18.5 <= user_info.get("BMI", 0) <= 24.9 else 6,
        "허리둘레": 8 if user_info.get("허리둘레", 0) <= 85 else 5,
        "혈압": 10 if 90 <= user_info.get("수축기혈압(최고 혈압)", 0) <= 120 and
                     60 <= user_info.get("이완기혈압(최저 혈압)", 0) <= 80 else 7,
        "총 콜레스테롤": 10 if user_info.get("총콜레스테롤", 0) < 200 else 6,
        "고혈당 위험": 8 if user_info.get("고혈당 위험", "낮음") == "낮음" else 5,
        "간 지표": 10 if user_info.get("간 지표", "정상") == "정상" else 7,
        "흡연/음주": 10 if user_info.get("흡연상태", "비흡연") == "비흡연" and 
                        user_info.get("음주여부", "비음주") == "비음주" else 6,
        "연령/성별": 8  # 연령과 성별에 대한 기본 점수
    }

    total_health_score = sum(score_components.values())

    return total_health_score

 
def get_final_health_score(model, user_info):
    """📌 최종 건강 점수 산출"""
    predicted_score = predict_health_score(model, user_info)  # 모델 예측 점수
    health_score = calculate_health_score(user_info)  # 건강 종합 점수

    final_score = int((predicted_score * 1.3) + (health_score * 0.4))  # 가중 평균

    return final_score


# ✅ 추천 로직 함수
def generate_recommendation(final_score, recommendation_type):
    """추천 로직을 생성하는 함수"""
    if recommendation_type == "운동":
        if final_score > 90:
            return "🏆 최고의 운동 습관! 꾸준한 운동이 건강을 지키는 열쇠입니다."
        elif final_score> 80:
            return "🥇 훌륭한 운동 습관을 갖고 계십니다. 운동 강도를 조금씩 높이세요."
        elif final_score> 70:
            return "🥈 좋은 운동 습관입니다! 다양한 운동을 시도하세요."
        elif final_score > 60:
            return "🥉 꾸준한 운동을 하고 계시네요! 유산소와 근력을 균형 있게 배치하면 더 효과적입니다."
        elif final_score> 50:
            return "⚠️ 운동량을 조금 더 늘려보세요. 하루 30분 걷기부터 시작하세요."
        elif final_score > 40:
            return "⚠️ 운동이 부족합니다. 가벼운 스트레칭부터 시작하세요."
        elif final_score > 30:
            return "❗ 운동 개선이 필요합니다. 매일 규칙적인 운동을 계획하세요."
        elif final_score> 20:
            return "❗❗ 운동이 매우 부족합니다. 가벼운 조깅이나 실내 운동을 추천합니다."
        else:
            return "❗❗❗ 건강에 적신호! 하루 10분이라도 몸을 움직이는 습관을 만드세요."
    elif recommendation_type == "식단":
        if final_score > 90:
            return "🏆 완벽한 식단 관리! 균형 잡힌 영양 섭취를 유지하세요."
        elif final_score> 80:
            return "🥇 매우 건강한 식습관을 갖고 계십니다. 단백질과 비타민이 풍부한 식단을 유지하세요!"
        elif final_score> 70:
            return "🥈 좋은 식습관을 유지하고 계십니다. 신선한 채소와 과일을 적극 활용해보세요!"
        elif final_score > 60:
            return "🥉 괜찮은 식단이지만, 가공식품을 줄이고 자연식 위주로 식단을 개선하면 더욱 건강에 도움이 됩니다."
        elif final_score> 50:
            return "⚠️ 식단 개선이 필요합니다. 탄수화물과 단백질의 균형을 맞춰보세요."
        elif final_score > 40:
            return "⚠️ 건강한 식습관을 위해 가공식품 섭취를 줄이고, 신선한 재료로 직접 요리해보세요!"
        elif final_score > 30:
            return "❗ 식단 개선이 필요합니다. 매 끼니에 영양소를 골고루 포함시키세요!"
        elif final_score> 20:
            return "❗❗ 식단이 매우 불균형합니다. 건강을 위해 채소, 단백질, 건강한 지방을 균형 있게 섭취하세요!"
        else:
            return "❗❗❗ 건강에 위험 신호가 감지되었습니다. 전문가와 상담하여 건강한 식단을 계획하세요."
        


def display_prediction_page():
    """📌 예측 페이지 표시"""
    st.header("🔍 AI 기반 운동 및 식단 예측")

    user_id = st.session_state.get("nickname", "게스트")
    user_data = load_user_data(user_id)
    
        
    if user_data:
        st.subheader("📌 사용자 정보")
        
        # 표에 표시할 사용자 정보 목록
        display_columns = ["user_id", "성별", "연령대", "허리둘레", "BMI", "총콜레스테롤", "혈압 차이", "식전혈당(공복혈당)", "간 지표", "비만 위험 지수", "활동 수준"]
        
        # 설명이 필요한 컬럼에 대한 설명을 담은 딕셔너리
        column_descriptions = {
            "user_id": "사용자 ID",
            "성별": "성별 ",
            "연령대": "연령대",
            "허리둘레": "허리둘레 (cm)",
            "BMI": "체질량지수 (kg/m^2)",
            "총콜레스테롤": "총 콜레스테롤 (mg/dL)",
            "혈압 차이": "최고혈압과 최저혈압의 차이 (mmHg)",
            "식전혈당(공복혈당)": "식사 전 혈당 수치 (mg/dL)",
            "간 지표": "간건강 지표",
            "비만 위험 지수": "비만위험 나타내는지수",
            "일상적인 활동 수준": " 저활동, 중간활동, 고활동"
        }

        # 사용자 정보를 DataFrame으로 변환
        user_info_df = pd.DataFrame([{column_descriptions.get(col, col): user_data.get(col, 'N/A') for col in display_columns}])

        # DataFrame을 HTML 테이블로 변환
        html_table = user_info_df.to_html(index=False, classes=['dataframe'], escape=False)

        # CSS 스타일 추가
            # 스타일링을 위한 CSS
        st.markdown("""
            <style>
                .dataframe {
                    border-collapse: separate;
                    border-spacing: 0;
                    width: 100%;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 0.9em;
                    box-shadow: 0 2px 15px rgba(64,64,64,.1);
                    border-radius: 12px;
                    overflow: hidden;
                }
                .dataframe thead tr {
                    background-color: #170B3B;
                    color: #ffffff;
                    text-align: left;
                }
                .dataframe th, .dataframe td {
                    padding: 12px 15px;
                }
                .dataframe th {
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 0.85em;
                    letter-spacing: 0.5px;
                }
                .dataframe tbody tr {
                    transition: background-color 0.3s ease;
                }
                .dataframe tbody tr:hover {
                    background-color: rgba(52, 152, 219, 0.1);
                }
                .dataframe tbody tr:nth-of-type(even) {
                    background-color: #f8f9fa;
                }
                .dataframe tbody td {
                    border-bottom: 1px solid #e9ecef;
                }
                .dataframe tbody tr:last-of-type td {
                    border-bottom: none;
                }
            </style>
            """, unsafe_allow_html=True)


        # HTML 테이블 표시
        st.markdown(html_table, unsafe_allow_html=True)

    if st.button("🔮 AI 예측 실행", help="클릭하여 AI 기반 운동 및 식단 예측을 시작합니다."):
        with st.spinner("⏳ AI가 데이터를 분석 중입니다..."):
            time.sleep(2)

    if user_data:
        prob_exercise = get_final_health_score(model_exercise, user_data)
        prob_food = get_final_health_score(model_food, user_data)

        exercise_recommendation = generate_recommendation(prob_exercise, "운동")
        diet_recommendation = generate_recommendation(prob_food, "식단")

        # 스타일 정의
        st.markdown("""
        <style>
        .health-score-container {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            border-radius: 15px;
            padding: 20px;
            color: white;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .score {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .recommendation {
            background-color: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            font-size: 16px;
            line-height: 1.6;
        }
        .icon {
            font-size: 36px;
            margin-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # 운동 점수 및 추천 표시
        st.markdown(f"""
        <div class="health-score-container">
            <h2><span class="icon">🏋️‍♂️</span> 운동 건강 점수</h2>
            <div class="score">{prob_exercise}</div>
            <div class="recommendation">{exercise_recommendation}</div>
        </div>
        """, unsafe_allow_html=True)

        # 식단 점수 및 추천 표시
        st.markdown(f"""
        <div class="health-score-container">
            <h2><span class="icon">🥗</span> 식단 건강 점수</h2>
            <div class="score">{prob_food}</div>
            <div class="recommendation">{diet_recommendation}</div>
        </div>
        """, unsafe_allow_html=True)

            
            # 예측 결과 저장
        save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food)
    else:
            st.error("사용자 정보가 없어 예측을 실행할 수 없습니다. 먼저 사용자 정보를 입력해주세요.")


def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    """📌 예측 데이터를 기존 컬럼에 저장"""
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
        # 행동 촉구 메시지
    st.success("🎉 분석이 완료되었습니다! 아래 버튼을 클릭하여 상세한 맞춤 계획을 받아보세요.")
    if st.button("📋 맞춤 건강 계획 받기"):
        st.balloons()
        st.info("🚀 축하합니다! 당신만의 맞춤 건강 여정이 시작되었습니다. 함께 건강해져 봐요!")

    else:
        st.error("⚠️ 사용자 정보가 없습니다. 먼저 기본 정보를 입력해주세요.")