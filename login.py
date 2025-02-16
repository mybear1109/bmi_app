import streamlit as st
import re
from user_data_utils import load_user_data, save_user_data

# ✅ 스타일 적용
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    color: #1E90FF;
}
.success-font {
    color: #32CD32;
    font-size: 16px;
}
.error-font {
    color: #FF4500;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ✅ 로그인 상태 확인
def check_login_status():
    return st.session_state.get("logged_in", False)

# ✅ 로그인 기능
def login():
    """📌 로그인 페이지"""
    st.markdown('<p class="big-font">🔐 로그인</p>', unsafe_allow_html=True)

    user_data = load_user_data()

    nickname = st.text_input("사용자 닉네임", key="login_nickname")
    password = st.text_input("비밀번호", type="password", key="login_password")

    if st.button("로그인", key="login_button"):
        if nickname in user_data and user_data[nickname]["password"] == password:
            st.markdown(f'<p class="success-font">🎉 환영합니다, {nickname}님!</p>', unsafe_allow_html=True)
            st.session_state["logged_in"] = True
            st.session_state["nickname"] = nickname
            st.session_state["user_info"] = user_data[nickname]
            st.session_state["show_signup"] = False
            st.session_state["show_auth"] = False
            st.rerun()
        else:
            st.markdown('<p class="error-font">🚨 사용자 닉네임 또는 비밀번호가 올바르지 않습니다.</p>', unsafe_allow_html=True)

    if st.button("🆕 회원가입", key="signup_button"):
        st.session_state["show_signup"] = True
        st.rerun()

# ✅ 로그아웃 기능
def logout():
    """📌 로그아웃 기능"""
    st.session_state["logged_in"] = False
    st.session_state["nickname"] = "게스트"
    st.session_state["user_info"] = {}
    st.session_state["show_signup"] = False
    st.session_state["show_auth"] = False
    st.markdown('<p class="success-font">✅ 로그아웃되었습니다.</p>', unsafe_allow_html=True)
    st.rerun()

# ✅ 사용자명 검증 함수 (한글 7자 이내, 영문 또는 영문+숫자 10자 이내 허용)
def is_valid_username(username):
    """📌 사용자 이름 검증: 한글 최대 7자, 영문 또는 영문+숫자 최대 10자"""
    if re.match(r'^[가-힣]{1,7}$', username):  # 한글 1~7자
        return True
    elif re.match(r'^[a-zA-Z0-9]{1,10}$', username):  # 영문/영문+숫자 1~10자
        return True
    return False


# ✅ 비밀번호 검증 함수 (4자리 이상, 영문+숫자 포함)
def is_valid_password(password):
    return (len(password) >= 4 and 
            re.search(r'[A-Za-z]', password) and 
            re.search(r'\d', password) and 
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password))


# ✅ 회원가입 기능
def signup():
    """🆕 회원가입 페이지"""
    st.title("🆕 회원가입")
    
    # ✅ 사용자 데이터 로드
    user_data = load_user_data()

    new_username = st.text_input("새 사용자 이름 (한글 7자, 영문 또는 영문+숫자 10자까지 가능)")
    new_password = st.text_input("새 비밀번호 (영문+특수문자+숫자, 4자 이상)", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("가입하기"):
            if not is_valid_username(new_username):
                st.error("❌ 사용자 이름은 한글 7자 이내 또는 영문/영문+숫자 10자 이내여야 합니다.")
            elif new_username in user_data:
                st.error("❌ 이미 존재하는 사용자 이름입니다.")
            elif not is_valid_password(new_password):
                st.error("비밀번호는 영문, 특수문자, 숫자를 모두 포함하고 4자 이상이어야 합니다.")
            elif new_password != confirm_password:
                st.error("❌ 비밀번호가 일치하지 않습니다.")
            else:
                user_data[new_username] = {"password": new_password}
                save_user_data(user_data)
                st.success("✅ 회원가입이 완료되었습니다. 이제 로그인할 수 있습니다.")
                st.session_state["show_signup"] = False
                st.rerun()  # ✅ 회원가입 후 로그인 페이지로 이동

    with col2:
        if st.button("⬅️ 로그인으로 돌아가기"):
            st.session_state["show_signup"] = False
            st.rerun()

# ✅ 메인 실행 함수
def display_auth_page():
    """📌 로그인 또는 회원가입 페이지 표시"""
    if st.session_state.get("show_signup", False):
        signup()
    else:
        login()
