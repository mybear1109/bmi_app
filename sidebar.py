import streamlit as st
from streamlit_option_menu import option_menu

def get_selected_menu():
    """📌 사이드바 네비게이션 메뉴"""
    with st.sidebar:
        selected = option_menu(
            menu_title=" 메뉴",
            options=[
                "홈 화면", 
                "건강 정보 입력", 
                "예측하기", 
                "AI 건강 코치", 
                "데이터 시각화",
                "개발과정",
            ],
            icons=[
                "house-heart",  # 집 모양에 하트가 있는 아이콘
                "pencil-square",  # 연필과 종이 아이콘
                "graph-up",   # 수정 구슬 아이콘 (예측을 나타냄)
                "robot",          # 로봇 아이콘
                "bar-chart-steps",# 단계별 막대 차트 아이콘
                "lightbulb",    # 전구 아이콘 (아이디어를 나타냄)
            ],
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
