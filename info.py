import streamlit as st

def display_info_page():
    st.title("💪 AI 기반 개인 맞춤형 건강 관리 웹 애플리케이션 🍎")
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📌 프로젝트 개요")
    st.markdown("""
    본 프로젝트는 개인의 건강 데이터를 기반으로 AI 모델이 맞춤형 운동 계획과 식단 추천을 제공하는 Streamlit 웹 애플리케이션입니다. 
    국민건강보험공단의 100만 명 건강검진정보 데이터셋을 활용하여 사용자의 건강 상태를 정확하게 분석하고, 
    최신 `google/gemma-2-9b-it` 모델을 통해 개인에게 최적화된 솔루션을 제공합니다.

    ✨ **핵심 목표:** 기존 `KoGPT2`모델의 한계를 극복하고, 딥러닝 기반으로 더욱 정확하고 개인화된 건강 관리 솔루션을 제공하는 것입니다.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🧠 AI 모델 및 알고리즘")
    st.subheader("1. google/gemma-2-9b-it 모델")
    st.markdown("""
    ### 🌟 주요 특징

    - 대규모 언어 모델(LLM)로, 텍스트 생성에 특화된 90억 개의 파라미터를 가진 모델입니다.
    - Transformer 아키텍처를 기반으로 하며, 자기 주의 메커니즘을 사용합니다.
    - 다양한 건강 관련 데이터를 학습하여 맥락 이해 능력이 뛰어납니다.
    - 기존 KoGPT2 모델의 한계(JSON 변환 문제, 부적절한 답변 생성)를 극복했습니다.

    ### 🚀 주요 기능

    - 대화, 질문 응답, 요약, 코드 생성 등 다양한 텍스트 생성 작업 수행
    - 8K 토큰의 컨텍스트 길이 지원
    - 제로샷 학습 및 퓨샷 학습 능력 보유

    ### 📊 학습 과정

    1. **사전 학습:** 대규모 텍스트 데이터로 일반적 지식 습득
    2. **파인튜닝:** 건강 전문가가 검증한 운동 계획 및 식단 데이터로 특화 학습
    3. **프롬프트 엔지니어링:** 다양한 건강 상태와 목표에 대한 시나리오로 최적화
    4. **온라인 학습:** 실시간 데이터로 지속적 업데이트

    ### 🧠 모델 개선 기법

    - 지식 증류: 더 큰 모델의 지식을 작은 모델로 전달
    - 로컬-글로벌 어텐션 교차 및 그룹 쿼리 어텐션 도입

    ### 📌 기술적 세부사항

    - Hugging Face Transformers 라이브러리를 사용하여 파인튜닝 수행
    - 토크나이저 설정, 모델 구성, 가중치 로딩 등의 과정 포함
    - SafeTensors 형식으로 모델 가중치 저장 및 로드
    - 효율적인 메모리 관리를 위해 모델을 여러 샤드로 분할하여 저장 및 로드
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🏥 맞춤형 건강 관리 AI 솔루션")
    st.markdown("""
    본 프로젝트에서는 `google/gemma-2-9b-it` 모델을 기반으로 맞춤형 건강 관리 솔루션을 제공합니다.

    ### 🚀 주요 특징

    - **빠른 처리 속도와 향상된 성능**
    - **개인화된 운동 계획 및 식단 추천**
    - **28종의 건강 관련 데이터 처리 및 학습**
    
    ### 📊 데이터 시각화
    
    - 사용자의 건강 데이터를 다양한 그래프와 차트로 시각화
    - 건강 점수, 예측 결과, AI 모델의 추천 사항을 직관적으로 표시
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🧬 알레르기 및 식품 제한 처리 시스템")
    st.markdown("""
    - **목적:** 사용자의 알레르기 정보를 고려한 안전한 식단 추천
    - **주요 기능:**
        1. 알레르기 확장 및 교차 반응성 고려
        2. 대체 식품 추천
    - **지속적 업데이트:** 새로운 알레르기 정보 및 식품 데이터로 주기적 갱신
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🚀 기술 스택")
    st.markdown("""
    - 🐍 **Python:** 웹 애플리케이션 개발의 핵심 언어
    - 🎈 **Streamlit:** 사용자 친화적인 인터페이스를 위한 웹 프레임워크
    - 🤗 **Hugging Face Transformers:** `google/gemma-2-9b-it`모델 통합
    - 📈 **Plotly:** 인터랙티브 데이터 시각화
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🎯 성능 지표")
    st.markdown("""
    - 운동 여부 예측 정확도: 95.78%
    - 식단 개선 필요성 예측 정확도: 84.74%
    - 사용자 만족도: 4.8/5.0 (베타 테스트 기준)
    """)

    st.markdown("""
    이 혁신적인 AI 기반 건강 관리 시스템은 개인의 건강 데이터, 알레르기 정보, 그리고 최신 AI 기술을 결합하여
    사용자에게 안전하고 효과적인 맞춤형 건강 솔루션을 제공합니다. Gemma-2 모델의 강력한 성능과 세밀한 프롬프트 엔지니어링을 통해,
    사용자의 건강 상태와 목표에 최적화된 운동 계획과 식단 추천을 제공할 수 있게 되었습니다.
    """)

    st.markdown("---")
    
    github_url = "https://github.com/mybear1109/bmi_app/blob/main/README.md"
    
    st.markdown(f"""
    <a href="{github_url}" target="_blank">
        <button style="
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;">
            🚀 자세한 정보 보기
        </button>
    </a>
    """, unsafe_allow_html=True)
