import streamlit as st
import pandas as pd
import os
import torch
import json
from user_data_utils import load_user_data, save_user_data  
import re
import hashlib

# 스타일 적용
st.markdown("""
<style>
    .stApp {
        background-color: #f0f4f8;
    }
    .big-font {
        font-size: 36px !important;
        color: #1E90FF;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .success-font {
        color: #28a745;
        font-size: 18px;
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        text-align: center;
        margin: 10px 0;
    }
    .error-font {
        color: #dc3545;
        font-size: 18px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        text-align: center;
        margin: 10px 0;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #495057;
        border: 1px solid #ced4da;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }
    .stNumberInput > div > div > input {
        background-color: #ffffff;
        color: #495057;
        border: 1px solid #ced4da;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stSelectbox > div > div > div {
        background-color: #ffffff;
        color: #495057;
        border: 1px solid #ced4da;
        border-radius: 5px;
        padding: 5px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# 사용자 데이터 파일 경로 정의
USER_DATA_FILE = "data/user_data.json"

def get_user_input(user_id):
    """📌 사용자 건강 정보 입력 폼 (저장된 정보 불러오기 포함)"""
    
    # ✅ 기존 데이터 불러오기
    existing_data = load_user_data(user_id)  # 🔹 기존 데이터를 불러와 기본값으로 활용

    st.title("🏥 건강 정보 입력")

def get_user_input(existing_data, user_id):
    """
    📌 사용자 정보를 입력받아 반환하는 함수
    :param existing_data: 기존 사용자 데이터 (딕셔너리)
    :param user_id: 사용자 ID (닉네임 등)
    :return: 새로운 사용자 데이터 (딕셔너리)
    """
    if existing_data is None:
        existing_data = {}

    if isinstance(existing_data, str):  # ✅ 문자열이면 JSON 변환
        try:
            existing_data = json.loads(existing_data)
        except json.JSONDecodeError:
            existing_data = {}

    # ✅ 기본 정보 입력
    st.header("👤 기본 정보")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("성별", ["남성", "여성"], 
                              index=0 if existing_data.get("성별", "남성") == "남성" else 1)
        with col2:
            age = st.slider("연령", min_value=10, max_value=150, 
                            value=existing_data.get("연령대", 30))

    st.markdown("---")  # 구분선 추가

    # ✅ 신체 측정 정보 입력
    st.header("📏 신체 측정")
    with st.container():
            col1, col2 = st.columns(2)
            with col1:
                height = st.number_input("키 (cm)", min_value=100, max_value=250, 
                                     value=existing_data.get("키 (cm)", 170))
            with col2:
                waist = st.number_input("허리둘레 (cm)", min_value=50, max_value=150, 
                                    value=existing_data.get("허리둘레", 80))
            st.info("📌 복부비만 기준  남성: 90cm(35.4인치) 이상, 여성: 85cm(33.5인치) 이상 입니다.")    

            st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
            with st.container():
                col1, col2= st.columns(2)
                with col1:
                    weight = st.number_input("현재 체중 (kg)", min_value=30, max_value=200, 
                                    value=existing_data.get("현재 체중", 70))

                with col2:
                    goal_weight = st.number_input("목표 체중 (kg)", min_value=30, max_value=200, 
                                     value=existing_data.get("목표 체중", 60))

    st.markdown("---")  # 구분선 추가

    # ✅ 혈압 및 콜레스테롤 입력
    st.header("🩸 혈압, 혈당 및 콜레스테롤")
    with st.container():
            col1, col2 = st.columns(2)
            with col1:
                systolic_bp = st.number_input("수축기혈압 (최고 혈압)/ **정상 수치 120mmHg 미만**", min_value=80, max_value=200,
                                         value=existing_data.get("수축기혈압", 120))
                diastolic_bp = st.number_input("이완기혈압 (최저 혈압)/ **정상 수치 80mmHg 미만** ", min_value=40, max_value=130,
                                          value=existing_data.get("이완기혈압", 80))
            with col2:
                hdl = st.number_input("HDL 콜레스테롤/ **정상 수치 남자 40mg/dL이상, 여자 50mg/dL이상**", min_value=20, max_value=100,
                                  value=existing_data.get("HDL콜레스테롤", 50))
                ldl = st.number_input("LDL 콜레스테롤/ **정상 수치 90~130mg/dL** ", min_value=50, max_value=200,
                                  value=existing_data.get("LDL콜레스테롤", 100))
            
            st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
            with st.container():
                col1, col2= st.columns(2)
                with col1:
                   fasting_glucose = st.number_input("식전혈당 (mg/dL)/ **정상 수치 70~110mg/dL**",
                                                 min_value=50, max_value=300,
                                                 value=existing_data.get("식전혈당", 90))
                with col2:
                    triglyceride = st.number_input("트리글리세라이드(중성지방)/ **정상 수치 150mg/dL 미만**", min_value=50, max_value=500, 
                                                   value=existing_data.get("트리글리세라이드", 150))

    st.markdown("---")  # 구분선 추가

    # ✅ 생활 습관 입력
    st.header("🏃‍♂️ 생활 습관")
    with st.container():
            col1, col2 = st.columns(2)
            with col1:
                smoking_status = st.selectbox(" 흡연 상태", ["비흡연", "흡연"],
                                              index=["비흡연", "흡연"].index(
                                                  existing_data.get("흡연상태", "비흡연")))
            with col2:
                alcohol_status = st.selectbox("음주 여부", ["비음주", "음주"],
                                              index=["비음주", "음주"].index(existing_data.get("음주여부", "비음주")))
            
            st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
            with st.container():
                activity_level = st.selectbox("활동 수준", ["저활동", "중간활동", "고활동"],
                                              index=["저활동", "중간활동", "고활동"].index(existing_data.get("활동 수준", "저활동")))

    # ✅ 자동 계산된 지표 추가
    bmi = round(weight / ((height / 100) ** 2), 2) if height > 0 else 0.0
    total_cholesterol = ldl + hdl + triglyceride
    blood_pressure_diff = systolic_bp - diastolic_bp

    liver_health_index = round(
        (existing_data.get("혈청지오티(AST)", 30) + existing_data.get("혈청지피티(ALT)", 40) + existing_data.get("감마지티피", 50)) / 3, 2
    )

    obesity_risk_index = round(waist / bmi, 2) if bmi > 0 else 0.0

    # ✅ 사용자 데이터 저장
    user_data = {
        "user_id": user_id,
        "성별": gender,
        "연령대": age,
        "허리둘레": waist,
        "현재 체중": weight,
        "목표 체중": goal_weight,
        "수축기혈압(최고 혈압)": systolic_bp,
        "이완기혈압(최저 혈압)": diastolic_bp,
        "식전혈당(공복혈당)": fasting_glucose,
        "혈압 차이": blood_pressure_diff,
        "HDL콜레스테롤": hdl,
        "LDL콜레스테롤": ldl,
        "트리글리세라이드": triglyceride,
        "총콜레스테롤": total_cholesterol,
        "간 지표": liver_health_index,
        "BMI": round(bmi, 2),
        "비만 위험 지수": obesity_risk_index,
        "흡연상태": smoking_status,
        "음주여부": alcohol_status,
        "활동 수준": activity_level
    }

    # ✅ 입력한 데이터 미리보기
    st.markdown("<h4 style='text-align: center; color: #1f618d;'>🔍 입력한 데이터 미리보기</h4>", unsafe_allow_html=True)
    
    selected_columns = ["user_id", "성별", "연령대", "허리둘레", "BMI", "총콜레스테롤", "혈압 차이", "식전혈당(공복혈당)", "간 지표", "비만 위험 지수", "활동 수준"]
    # 컬럼 이름 변경 (줄 바꿈 추가)
 



    df_selected = pd.DataFrame([{col: user_data[col] for col in selected_columns}])

    # 특정 컬럼 소수점 2자리 유지
    for col in ["BMI", "비만 위험 지수", "간 지표"]:
        df_selected[col] = df_selected[col].apply(lambda x: f"{x:.2f}")
        
    df_selected = pd.DataFrame([{col: user_data[col] for col in selected_columns}])

    # 컬럼 이름 변경 (줄 바꿈 추가)
    selected_columns = [
        "user_id", "성별", "연령대", "허리둘레", "BMI", "총콜레스테롤", "혈압 차이", 
        "식전혈당\n(공복혈당)", "간 지표", "비만 위험\n지수", "활동 수준"
]


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
            background-color: #3498db;
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


    # 데이터프레임을 HTML 테이블로 변환
    html_table = df_selected.to_html(index=False, classes='dataframe')
    st.markdown(html_table, unsafe_allow_html=True)

    # 데이터 저장 버튼
    if st.button("✅ 저장하기"):
        if "data_saved" not in st.session_state:  # 상태가 없으면 저장
            save_user_data(user_id, user_data)  # 기존 데이터 덮어쓰기
            st.session_state["data_saved"] = True
            st.success("✅ 데이터가 성공적으로 저장되었습니다!")
        
     

    return user_data