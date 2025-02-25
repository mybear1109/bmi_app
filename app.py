import streamlit as st
import json
import os
from sidebar import get_selected_menu
from home import display_home_page
from prediction import display_prediction_page
from visualization import display_visualization_page
from ai_coach import display_ai_coach_page
from user_input import get_user_input
from model_loader import model_exercise, model_food 
from user_data_utils import save_user_data, load_user_data
from login import display_auth_page, check_login_status, logout  
from info import display_info_page
from login_visualization import display_login_visualization 

# ✅ 세션 초기화 함수
def initialize_session():
    session_defaults = {
        "logged_in": False,
        "nickname": "게스트",
        "user_info": None,
        "show_signup": False,
        "guest_mode": False,
        "show_auth": False,
        "show_user_input": False,
        "user_data": None,
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session()

# ✅ 메인 앱 실행 함수
def app():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state["logged_in"]:
            st.markdown(f"### 👋 환영합니다, **{st.session_state['nickname']}**님!")
            st.markdown("---")

            # 🔓 로그아웃 버튼
            if st.button("🔓 로그아웃", key="logout_btn"):
                logout()
                initialize_session()  # ✅ 세션 초기화
                st.experimental_rerun()  # ✅ 로그아웃 후 즉시 새로고침

        else:
            if st.button("🔐 로그인/회원가입", key="login_btn"):
                st.session_state["show_auth"] = True
                st.experimental_rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 게스트 입장", key="guest_btn"):
                st.session_state["logged_in"] = True
                st.session_state["nickname"] = "게스트"
                st.session_state["guest_mode"] = True
                st.experimental_rerun()

    # ✅ 로그인 페이지로 이동 (로그인이 필요할 경우)
    if not st.session_state["logged_in"] and st.session_state.get("show_auth", False):
        display_auth_page()
        return

    # ✅ 메뉴 선택 및 페이지 이동
    menu_option = get_selected_menu()

    if menu_option == "홈 화면":
        display_home_page()

    elif menu_option == "내 정보":  # ✅ 로그인한 사용자 전용 메뉴 추가
        if not st.session_state["logged_in"]:
            st.warning("⚠️ 로그인 후 접근할 수 있습니다.")
        else:
            display_login_visualization()  # ✅ 문제 해결

    elif menu_option == "건강 정보 입력":
        existing_data = st.session_state.get("user_data", {})

        if isinstance(existing_data, str):
            try:
                existing_data = json.loads(existing_data)
            except json.JSONDecodeError:
                existing_data = {}

        user_id = st.session_state["nickname"]
        user_data = get_user_input(existing_data=existing_data, user_id=user_id)

        if user_data:
            st.session_state["user_data"] = json.dumps(user_data)
            save_user_data(user_id, user_data)
            st.success("✅ 사용자 정보가 저장되었습니다!")

    elif menu_option == "예측하기":
        display_prediction_page()

    elif menu_option == "데이터 시각화":
        display_visualization_page()

    elif menu_option == "AI 건강 코치":
        if not st.session_state.get("user_data"):
            st.warning("⚠️ 건강 정보를 입력한 후 AI 코치를 이용해주세요.")
        else:
            display_ai_coach_page()

    elif menu_option == "개발 과정":
        display_info_page()

# ✅ 앱 실행
if __name__ == "__main__":
    app()
