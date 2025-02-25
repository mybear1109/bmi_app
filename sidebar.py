import streamlit as st
from streamlit_option_menu import option_menu

def get_selected_menu():
    """📌 사이드바 네비게이션 메뉴"""
    
    menu_options = [
        "홈 화면",
        "건강 정보 입력", 
        "예측하기", 
        "AI 건강 코치", 
        "데이터 시각화",
        "개발 과정",
    ]

    menu_icons = [
        "house-heart",  # 홈 화면 아이콘
        "pencil-square",  # 건강 정보 입력 아이콘
        "graph-up",  # 예측하기 아이콘
        "robot",  # AI 건강 코치 아이콘
        "bar-chart-steps",  # 데이터 시각화 아이콘
        "lightbulb",  # 개발 과정 아이콘
    ]

    # ✅ 로그인 상태라면 "내 정보" 메뉴 추가
    if st.session_state.get("logged_in", False):
        menu_options.insert(1, "내 정보")
        menu_icons.insert(1, "person-circle")  # 👤 사용자 아이콘

    with st.sidebar:
        selected = option_menu(
            menu_title=" 메뉴",
            options=menu_options,
            icons=menu_icons,
            menu_icon="heart-pulse",  # 심장박동 아이콘
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#f0f2f6"},
                "icon": {"font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e6e9ef",
                },
                "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
            },
        )
    return selected  # ✅ 선택한 메뉴 반환
