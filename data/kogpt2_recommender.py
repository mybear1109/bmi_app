import re
import torch
import pandas as pd
from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import streamlit as st

@st.cache_resource
def load_kogpt2_model():
    model_name = "skt/kogpt2-base-v2"
    try:
        tokenizer = GPT2TokenizerFast.from_pretrained(
            model_name, bos_token='</s>', eos_token='</s>',
            unk_token='<unk>', pad_token='<pad>', mask_token='<mask>'
        )
        model = GPT2LMHeadModel.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        st.error(f"🚨 모델 로딩 중 오류 발생: {e}")
        return None, None

def generate_recommendation_kogpt2(tokenizer, model, prompt, max_length=500):
    if tokenizer is None or model is None:
        return "🚨 모델을 로드하는데 실패했습니다."
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=200)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                do_sample=True
            )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return clean_text(generated_text.strip())
    except Exception as e:
        st.error(f"🚨 텍스트 생성 중 오류 발생: {e}")
        return "추천을 생성하는데 실패했습니다."

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|<.*?>|[^ㄱ-ㅎ가-힣a-zA-Z0-9\s:]", "", text)
    return text.strip()

def get_recommendations(category, user_info, tokenizer, model):
    prompts = {
        "운동": f"{user_info}\n사용자의 정보를 바탕으로 7일치 운동 계획과 각 운동당 칼로리 소모량을 표 형식으로 추천해주세요.",
        "식단": f"{user_info}\n사용자의 정보를 바탕으로 7일치 아침, 점심, 저녁 식단을 표 형식으로 추천해주세요.",
        "건강 상담": f"{user_info}\n사용자의 건강 상태에 대해 조언해주세요."
    }
    return generate_recommendation_kogpt2(tokenizer, model, prompts.get(category, "잘못된 요청입니다."))

def parse_recommendation_to_table(text):
    lines = text.split("\n")
    data = []
    for line in lines:
        columns = re.split(r'[:：]|\s{2,}', line)
        columns = [col.strip() for col in columns if col.strip()]
        if len(columns) >= 2:
            data.append(columns)
    
    if data:
        df = pd.DataFrame(data)
        return df
    else:
        return None


# ✅ 운동 계획 추천 함수
def get_workout_plan(user_info, tokenizer, model):
    workout_text = get_recommendations("운동", user_info, tokenizer, model)
    # 여기서 workout_text를 파싱하여 DataFrame으로 변환하는 로직 추가
    # 예시:
    workout_data = {
        "요일": ["월", "화", "수", "목", "금", "토", "일"],
        "운동": ["달리기 30분", "자전거 45분", "수영 30분", "휴식", "웨이트 60분", "달리기 45분", "휴식"],
        "칼로리 소모": [300, 400, 350, 0, 500, 450, 0]
    }
    return pd.DataFrame(workout_data)

# ✅ 식단 계획 추천 함수
def get_diet_plan(user_info, tokenizer, model):
    diet_text = get_recommendations("식단", user_info, tokenizer, model)
    # 여기서 diet_text를 파싱하여 DataFrame으로 변환하는 로직 추가
    # 예시:
    diet_data = {
        "요일": ["월", "화", "수", "목", "금", "토", "일"],
        "아침": ["계란 + 오트밀", "그릭 요거트", "과일 + 견과류", "계란 + 토스트", "오트밀", "그릭 요거트", "계란 + 채소"],
        "점심": ["닭가슴살 샐러드", "연어 샐러드", "현미밥 + 야채", "닭가슴살 샐러드", "연어 샐러드", "현미밥 + 야채", "닭가슴살 샐러드"],
        "저녁": ["구운 채소", "찐 생선", "닭가슴살", "구운 채소", "찐 생선", "닭가슴살", "구운 채소"]
    }
    return pd.DataFrame(diet_data)

# ✅ 건강 상담 추천 함수
def get_health_consultation(user_info, tokenizer, model):
    return get_recommendations("건강 상담", user_info, tokenizer, model)