import streamlit as st
import re
import hashlib
import json
import os
from user_data_utils import load_user_data, save_user_data

USER_DATA_FILE = "data/user_data.json"

# ✅ 사용자 데이터 로드
def load_user_data():
    """📌 사용자 데이터 로드"""
    try:
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.warning("🚨 사용자 데이터 파일이 손상되었습니다. 기본값을 사용합니다.")
        return {}
    except Exception as e:
        st.error(f"🚨 사용자 데이터 로드 중 오류 발생: {e}")
        return {}

# ✅ 사용자 데이터 저장
def save_user_data(data):
    """📌 사용자 데이터 저장"""
    try:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"❌ 사용자 정보 저장 중 오류 발생: {e}")

# ✅ 비밀번호 해싱
def hash_password(password):
    """📌 비밀번호를 해싱하여 저장"""
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ 로그인 상태 확인
def check_login_status():
    """📌 사용자의 로그인 상태 확인"""
    return st.session_state.get("logged_in", False)

# ✅ 로그인 기능
def login():
    st.markdown('<h1 style="text-align: center; color: #007bff;">🔐 로그인</h1>', unsafe_allow_html=True)

    user_data = load_user_data() or {}
    nickname = st.text_input("사용자 닉네임", key="login_nickname")
    password = st.text_input("비밀번호", type="password", key="login_password")

    if st.button("로그인", key="login_button"):
        hashed_password = hash_password(password)

        try:
            if nickname in user_data and user_data[nickname]["password"] == hashed_password:
                st.session_state["logged_in"] = True
                st.session_state["nickname"] = nickname
                st.session_state["user_info"] = user_data[nickname]

                st.success(f"🎉 환영합니다, {nickname}님! 개인 페이지로 이동합니다.")
                st.experimental_set_query_params(logged_in="true")  # ✅ URL 파라미터 설정
                st.experimental_rerun()  # ✅ 로그인 후 자동 새로고침하여 개인 페이지로 이동
            else:
                st.error("🚨 사용자 닉네임 또는 비밀번호가 올바르지 않습니다.")
        except KeyError:
            st.error("🚨 사용자 데이터에 문제가 있습니다. 관리자에게 문의하세요.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 회원가입", key="signup_button"):
            st.session_state["show_signup"] = True
            st.experimental_rerun()
    with col2:
        if st.button("🚀 게스트로 입장", key="guest_button"):
            guest_login()

# ✅ 게스트 로그인
def guest_login():
    """📌 게스트 로그인"""
    st.session_state["logged_in"] = True
    st.session_state["nickname"] = "게스트"
    st.session_state["user_info"] = {"is_guest": True}
    st.experimental_set_query_params(logged_in="true")  # ✅ URL 파라미터 설정
    st.experimental_rerun()

# ✅ 로그아웃
def logout():
    """📌 로그아웃 기능"""
    st.session_state["logged_in"] = False
    st.session_state["nickname"] = ""
    st.session_state["user_info"] = {}
    st.session_state["show_signup"] = False

    st.success("✅ 로그아웃되었습니다. 로그인 페이지로 이동합니다.")
    st.experimental_set_query_params(logged_in="false")  # ✅ URL 파라미터 설정
    st.experimental_rerun()

# ✅ 회원가입 기능
def signup():
    st.markdown('<h1 style="text-align: center; color: #28a745;">🆕 회원가입</h1>', unsafe_allow_html=True)

    user_data = load_user_data() or {}

    new_username = st.text_input("사용자 이름 (한글 7자 이내 또는 영문+숫자 10자 이내)")
    new_password = st.text_input("새 비밀번호 (영문+숫자+특수문자, 4자 이상)", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("가입하기"):
            if new_username in user_data:
                st.error("❌ 이미 존재하는 사용자 이름입니다.")
            elif new_password != confirm_password:
                st.error("❌ 비밀번호가 일치하지 않습니다.")
            else:
                hashed_password = hash_password(new_password)
                user_data[new_username] = {"password": hashed_password}
                save_user_data(user_data)

                st.session_state["logged_in"] = True
                st.session_state["nickname"] = new_username
                st.session_state["user_info"] = user_data[new_username]

                st.success("✅ 회원가입 완료! 개인 페이지로 이동합니다.")
                st.experimental_set_query_params(logged_in="true")  # ✅ URL 파라미터 설정
                st.experimental_rerun()

    with col2:
        if st.button("⬅️ 로그인으로 돌아가기"):
            st.session_state["show_signup"] = False
            st.experimental_rerun()

# ✅ 개인 페이지로 자동 이동
if check_login_status():
    st.success("🎯 로그인 성공! 개인 페이지로 이동합니다.")
    st.switch_page("login_visualization.py")  # ✅ 개인 페이지로 이동 🚀

# ✅ 로그인 페이지 표시
elif st.session_state.get("show_signup", False):
    signup()
else:
    login()
