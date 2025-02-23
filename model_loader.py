import torch
import os
import streamlit as st
import logging
from model import ExercisePredictionModel, FoodPredictionModel
from transformers import AutoTokenizer, AutoModelForCausalLM

# 로깅 설정 (필요에 따라 파일로도 기록할 수 있음)
logging.basicConfig(level=logging.ERROR)

# 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

def load_model(model_path, model_class, input_dim=13):
    """PyTorch 모델 로드 함수 (내부 로깅만 수행, 사용자에게는 메시지 표시하지 않음)"""
    model = model_class(input_dim)
    if not os.path.exists(model_path):
        logging.error(f"🚨 모델 파일을 찾을 수 없습니다: {model_path}")
        return None
    try:
        # weights_only=True 옵션을 사용하여 안전하게 모델 파라미터만 로드
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
        model.load_state_dict(checkpoint, strict=False)
        model.eval()
        logging.info(f"✅ 모델 로드 성공: {model_path}")
        return model
    except Exception as e:
        logging.error(f"🚨 모델 로드 중 오류 발생: {e}")
    return None

# 모델 로드 실행 (UI에는 성공/실패 메시지를 표시하지 않음)
model_exercise = load_model(MODEL_EXERCISE_PATH, ExercisePredictionModel, input_dim=13)
model_food = load_model(MODEL_FOOD_PATH, FoodPredictionModel, input_dim=13)

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")  # 미리 선언된 API 키 변수

@st.cache_resource
def load_gemma_model():
    """Gemma 모델과 토크나이저 로드 함수 (오류는 내부 로깅으로만 처리)"""
    model_name = "google/gemma-2b-it"
    try:
        hf_token = HF_API_KEY
        if not hf_token:
            logging.error("🚨 HF_API_KEY가 설정되지 않았습니다!")
            return None, None
        # AutoTokenizer를 사용하여 토크나이저 불러오기
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            use_auth_token=hf_token
        )
        logging.info("✅ Gemma 모델 로드 성공")
        return tokenizer, model
    except Exception as e:
        logging.error(f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        # 사용자에게는 아무런 메시지도 표시하지 않습니다.
        return None, None

# Gemma 모델과 토크나이저 로드 (UI에서는 관련 메시지 표시 X)
gemma_tokenizer, gemma_model = load_gemma_model()
