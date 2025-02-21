import requests
import json
import os
import streamlit as st

# Hugging Face API Key를 secrets.toml에서 가져오기
HF_API_KEY = st.secrets["HF_API_KEY"]  # secrets.toml에 저장된 API 키를 사용

def generate_text_via_api(prompt, model_name="google/gemma-2-9b-it", max_tokens=256):
    """Hugging Face API를 사용하여 텍스트 생성"""
    # Hugging Face API 호출 URL
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    # 헤더에 API 키 추가
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 요청에 포함할 데이터 (프롬프트 및 기타 설정)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 1.3,  # 응답 다양성을 위해 온도 설정
        }
    }
    
    # API 요청을 통해 결과 가져오기
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # 응답 텍스트 반환
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"🚨 API 호출 오류: {e}")
        return {"메시지": "🚨 API 호출 오류 발생"}

def parse_json_response(response_json):
    """모델 응답을 JSON 형식으로 변환"""
    try:
        # 응답에서 생성된 텍스트를 추출합니다.
        if 'generated_text' in response_json:
            return json.loads(response_json['generated_text'])
        else:
            print("🚨 예상치 못한 응답 형식입니다.")
            return {"메시지": "🚨 JSON 데이터 변환 실패, 모델 응답을 확인하세요."}
    except json.JSONDecodeError:
        print("🚨 JSON 변환 오류 발생, 모델 응답을 확인하세요.")
        return {"메시지": "🚨 JSON 변환 오류"}

def get_gemma_recommendation(category, user_info, excluded_foods=[]):
    """Google Gemma 모델을 이용한 맞춤형 운동 & 식단 추천"""
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"

    if category == "운동":
        prompt += "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요."
    elif category == "식단":
        prompt += "사용자의 건강 상태를 고려한 7일 식단을 JSON 형식으로 제공해 주세요."
        if excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(excluded_foods)}**"

    system_content = (
        "당신은 전문적인 AI 피트니스 코치이며, 개인 맞춤형 건강 관리 전문가입니다. "
        "사용자의 건강 정보를 기반으로 최적의 운동 및 식단 계획을 작성해 주세요. "
        "일반적인 조언이 아니라, 사용자의 현재 건강 상태와 목표에 맞춘 상세한 가이드를 제공해야 합니다.\n\n"
        "운동 추천 시:\n"
        "- 사용자의 신체 상태(BMI, 체중, 활동 수준 등)에 따라 운동 강도를 조정하세요.\n"
        "- 매일 수행할 운동을 추천하고, 각 운동의 시간(분)과 예상 소모 칼로리를 포함하세요.\n"
        "- 운동 부위(상체, 하체, 코어 등)를 균형 있게 고려하세요.\n"
        "- 사용자가 피해야 할 운동(부상 위험, 건강 상태 고려)을 주의하세요.\n"
        "- 7일 운동 계획을 제공하세요.\n\n"
        "식단 추천 시:\n"
        "- 사용자의 건강 목표(체중 감량, 근육 증가, 혈압 관리 등)에 따라 식단을 맞춤 구성하세요.\n"
        "- 아침, 점심, 저녁 3끼를 추천하며, 각 식사의 영양 균형을 고려하세요.\n"
        "- 사용자가 알러지 반응을 보이거나 피해야 하는 음식은 포함하지 마세요.\n"
        "- 음식의 영양적 이점과 섭취 이유를 간략히 설명하세요.\n"
        "- 7일 식단 계획을 제공하세요.\n\n"
        "🚨 **모든 응답은 JSON 형식으로 제공해야 합니다!**\n"
        "운동 예시:\n"
        '[{"요일": "월요일", "운동": "러닝", "운동 시간(분)": 30, "칼로리 소모량(kcal)": 250}]\n'
        "식단 예시:\n"
        '[{"요일": "월요일", "아침": "현미밥 + 나물반찬", "점심": "닭가슴살 샐러드", "저녁": "구운 연어와 채소"}]\n'
    )

    prompt = system_content + prompt

    # Hugging Face API를 통해 텍스트 생성
    response_json = generate_text_via_api(prompt)

    # 응답 파싱
    return parse_json_response(response_json)
