import streamlit as st
from streamlit_option_menu import option_menu

def get_selected_menu():
    """📌 사이드바 네비게이션 메뉴"""
    with st.sidebar:
      
       

# ✅ 옵션 메뉴 생성
        selected = option_menu(
            menu_title="메뉴",
            options=["홈 화면", "정보 입력", "예측하기", "AI 건강 코치", "데이터 시각화"],
            icons=["house-fill", "pencil-square", "graph-up", "robot", "pie-chart-fill"],  # 아이콘 수정
            menu_icon="menu-button",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#f0f2f6"},
                "icon": {"font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#e6e9ef",
                },
                "nav-link-selected": {"background-color": "#4caf50", "color": "white"},
            },
        )
    return selected  # ✅ 선택한 메뉴 반환
