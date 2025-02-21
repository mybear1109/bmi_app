import json
import re
import requests
from huggingface_hub import InferenceClient
import os
import streamlit as st
import pandas as pd

# 환경 변수에서 API 키를 가져옵니다
HF_API_KEY = os.getenv("HF_API_KEY")  # secrets.toml 또는 환경변수에서 API 키를 가져옵니다

# InferenceClient 객체 생성
client = InferenceClient(
    provider="hf-inference", 
    api_key=HF_API_KEY  # secrets.toml에서 API 키를 가져옵니다
)


def generate_text_via_api(prompt, model_name="google/gemma-2-9b-it"):
    """Hugging Face API를 사용하여 텍스트 생성"""
    messages = [
        {"role": "user", "content": prompt},
        {"role": "system", "content":         "당신은 전문적인 AI 피트니스 코치이며, 개인 맞춤형 건강 관리 전문가입니다. "
        "사용자의 건강 정보를 기반으로 최적의 운동 및 식단 계획을 작성해 주세요. "
        "일반적인 조언이 아니라, 사용자의 현재 건강 상태와 목표에 맞춘 상세한 가이드를 제공해야 합니다.\n\n"
        "예측결과의 점수에 따라 사용자에게 운동 및 식단을 추천해 주세요. "
        "운동 추천 점수가 높을수록 사용자의 운동 습관이 좋다는 의미이며, 식단 추천 점수가 높을수록 건강한 식습관을 갖고 있다는 의미입니다.\n\n"
        "운동 추천 시:\n"
        "- 사용자의 신체 상태(BMI, 체중, 활동 수준 등)에 따라 운동 강도를 조정하세요.\n"
        "- 매일 수행할 운동을 추천하고, 각 운동의 시간(분)과 예상 소모 칼로리를 포함하세요.\n"
        "- 운동 부위(상체, 하체, 코어 등)를 균형 있게 고려하세요.\n"
        "- 사용자가 피해야 할 운동(부상 위험, 건강 상태 고려)을 주의하세요.\n"
        "- 운동의 이점과 권장 이유를 간략히 설명하세요.\n"
        "- 운동 전후 스트레칭과 근력 운동을 포함하여 다양한 운동을 추천하세요.\n"
        "- 스트레칭만 하는 날도 포함하여 매일 운동 계획을 제공하세요.\n"
        "- 7일 운동 계획을 제공하세요.\n\n"
        "식단 추천 시:\n"
        "- 사용자의 건강 목표(체중 감량, 근육 증가, 혈압 관리 등)에 따라 식단을 맞춤 구성하세요.\n"
        "- 아침, 점심, 저녁 3끼를 추천하며, 각 식사의 영양 균형을 고려하세요.\n"
        "- 사용자가 알러지 반응을 보이거나 피해야 하는 음식은 포함하지 마세요.\n"
        "- 음식의 영양적 이점과 섭취 이유를 간략히 설명하세요.\n"
        "- 다이어트를 할경우 칼로리 및 영양소 함량을 고려하여 작성해주세요\n"
        "- 일일 권장 칼로리를 초과하지 않도록 주의하세요.\n"
        "- 7일 식단 계획을 제공하세요.\n\n"
        "추천 결과를 작성할 때, 사용자의 건강을 최우선으로 고려하고, 신속하고 친절한 답변을 제공해 주세요.\n\n"
        "운동 및 식단 예시를 포함하여 최대한 구체적으로 작성해 주세요.\n\n"
        "운동과 식단의 경우 목표체중을 위해 계산해서 작성해주세요 \n\n"
        "아래 예시를 참고하여 작성해 주세요.\n\n"
        "운동 예시:\n"
        '[{"요일": ["월", "화", "수", "목", "금", "토", "일"],"운동": ["달리기 30분", "자전거 45분", "수영 30분", "휴식", "웨이트 60분", "달리기 45분", "휴식"],  "칼로리 소모": [300, 400, 350, 0, 500, 450, 0]}]\n'
        "식단 예시:\n"
        '[{"요일": ["월", "화", "수", "목", "금", "토", "일"], "월", "아침": ["계란 + 오트밀", "그릭 요거트", "과일 + 견과류", "계란 + 토스트", "오트밀", "그릭 요거트","총칼로리 (kcal): 250"],  "점심": ["닭가슴살 샐러드", "연어 샐러드", "현미밥 + 야채", "닭가슴살 샐러드", "연어 샐러드", "현미밥 + 야채", "닭가슴살 샐러드","총칼로리 (kcal): 250"], , "저녁": ["구운 채소", "찐 생선", "닭가슴살", "구운 채소", "찐 생선", "닭가슴살", "구운 채소","총칼로리 (kcal): 250"],"총칼로리 (kcal): 750"}]\n\n'
        "식단 계획 추천 과 운동 계획 추천 을 선택하여 따로 작성해주세요\n\n"
        "유저가 버튼을 눌렀을경우 각각의 추천 결과를 보여주는 함수에 따라 결과를 보여주세요\n\n"
        }
    ]
    try:
        response_json = client.chat.completions.create(
            model=model_name,
            messages=messages,
   
        )
        return parse_json_response(response_json)
    except requests.exceptions.RequestException as e:
        print(f"🚨 API 호출 오류: {e}")
        return {"메시지": "🚨 API 호출 오류 발생"}


def parse_json_response(response_json):
    """모델 응답을 JSON 형식으로 변환"""
    try:
        content = response_json['choices'][0]['message']['content']
        
        # 응답이 텍스트일 경우 JSON 형식으로 처리하지 않고 텍스트를 그대로 반환
        if "```json" not in content:
            print(f"content 형식입니다. 응답 내용: {content}")
            return {"메시지": f" {content}"}
     

        # JSON 부분만 추출해서 처리
        json_text = content.split("```json")[-1].split("```")[0].strip()  # json 형식만 추출
        try:
            # 제어 문자를 처리하기 위해 '\r', '\n', '\t', '\f' 등을 공백으로 변환
            json_text = json_text.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t").replace("\f", "\\f")
            
            # 작은따옴표를 큰따옴표로 변경
            json_text = json_text.replace("'", '"')  # 작은따옴표를 큰따옴표로 변경

            # 수정된 JSON 텍스트를 파싱하여 반환
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"json_text 형식입니다. 응답 내용: {json_text}")
            print(f"오류 위치: {e}")
            return {"메시지": "🚨 JSON 변환 오류"}

    except KeyError as e:
        print(f"🚨 응답에서 필수 항목을 찾을 수 없음: {e}")
        return {"메시지": "🚨 응답 처리 오류"}
    
def get_user_info_with_default(user_data):
    """사용자 정보를 기본값으로 대체하여 유효한 정보를 반환"""
    default_info = {
        "BMI": 24.5,
        "허리둘레": "80cm",
        "수축기혈압(최고 혈압)": 120,
        "이완기혈압(최저 혈압)": 80,
        "혈압 차이": 40,
        "총콜레스테롤": 190,
        "고혈당 위험": "낮음",
        "간 지표": "정상",
        "성별": "남성",
        "연령대": "30대",
        "비만 위험 지수": "보통",
        "흡연상태": "비흡연",
        "음주여부": "비음주"
    }
    # 미측정된 항목을 기본값으로 채우기
    for key, value in user_data.items():
        if value == "미측정":
            user_data[key] = default_info.get(key, "미측정")
    return user_data


def expand_allergies(allergies):
    """알레르기 목록을 확장하여 관련 모든 식품을 포함"""
    allergy_mapping = {
        '계란': ['계란', '계란노른자', '계란흰자', '달걀', '노른자', '흰자'],
        '생선': ['생선', '연어', '참치', '광어'],
        '우유': ['우유', '요구르트', '치즈'],
        '콩': ['콩', '두부', '콩나물'],
        '밀가루': ['밀가루', '빵', '면'],
        '아몬드': ['아몬드', '호두', '땅콩'],
        '닭고기': ['닭고기', '닭가슴살', '닭날개'],
        '소고기': ['소고기', '소불고기', '소양지'],
        '돼지고기': ['돼지고기', '삼겹살', '목살'],
        '새우': ['새우', '게', '랍스터'],
    }
    expanded = set()
    for allergy in allergies:
        if allergy in allergy_mapping:
            expanded.update(allergy_mapping[allergy])
        else:
            expanded.add(allergy)
    return list(expanded)

# 운동 및 식단 추천 로직
def get_gemma_recommendation(category, user_info, allergies=[], excluded_foods=[]):
    """운동 및 식단 추천 함수"""
    user_info = get_user_info_with_default(user_info)  # 미측정된 정보 기본값으로 대체
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"

    if category == "운동":
        prompt += "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 제공해 주세요."
    elif category == "식단":
        prompt += "사용자의 건강 상태를 고려한 7일 식단을 제공해 주세요."
        
        # 알레르기 정보 확장 및 처리
        expanded_allergies = expand_allergies(allergies)
        all_excluded_foods = set(expanded_allergies + excluded_foods)
        
        if all_excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(all_excluded_foods)}**"

    return generate_text_via_api(prompt)


    
