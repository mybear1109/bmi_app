import streamlit as st
import json
import os

# ✅ 페이지 설정
st.set_page_config(page_title="건강 관리 앱", page_icon="🏥", layout="wide")

# ✅ 필수 모듈 불러오기
from sidebar import get_selected_menu
from home import display_home_page
from prediction import display_prediction_page
from visualization import display_visualization_page
from ai_coach import display_ai_coach_page
from user_input import get_user_input
from user_data_utils import save_user_data, load_user_data
from model_manager import model_exercise, model_food  # ✅ 모델 올바르게 import
from login import display_auth_page, check_login_status, logout  # ✅ Import 확인
from gemma2_recommender import load_gemma_model

# ✅ 세션 초기화
def initialize_session():
    session_keys = [
        "logged_in", "nickname", "user_info", "show_signup",
        "guest_mode", "show_auth", "show_user_input", "user_data"
    ]
    for key in session_keys:
        if key not in st.session_state:
            st.session_state[key] = False if key not in ["nickname", "user_data"] else "게스트"

initialize_session()

# ✅ 메인 앱 함수
def app():
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state["logged_in"]:
            st.markdown(f"### 👋 환영합니다, **{st.session_state['nickname']}**님!")
            st.markdown("---")

            # 🔓 로그아웃 버튼
            if st.button("🔓 로그아웃", key="logout_btn"):
                logout()
                st.session_state["logged_in"] = False
                st.session_state["nickname"] = "게스트"
                st.session_state["user_data"] = None
                st.session_state["guest_mode"] = False
                st.session_state["show_auth"] = False
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

        st.markdown("<br><br>", unsafe_allow_html=True)

    # ✅ 로그인 상태 확인
    if not st.session_state["logged_in"] and st.session_state.get("show_auth", False):
        display_auth_page()
        return

    # ✅ 메뉴 선택 및 페이지 표시
    menu_option = get_selected_menu()

    if menu_option == "홈 화면":
        display_home_page()
    elif menu_option == "정보 입력":
        # ✅ 기존 데이터가 문자열이면 JSON 변환, 아니라면 그대로 사용
        existing_data = st.session_state.get("user_data", {})

        if isinstance(existing_data, str):  # 문자열이면 JSON 변환
            try:
                existing_data = json.loads(existing_data)  
            except json.JSONDecodeError:
                existing_data = {}

        user_id = st.session_state["nickname"]  # ✅ 사용자의 닉네임을 user_id로 사용

        user_data = get_user_input(existing_data=existing_data, user_id=user_id)  # ✅ user_id 전달

        if user_data:
            st.session_state["user_data"] = json.dumps(user_data)  # ✅ JSON 형태로 저장
            save_user_data(user_id, user_data)  # ✅ user_id 사용하여 저장
            st.success("✅ 사용자 정보가 저장되었습니다!")
            st.rerun()
    elif menu_option == "예측하기":
        display_prediction_page()
    elif menu_option == "데이터 시각화":
        display_visualization_page()
    elif menu_option == "AI 건강 코치":
        display_ai_coach_page()

# ✅ 앱 실행
if __name__ == "__main__":
    app()
