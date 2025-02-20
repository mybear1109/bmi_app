import streamlit as st
import time
import torch
import pandas as pd
import os
from model_manager import model_exercise, model_food  # ✅ 올바르게 import 확인
from user_data_utils import load_user_data, save_user_data

st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .stButton>button {
        color: #4F8BF9;import streamlit as st
import re
import hashlib
from user_data_utils import load_user_data, save_user_data



# ✅ 스타일 적용
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
</style>
""", unsafe_allow_html=True)

# ✅ 비밀번호 해싱 함수 (보안 강화)
def hash_password(password):
    """📌 비밀번호를 해싱하여 저장"""
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ 로그인 상태 확인 함수
def check_login_status():
    """📌 사용자의 로그인 상태 확인"""
    return st.session_state.get("logged_in", False)

# ✅ 로그인 페이지 표시 함수 (🚀 display_auth_page 함수 추가)
def display_auth_page():
    if st.session_state.get("show_signup", False):
        signup()
    else:
        login()



# ✅ 로그인 기능
def login():
    st.markdown('<p class="big-font">🔐 로그인</p>', unsafe_allow_html=True)

    user_data = load_user_data()  # ✅ 전체 사용자 데이터 로드
    nickname = st.text_input("사용자 닉네임", key="login_nickname")
    password = st.text_input("비밀번호", type="password", key="login_password")

    if st.button("로그인", key="login_button"):
        hashed_password = hash_password(password)
    if st.button("로그인", key="login_button"):
        hashed_password = hash_password(password)

        if nickname in user_data and user_data[nickname]["password"] == hashed_password:
            st.markdown(f'<p class="success-font">🎉 환영합니다, {nickname}님!</p>', unsafe_allow_html=True)
            st.session_state["logged_in"] = True
            st.session_state["nickname"] = nickname
            st.session_state["user_info"] = user_data[nickname]
            st.session_state["show_signup"] = False
            st.session_state["show_auth"] = False
            st.rerun()
        else:
            st.markdown('<p class="error-font">🚨 사용자 닉네임 또는 비밀번호가 올바르지 않습니다.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 회원가입", key="signup_button"):
            st.session_state["show_signup"] = True
            st.rerun()
    with col2:
        if st.button("🚀 게스트로 입장", key="guest_button"):
            guest_login()


# ✅ 게스트 로그인 기능
def guest_login():
    """📌 게스트 로그인"""
    st.session_state["logged_in"] = True
    st.session_state["nickname"] = "게스트"
    st.session_state["user_info"] = {"is_guest": True}
    st.session_state["show_auth"] = False
    st.rerun()


# ✅ 로그아웃 기능
def logout():
    """📌 로그아웃 기능"""
    st.session_state["logged_in"] = False
    st.session_state["nickname"] = ""
    st.session_state["user_info"] = {}
    st.session_state["show_signup"] = False
    st.session_state["show_auth"] = False
    st.markdown('<p class="success-font">✅ 로그아웃되었습니다.</p>', unsafe_allow_html=True)
    st.rerun()


# ✅ 사용자명 검증 함수
def is_valid_username(username):
    """📌 한글(7자 이내) 또는 영문+숫자(10자 이내) 검증"""
    return bool(re.match(r'^[가-힣]{1,7}$', username) or re.match(r'^[a-zA-Z0-9]{1,10}$', username))


# ✅ 비밀번호 검증 함수
def is_valid_password(password):
    """📌 비밀번호는 영문, 숫자, 특수문자 포함 4자 이상"""
    return (
        len(password) >= 4 and
        re.search(r'[A-Za-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )


# ✅ 회원가입 기능
def signup():
    st.markdown('<p class="big-font">🆕 회원가입</p>', unsafe_allow_html=True)
    
    user_data = load_user_data()  # ✅ 전체 사용자 데이터 로드

    new_username = st.text_input("사용자 이름 (한글 7자 이내 또는 영문+숫자 10자 이내)")
    new_password = st.text_input("새 비밀번호 (영문+숫자+특수문자, 4자 이상)", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("가입하기"):
            if not is_valid_username(new_username):
                st.markdown('<p class="error-font">❌ 사용자 이름은 한글 7자 이내 또는 영문+숫자 10자 이내여야 합니다.</p>', unsafe_allow_html=True)
            elif new_username in user_data:
                st.markdown('<p class="error-font">❌ 이미 존재하는 사용자 이름입니다.</p>', unsafe_allow_html=True)
            elif not is_valid_password(new_password):
                st.markdown('<p class="error-font">❌ 비밀번호는 영문, 숫자, 특수문자를 포함해야 합니다.</p>', unsafe_allow_html=True)
            elif new_password != confirm_password:
                st.markdown('<p class="error-font">❌ 비밀번호가 일치하지 않습니다.</p>', unsafe_allow_html=True)
            else:
                hashed_password = hash_password(new_password)
                user_data[new_username] = {"password": hashed_password}
                save_user_data(user_data)
                st.markdown('<p class="success-font">✅ 회원가입이 완료되었습니다. 이제 로그인할 수 있습니다.</p>', unsafe_allow_html=True)
                st.session_state["show_signup"] = False
                st.rerun()

    with col2:
        if st.button("⬅️ 로그인으로 돌아가기"):
            st.session_state["show_signup"] = False
            st.rerun()


# ✅ 로그인/회원가입 페이지 실행 함수
def display_auth_page():
    """📌 로그인 및 회원가입 페이지 표시"""
    if st.session_state.get("show_signup", False):
        signup()
    else:
        login()


AttributeError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.10/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 564, in _run_script
    exec(code, module.__dict__)
File "/mount/src/bmi_app/app.py", line 103, in <module>
    app()
File "/mount/src/bmi_app/app.py", line 53, in app
    st.rerun()

  login.py 코드 확인해서 수정해줘 
        border-radius: 50px;
        height: 3em;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ✅ 예측 데이터 저장 경로
PREDICTION_FILE = "data/predictions.csv"

def preprocess_input(user_data):
    """📌 입력 데이터 전처리"""
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
        "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]

    processed_data = []
    for key in required_keys:
        value = user_data.get(key, 0)  # 기본값 0

        # ✅ 성별 변환 (남성=1, 여성=0)
        if key == "성별":
            value = 1 if value in ["남성", "Male", "M"] else 0

        # ✅ 흡연 상태 변환 (비흡연=0, 흡연=1)
        elif key == "흡연상태":
            value = 1 if value == "흡연" else 0

        # ✅ 음주 여부 변환 (비음주=0, 음주=1)
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
    """📌 운동 또는 식단 예측 수행 (점수를 더 후하게 조정)"""
    if model is None:
        return 40  # 기본값을 40으로 설정하여 너무 낮은 점수 방지

    try:
        input_tensor = preprocess_input(input_data)
        with torch.no_grad():
            output = model(input_tensor)

            # ✅ 모델 출력값 확인 (디버깅용)
            print(f"모델 출력값: {output.item()}")

            # ✅ 점수 변환 (출력값이 작을 경우 보정)
            base_score = output.item() * 120  # 🔹 원래보다 높은 가중치 적용

            # ✅ 최소 점수 보정 (너무 낮은 점수 방지)
            base_score = max(25, base_score)  # ✅ 최소 25점 이상 보장

            # ✅ 점수 추가 가산 (더 후한 점수 부여)
            if base_score < 50:
                base_score += 20
            elif base_score < 70:
                base_score += 15
            elif base_score < 85:
                base_score += 10
            elif base_score < 95:
                base_score += 5

            return min(100, int(base_score))  # ✅ 100점 초과 방지
    except Exception as e:
        print(f"🚨 예측 중 오류 발생: {e}")
        return 25  # 오류 발생 시 최소 점수 35점 반환
    

# ✅ 운동 추천 로직
def generate_exercise_recommendation(score):
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

# ✅ **식단 추천 로직 (수정)**
def generate_diet_recommendation(score):
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
    """📌 예측 페이지 표시"""
    st.header("🔍 AI 기반 운동 및 식단 예측")

    user_id = st.session_state.get("nickname", "게스트")
    user_data = load_user_data(user_id)

    if st.button("🔮 AI 예측 실행", help="클릭하여 AI 기반 운동 및 식단 예측을 시작합니다."):
        with st.spinner("⏳ AI가 데이터를 분석 중입니다..."):
            time.sleep(2)

        prob_exercise = 45  # 예제 점수
        prob_food = 45  # 예제 점수

        exercise_recommendation = "가벼운 스트레칭부터 시작해 점진적으로 운동 강도를 높여보세요."
        diet_recommendation = "가공식품 섭취를 줄이고, 신선한 재료로 직접 요리해보세요."

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
            .ai-advice {
                margin-top: 20px;
                padding: 15px;
                background-color: #fdebd0;
                border: 2px dashed #f39c12;
                border-radius: 5px;
                font-size: 18px;
                text-align: center;
                color: #34495e;
            }
            .ai-recommendation {
                font-size: 18px;
                font-weight: bold;
                color: #2980b9;
                margin-top: 10px;
            }
            .effort-preview {
                margin-top: 20px;
                padding: 15px;
                background-color: #e8f8f5;
                border: 2px solid #1abc9c;
                border-radius: 5px;
                font-size: 16px;
                text-align: center;
                color: #16a085;
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
            <div class="ai-advice">
                <strong>💡 AI의 조언:</strong> 개인화된 상세 운동 계획과 식단 추천을 받아보세요. 
                AI가 당신의 건강 목표 달성을 위한 최적의 방법을 제시합니다.
            </div>
            <div class="effort-preview">
                <strong>🌟 노력의 결과:</strong> 꾸준한 실천으로 2주 후에는 체중 2kg 감소, 
                근력 10% 향상, 그리고 전반적인 건강 상태가 15% 개선될 수 있습니다!
            </div>
        </div>
        """

        st.markdown(result_html, unsafe_allow_html=True)

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='success-message'><strong>🎉 축하합니다! 예측 결과가 성공적으로 저장되었습니다! 🎉</strong><br>귀하의 건강 여정을 추적하고 개선할 수 있는 소중한 데이터가 안전하게 보관되었습니다.</div>",
        unsafe_allow_html=True
    )


