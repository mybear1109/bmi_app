import streamlit as st
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

# ✅ 로그인 페이지 표시 함수 (🚀 `display_auth_page` 함수 추가)
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
