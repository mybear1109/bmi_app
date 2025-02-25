# 💖 "당신의 오늘은 안녕하십니까?" 💖

## 🚀 AI 피트니스 코치: 개인 맞춤형 건강 관리의 혁명 🚀

### 🖥️ [홈페이지 바로가기](https://bmiapp-b8f7gzplqquawaid9efsrc.streamlit.app/)

<br>

---

<br>


## 🌟 프로젝트 개요

**"당신의 오늘은 안녕하십니까?"**는 바쁜 현대인들이 자신의 감정과 건강을 챙기도록 돕는 AI 기반 웹 애플리케이션입니다. **개인 맞춤형 운동 계획**과 **식단 추천**을 제공하여 사용자의 건강 관리를 돕습니다.

본 프로젝트는 **Gemini Pro (Gemma-2) 모델**을 활용하여 개인의 건강 데이터를 분석하고 **최적의 맞춤형 건강 솔루션**을 제공합니다. 개인적으로 진행되었으며, 사용자에게 최적화된 건강 관리 솔루션을 제공하는 것을 목표로 합니다.
<br>
<br>

---

<br>


## 🎯 프로젝트 목표

- ✅ **맞춤형 건강 관리**: AI 모델을 활용하여 개인의 건강 상태에 맞는 운동/식단 추천
- ✅ **사용자 친화적 UI**: Streamlit 기반 직관적인 인터페이스 제공
- ✅ **데이터 기반 인사이트**: 건강 데이터를 분석하여 장기적인 건강 관리 지원
- ✅ **지속적인 개선**: AI 모델을 지속적으로 업데이트하여 더 정확한 예측 제공

<br>
<br>

---

<br>


## ⚙️ 주요 기능

### 📝 건강 데이터 입력

사용자 친화적인 인터페이스를 통해 **기본 정보, 신체 측정, 생활 습관, 혈압/혈당/콜레스테롤** 등의 데이터를 간편하게 입력할 수 있습니다.

### 🧠 AI 기반 예측

**Gemini Pro (Gemma-2-9b-it) 모델**을 활용하여 운동 및 식단 개선 필요성을 예측합니다.

### 🍏 개인 맞춤형 운동/식단 추천

**Gemma-2 모델로 전환**하여 기존 KoGPT2 모델의 한계를 극복하고, AI가 사용자의 건강 상태를 분석하여 **운동 계획 & 식단 추천**을 생성합니다.

### 📊 데이터 시각화

사용자의 건강 데이터를 **그래프와 차트로 시각화**하여 건강 변화를 쉽게 확인할 수 있습니다.

### 🔑 사용자 계정 관리

회원가입 및 로그인 기능을 통해 **개인 건강 데이터를 안전하게 관리**합니다.

<br>
<br>

---

<br>


## 🤖 AI 모델 및 추천 시스템

### 주요 모델: Gemini Pro (Gemma-2-9b-it)

*   **모델 유형**: 대규모 언어 모델 (LLM), 텍스트 생성 특화
*   **파라미터 크기**: 90억 개 (9B)
*   **기반 아키텍처**: Transformer, 자기 주의 메커니즘 사용
*   **컨텍스트 길이**: 8K 토큰 지원
*   **특징**:

    *   다양한 건강 관련 데이터를 학습하여 문맥 이해 능력이 우수
    *   기존 KoGPT2 모델의 한계 극복 (JSON 변환 오류, 비정확한 추천 등)
    *   제로샷 및 퓨샷 학습 능력 보유
*   **주요 기능**:

    *   대화형 응답 생성
    *   질문 답변
    *   텍스트 요약
    *   맞춤형 운동 계획 및 식단 추천 생성

### 학습 과정

1.  **사전 학습**: 대규모 텍스트 데이터로 일반적인 지식 습득
2.  **파인튜닝**: 건강 전문가가 검증한 운동 계획 및 식단 데이터 사용 (Hugging Face Transformers 활용)
3.  **프롬프트 엔지니어링**: 다양한 건강 상태와 목표 시나리오 기반으로 최적화
4.  **온라인 학습**: 실시간 데이터를 활용한 지속적인 모델 업데이트

### 모델 개선 기법

*   지식 증류: 더 큰 모델의 지식을 작은 모델로 전달
*   로컬-글로벌 어텐션 교차: 문맥 이해 능력 향상
*   그룹 쿼리 어텐션: 효율적인 정보 처리

### 기술적 세부 사항

*   모델 저장 및 로딩: SafeTensors 형식 사용
*   메모리 관리: 모델을 여러 샤드로 분할하여 효율적으로 저장 및 로드
*   API 변경: 'use_auth_token' 대신 'token' 인자 사용 (보안 강화)

<br>
<br>

---

<br>


## 🚀 알고리즘 및 데이터 정보

### 사용 알고리즘

*   **운동/식단 추천**: Gemini Pro (Gemma-2-9b-it) 모델 활용
*   **운동/식단 필요성 예측**: XGBClassifier 활용




<br>



### 📊 데이터 미리보기


이 파일은 사용자의 건강 데이터와 예측 결과를 포함하고 있습니다.

#### 데이터 샘플

| user_id | 성별 | 연령대 | BMI | 총콜레스테롤 | 운동 점수 | 식단 점수 |
|---------|------|--------|-----|--------------|-----------|-----------|
| user_1  | 남성 | 30대   | 24.5| 180          | 75        | 80        |
| user_2  | 여성 | 40대   | 22.1| 190          | 65        | 70        |
| ...     | ...  | ...    | ... | ...          | ...       | ...       |


<br>

#### 주요 컬럼 설명

- `user_id`: 사용자 고유 식별자
- `성별`: 사용자의 성별 (남성/여성)
- `연령대`: 사용자의 연령대 (20대, 30대, ...)
- `BMI`: 체질량지수
- `총콜레스테롤`: 총 콜레스테롤 수치 (mg/dL)
- `운동 점수`: AI가 평가한 사용자의 운동 습관 점수 (0-100)
- `식단 점수`: AI가 평가한 사용자의 식단 습관 점수 (0-100)


<br>

#### 통계 정보

| 통계량 | BMI   | 총콜레스테롤 | 운동 점수 | 식단 점수 |
|--------|-------|--------------|-----------|-----------|
| 평균   | 23.5  | 185          | 70        | 75        |
| 중앙값 | 23.0  | 180          | 72        | 77        |
| 최소값 | 18.5  | 150          | 30        | 40        |
| 최대값 | 35.0  | 250          | 95        | 98        |


> 주의: 위의 통계 정보는 예시이며, 실제 데이터와 다를 수 있습니다.

자세한 데이터는  [AI 피트니스 코치 데이터](https://github.com/mybear1109/bmi_app/blob/main/data/predictions.csv)에서 확인하실 수 있습니다.

---


<br>

### 모델 성능 평가 결과

    
|  | 성능 지표 |	Precision |	Recall	| F1-score|
|:---|:---|:---|:---|:---|
| 0 | 운동 안 함	| 96%|	95%|	96% |
| 1 | 운동 함 |	95% | 96%	| 96% |
|전체 정확도	|		95.78%|


##### 🟢 혼동 행렬 (Confusion Matrix):

```
[[21124 1018]  
 [  853 21366]]
```


<br>

####   2. 🍽️ **음식 섭취 여부 예측 평가**

##### ✔ 정확도 (Accuracy): : 84.74%

|  | 성능 지표 |	Precision |	Recall	| F1-score|
|:---|:---|:---|:---|:---|
| 1 | 식단 개선 필요 없음	| 	88%		| 81%	| 	84%	| 
| 0 |  식단 개선 필요 | 	82%		| 89%	| 85%	| 
| 전체 정확도		| 		84.74%	| 

##### 🟢 혼동 행렬 (Confusion Matrix):

```
[[31923 7519]  
 [ 4459 34576]]
```

<br>
<br>

---

<br>


### 🎯 건강 점수 계산 시스템

1.  **개별 건강 지표 평가**: BMI, 허리둘레, 혈압, 콜레스테롤, 고혈당 위험, 간 지표, 흡연/음주 상태, 연령 등 다양한 건강 지표를 평가하고 4~10점 사이의 점수 부여
2.  **성별 특화 평가**: 허리둘레 평가에서 성별에 따라 다른 기준 적용
3.  **종합 점수 계산**: 각 지표의 점수를 합산하여 전체 건강 점수 산출
4.  **AI 모델 통합**: `predict_health_score` 함수를 통해 AI 모델의 예측 결과를 반영
5.  **맞춤형 가중치 적용**: 운동과 식단 추천에 대해 다른 가중치를 적용
    *   운동: AI 모델 30%, 건강 정보 70%
    *   식단: AI 모델 20%, 건강 정보 80%
6.  **보정 기능**: `calibration_factor`를 통해 모델 예측을 미세 조정

<br>

### 📊 데이터 시각화

*   사용자의 건강 데이터를 그래프와 차트로 시각화
*   건강 점수, 예측 결과, AI 모델 추천 사항을 직관적으로 표시

<br>
<br>

---

<br>

### 🧬 데이터 전처리

#### 📜 주요 데이터 소스

1.  국민건강보험공단 건강검진정보: 100만 명의 건강검진 데이터
2.  공공데이터포털 API: 검진기관별 정보 수집
3.  건강보험심사평가원 Open API 서비스: 보건의료 빅데이터 활용
4.  Kaggle Food Nutrition Dataset: 음식별 영양 정보 데이터
5.  Gemini Pro (Gemma-2-9b-it) 학습 데이터셋 (Common Crawl, Wikipedia 등)

<br>

#### ⚙️ 주요 전처리 과정

1.  **결측치 처리**: 수치형 컬럼은 중앙값, '식이섬유'는 0으로 대체하여 데이터 손실 최소화
2.  **텍스트 데이터 처리**: 특정 문자열로 대체하여 일관성 유지
3.  **이상치 제거**: 신뢰도 높은 데이터 확보

<br>

#### 🎯 주요 사용 컬럼

*   기본 정보 (성별, 연령대, 나이)
*   신체 측정 (키, 체중, 허리둘레, BMI)
*   혈액 검사 (총콜레스테롤, HDL, LDL, 트리글리세라이드, 식전혈당)
*   혈압 관련 (수축기, 이완기 혈압, 혈압 차이, 고혈압 위험)
*   생활 습관 (활동 수준, 흡연, 음주)
*   건강 위험 평가 (고혈당 위험, 간 지표, 비만 위험 지수)
*   건강 개선 지표 (운동/식단 개선 필요성, 운동/식단 점수)

<br>

### 🧬 알레르기 및 식품 제한 처리 시스템

*   사용자 알레르기 정보를 기반으로 안전한 식단 추천 제공
*   **주요 기능**:
    1.  알레르기 정보 확장: 알레르기 항목과 관련된 모든 식품군을 포함합니다.
    2.  교차 반응성 고려: 알레르기 간 교차 반응성을 고려한 식품을 제외합니다.
    3.  대체 식품 추천: 제외된 식품 대신 영양학적으로 유사한 대체 식품을 제안합니다.
*   **알레르기 정보 데이터베이스**:
    *   계란, 생선, 우유, 밀, 콩, 견과류, 갑각류, 과일, 육류, 해산물, 견과류 및 씨앗, 채소, 향신료, 기타(초콜릿, 카카오, 커피, 알코올, 인공감미료, 방부제) 등

<br>
<br>

---

<br>


## 🛠️ 기술 스택

<br>

*   <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> : 웹 애플리케이션 개발의 핵심 언어
*   <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> : 사용자 친화적인 인터페이스를 위한 웹 프레임워크
*   <img src="https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"> : 데이터 분석 및 조작
*   <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"> : 수치 계산
*   <img src="https://img.shields.io/badge/numpy-013243?style=for-the-badge&logo=numpy&logoColor=white"> : 머신러닝 모델 개발 및 평가
*   <img src="https://img.shields.io/badge/pytorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white"> : 딥러닝 모델 구현
*  <img src="https://img.shields.io/badge/huggingface-FFD21F?style=for-the-badge&logo=huggingface&logoColor=black"> : Gemini Pro (Gemma-2) 모델 활용
*   <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> : 인터랙티브한 데이터 시각화
*   <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white"> : 서버리스 환경 구축 (배포 후 변경 예정)
*   <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"> : 컨테이너 기반 개발 환경 구성


<br>
<br>

---

<br>

## 🗂️ 디렉토리 구조  

```

📁 health_app/
├── app.py                       # Streamlit 앱의 메인 실행 파일
├── login.py                     # 사용자 인증 관리 (회원가입, 로그인)
├── login_visualization.py       # 로그인 사용자 개인 건강 데이터 시각화
├── home.py                      # 앱의 홈 화면 구성
├── sidebar.py                   # 사이드바 메뉴 및 기능 설정
├── info.py                      # 앱 소개 및 주요 기능 설명 페이지
├── user_input.py                # 사용자 건강 정보 입력 폼
├── user_data_utils.py           # 사용자 데이터 처리 유틸리티
├── model.py                     # 데이터셋 처리 및 모델 관련 기능
├── model_manager.py             # AI 모델 관리 (저장, 로드)
├── prediction.py                # 건강 예측 로직 실행
├── visualization.py             # 전체 사용자 데이터 시각화
├── gemma-2_recommender.py       # AI 기반 맞춤형 건강 추천 시스템
├── ai_coach.py                  # AI 건강 코치 인터페이스
├── models/                      # 훈련된 AI 모델 저장 디렉토리
│   ├── model_exercise.pth       # 운동 추천 모델
│   └── model_food.pth           # 식단 추천 모델
├── data/                        # 데이터 저장 디렉토리
│   ├── predictions.csv          # 건강 예측 결과 데이터
│   └── user_data.json           # 사용자 프로필 데이터
├── requirements.txt             # 프로젝트 의존성 패키지 목록
└── .streamlit/                  # Streamlit 설정 디렉토리
    └── secrets.toml             # 보안 키 및 인증 정보


```
<br>
<br>

---


<br>

## 🚀 실행 방법  

<br>

### 1️⃣ 환경 설정  

```
pip install -r requirements.txt

```

<br> 



## 🔑 2️⃣ API 키 설정  

`.streamlit/secrets.toml` 파일을 생성하고, **Gemini Pro (Gemma-2-9b-it) 모델**의 API 키를 저장하세요.  

```
HUGGINGFACE_API_TOKEN  = "YOUR_API_KEY"

```

⚠️ 주의: .streamlit/secrets.toml 파일은 절대 GitHub 등 버전 관리 시스템에 업로드되지 않도록 설정해야 합니다.

<br>
<br>

---


<br>


## ✨ 기대 효과

*   개인 맞춤형 건강 관리 솔루션 제공
*   사용자의 건강 개선 및 유지에 기여
*   AI 기술을 활용한 건강 관리 서비스의 가능성 제시

<br>

---


<br>



## 📚 참고 자료

<br> 

1.  **국민건강보험공단 건강검진정보 데이터셋**:

    *   100만 명의 건강검진 데이터 ([공공데이터포털](https://www.data.go.kr/data/15007122/fileData.do#tab-layer-file) 에서 다운로드)

<br>  
     
2.  **공공데이터포털 API 활용**:

    *   REST API를 통해 검진기관별 정보 수집

<br>
   
3.  **건강보험심사평가원 Open API 서비스**:
     
    *   보건의료 빅데이터 활용
    
<br>  
    
4.  **Kaggle Food Nutrition Dataset**:
 <img src="https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=Kaggle&logoColor=white" />  

* 음식별 영양 정보 데이터

  [food-nutrition-dataset](https://www.kaggle.com/datasets/utsavdey1410/food-nutrition-dataset)
    
<br>  
    
5.  **Gemini Pro (Gemma-2-9b-it) 모델 데이터**:

<br> 


| 데이터셋 | 설명 | 출처 |
| --- | --- | --- |
| **Common Crawl** | 웹 크롤링을 통해 수집한 방대한 텍스트 데이터 | Common Crawl |
| **C4 (Colossal Clean Crawled Corpus)** | 필터링된 웹 문서 데이터셋 | TensorFlow Datasets |
| **Wikipedia** | 다국어 위키백과 문서 데이터 | Wikipedia |
| **BooksCorpus** | 다양한 책에서 추출된 문서 데이터 | BooksCorpus |
| **ArXiv & PubMed** | 연구 논문, 과학 논문 데이터 | ArXiv, PubMed |
| **OpenWebText2** | OpenAI GPT 모델 훈련에 사용된 고품질 웹 문서 | OpenWebText |
| **Multi-News Dataset** | 뉴스 기사 요약을 위한 다중 문서 데이터 | Multi-News |
| **Hacker News & StackExchange** | 개발자 커뮤니티 및 Q&A 플랫폼에서 추출한 데이터 | Hacker News |
| **GitHub Code** | 프로그래밍 코드 데이터 | GitHub |



 
<br>
<br>  

---

<br>



