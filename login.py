import streamlit as st
import json
import os
import hashlib
from user_data_utils import load_user_data, save_user_data

USER_DATA_FILE = "data/user_data.json"

# ✅ 사용자 데이터 로드 함수
def load_user_data():
    try:
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.warning(f"🚨 사용자 데이터 파일({USER_DATA_FILE})이 손상되었습니다. 기본값을 사용합니다.")
        return {}
    except Exception as e:
        st.error(f"🚨 사용자 데이터 로드 중 오류 발생: {e}")
        return {}

# ✅ 사용자 데이터 저장 함수
def save_user_data(data):
    try:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"❌ 사용자 정보 저장 중 오류 발생: {e}")

# ✅ 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ 로그인 상태 확인 함수
def check_login_status():
    return st.session_state.get("logged_in", False)

# ✅ 로그인 기능
def login():
    st.title("🔐 로그인")

    user_data = load_user_data()
    nickname = st.text_input("사용자 닉네임", key="login_nickname")
    password = st.text_input("비밀번호", type="password", key="login_password")

    if st.button("로그인", key="login_button"):
        hashed_password = hash_password(password)

        try:
            if nickname in user_data and user_data[nickname]["password"] == hashed_password:
                st.session_state["logged_in"] = True
                st.session_state["nickname"] = nickname
                st.session_state["user_info"] = user_data[nickname]
                st.success(f"🎉 환영합니다, {nickname}님!")
                st.experimental_rerun()
            else:
                st.error("🚨 사용자 닉네임 또는 비밀번호가 올바르지 않습니다.")
        except KeyError:
            st.error("🚨 사용자 데이터에 문제가 있습니다. 관리자에게 문의하세요.")

# ✅ 로그아웃 기능
def logout():
    st.session_state["logged_in"] = False
    st.session_state["nickname"] = "게스트"
    st.session_state["user_info"] = None
    st.experimental_rerun()

# ✅ 회원가입 기능
def signup():
    st.title("🆕 회원가입")

    user_data = load_user_data()
    new_username = st.text_input("사용자 이름 (한글 7자 이내 또는 영문+숫자 10자 이내)")
    new_password = st.text_input("새 비밀번호 (영문+숫자+특수문자 포함 4자 이상)", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")

    if st.button("가입하기"):
        if new_username in user_data:
            st.error("❌ 이미 존재하는 사용자 이름입니다.")
        elif new_password != confirm_password:
            st.error("❌ 비밀번호가 일치하지 않습니다.")
        else:
            hashed_password = hash_password(new_password)
            user_data[new_username] = {"password": hashed_password}
            save_user_data(user_data)
            st.success("✅ 회원가입이 완료되었습니다! 로그인 해주세요.")
            st.experimental_rerun()

# ✅ 로그인/회원가입 페이지 표시
def display_auth_page():
    if st.session_state.get("show_signup", False):
        signup()
    else:
        login()
