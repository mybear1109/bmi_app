import streamlit as st

# ✅ 페이지 설정 (import 문 아래에서 가장 먼저 실행)
st.set_page_config(page_title="건강 관리 앱", page_icon="🏥", layout="wide")

# ✅ 필요한 모듈 가져오기
from sidebar import get_selected_menu
from home import display_home_page
from prediction import display_prediction_page
from visualization import display_visualization_page
from ai_coach import display_ai_coach_page
from login import display_auth_page, check_login_status, logout

# ✅ 세션 상태 초기화
def initialize_session():
    """📌 세션 변수 초기화 (로그인 상태, 닉네임, 유저 정보, 게스트 모드)"""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "nickname" not in st.session_state:
        st.session_state["nickname"] = "게스트"
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = {}
    if "show_signup" not in st.session_state:
        st.session_state["show_signup"] = False
    if "guest_mode" not in st.session_state:
        st.session_state["guest_mode"] = False

# ✅ 세션 상태 초기화 실행
initialize_session()

def app():
    """📌 Streamlit 앱 실행 함수"""

    # ✅ 사이드바에 로그인 상태 및 메뉴 추가
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state["logged_in"]:
            st.markdown(f"### 👋 환영합니다, **{st.session_state['nickname']}**님!")
            st.markdown("---")
            if st.button("🔓 로그아웃", key="logout_btn"):
                logout()
                st.rerun()
        else:
            if st.button("🔐 로그인/회원가입", key="login_btn"):
                st.session_state["show_auth"] = True
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 게스트 입장", key="guest_btn"):
                st.session_state["logged_in"] = True
                st.session_state["nickname"] = "게스트"
                st.session_state["guest_mode"] = True
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # ✅ 로그인/회원가입 페이지 표시
    if not st.session_state["logged_in"] and st.session_state.get("show_auth", False):
        display_auth_page()
    else:
        # ✅ 메뉴 선택
        menu_option = get_selected_menu()

        # ✅ 선택한 페이지로 이동
        if menu_option == "🏠 홈 화면":
            display_home_page()
        elif menu_option == "🏋️‍♂️ 예측하기":
            display_prediction_page()
        elif menu_option == "🧑‍🏫 AI 건강 코치":
            display_ai_coach_page()
        elif menu_option == "📊 데이터 시각화":
            display_visualization_page()


if __name__ == "__main__":
    app()
