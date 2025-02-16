import streamlit as st
import numpy as np
import torch
import pandas as pd
import uuid
import login
import json
import math

# 사용자 데이터 파일 경로 정의
USER_DATA_FILE = "user_data.json"

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_safe_int(value, default):
    """📌 NaN 및 리스트 타입 처리 후 int 변환"""
    if isinstance(value, list):  # 리스트인 경우 첫 번째 값 사용
        value = value[0]
    if value is None or (isinstance(value, float) and math.isnan(value)):  # NaN 처리
        return default
    return int(value)

def get_user_input(default_values=None):
    """📌 사용자 입력을 받아 모델 입력 형식으로 변환하는 함수"""
    
    # ✅ 스타일 적용
    st.markdown("""
    <style>
        .input-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .preview-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 20px;
        }
        .title-container {
            text-align: center;
            color: #1f618d;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .stTextInput, .stSelectbox, .stNumberInput {
            margin-bottom: 15px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ✅ 제목
    st.markdown("<div class='title-container'>📋 사용자 건강 정보 입력</div>", unsafe_allow_html=True)

    # ✅ 입력 필드
    col1, col2 = st.columns(2)

    with col1:
        gender = st.radio("🧑 성별", ["남성", "여성"], index=0 if default_values and default_values.get("성별") == "남성" else 1)

        # 🔥 나이 입력 슬라이더 (NaN 방지)
        age = st.slider("🕒 나이", min_value=10, max_value=100, value=get_safe_int(default_values.get("나이", 25), 25), step=1)

        height = st.number_input("📏 키 (cm)", min_value=100, max_value=250, value=get_safe_int(default_values.get("키 (cm)", 170), 170))
        weight = st.number_input("⚖ 현재 체중 (kg)", min_value=30, max_value=200, value=get_safe_int(default_values.get("현재 체중 (kg)", 70), 70))
        goal_weight = st.number_input("🎯 목표 체중 (kg)", min_value=30, max_value=200, value=get_safe_int(default_values.get("목표 체중 (kg)", 65), 65))

    with col2:
        waist = st.slider("📏 허리둘레 (cm)", min_value=50, max_value=150, value=get_safe_int(default_values.get("허리둘레 (cm)", 80), 80), step=1)

        systolic_bp = st.number_input("🩸 수축기혈압(최고 혈압)", min_value=80, max_value=200, value=get_safe_int(default_values.get("수축기혈압(최고 혈압)", 120), 120))
        diastolic_bp = st.number_input("🩸 이완기혈압(최저 혈압)", min_value=40, max_value=130, value=get_safe_int(default_values.get("이완기혈압(최저 혈압)", 80), 80))
        cholesterol = st.number_input("🥩 콜레스테롤 지수", min_value=100, max_value=300, value=get_safe_int(default_values.get("콜레스테롤 지수", 180), 180))

        activity_level = st.selectbox(
            "💪 활동 수준", 
            ["저활동", "중간활동", "고활동"], 
            index=["저활동", "중간활동", "고활동"].index(default_values.get("활동 수준", "중간활동")) if default_values else 1
        )


    # ✅ 활동 수준 코드 매핑
    activity_mapping = {"저활동": 0, "중간활동": 1, "고활동": 2}
    activity_level_code = activity_mapping[activity_level]

    # ✅ BMI 자동 계산
    bmi = round(weight / ((height / 100) ** 2), 2) if height > 0 else 0.0

    # ✅ 유니크 ID 생성
    unique_id = st.session_state.get("username", f"user_{uuid.uuid4().hex[:8]}")

    # ✅ 사용자 데이터 저장
    user_data = {
        "ID": unique_id,
        "성별": gender,
        "나이": age,
        "연령대코드(5세단위)": age // 5 * 5,
        "키 (cm)": height,
        "현재 체중 (kg)": weight,
        "목표 체중 (kg)": goal_weight,
        "허리둘레 (cm)": waist,
        "수축기혈압(최고 혈압)": systolic_bp,
        "이완기혈압(최저 혈압)": diastolic_bp,
        "콜레스테롤 지수": cholesterol,
        "활동 수준": activity_level,
        "활동수준코드": activity_level_code,
        "BMI": bmi
    }

    # ✅ 스타일 적용 (CSS)
    st.markdown("""
        <style>
            div[data-testid="stDataFrame"] {
                width: 100% !important;
            }
            table {
                width: 100% !important;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px !important;
                font-size: 16px !important;
                text-align: center !important;
                border: 1px solid #ddd !important;
            }
            th {
                background-color: #f2f2f2 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ✅ 제목 추가 (위치 조정)
    st.markdown("<h4 style='text-align: center; color: #1f618d;'>🔍 입력한 데이터 미리보기</h4>", unsafe_allow_html=True)

    # ✅ 설명 문구 위치 조정 (제목 아래)
    st.markdown("<div style='text-align: right; color: #666; font-size: 16px;'>💡 입력하신 데이터를 확인해주세요.</div>", unsafe_allow_html=True)


    # ✅ 선택 가능한 데이터 목록
    all_columns = list(user_data.keys())

    # ✅ 사용자가 원하는 데이터 선택 (멀티셀렉트)
    selected_columns = ["ID" , "성별", "나이", "키 (cm)", "현재 체중 (kg)",'허리둘레 (cm)',"BMI"]
                                   

    # ✅ 선택한 데이터만 DataFrame으로 변환
    df_selected = pd.DataFrame([{col: user_data[col] for col in selected_columns}])

    # ✅ ID 컬럼 숨김
    df_user = pd.DataFrame([user_data])
    df_user.drop(columns=["ID"], inplace=True, errors="ignore")  # ID 숨기기

    # ✅ 선택한 데이터만 표시 (전체 화면 너비 사용)
    st.dataframe(df_selected, use_container_width=True)  # 📌 전체 화면 너비로 확장하여 표시


    return user_data


def preprocess_input(user_data):
    """💡 모델 입력을 위해 데이터를 변환하는 함수"""
    required_keys = [
        "ID", "키 (cm)", "체중 (kg)", "목표체중 (kg)", "성별코드", "나이",
        "허리둘레 (cm)", "수축기 혈압", "이완기 혈압",
        "콜레스테롤 지수", "BMI"
    ]

    # ✅ 필요한 키가 모두 존재하는지 확인
    missing_keys = [key for key in required_keys if key not in user_data]
    if missing_keys:
        raise ValueError(f"🚨 입력 데이터에 필요한 키가 없습니다: {missing_keys}")

    try:
        # ✅ ID를 제외한 숫자형 데이터 변환
        converted_data = [float(user_data[key]) for key in required_keys if key != "ID"]

        # ✅ NumPy 배열로 변환 후 PyTorch 텐서로 변환
        input_array = np.array(converted_data).reshape(1, -1)  # (1, N) 형태로 변환
        input_tensor = torch.tensor(input_array, dtype=torch.float32)

        return input_tensor
    except ValueError as ve:
        raise ValueError(f"🚨 숫자 변환 중 오류 발생: {ve}")
    except Exception as e:
        raise ValueError(f"🚨 데이터 변환 중 알 수 없는 오류 발생: {e}")

