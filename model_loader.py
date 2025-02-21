import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import streamlit as st
from model import ExercisePredictionModel, FoodPredictionModel
from transformers import AutoTokenizer, AutoModelForCausalLM 

# ✅ 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

# ✅ 모델 로드 함수
def load_model(model_path, model_class, input_dim=13):
    """💡 PyTorch 모델 로드 함수"""
    
    model = model_class(input_dim)

    if not os.path.exists(model_path):
        print(f"🚨 모델 파일을 찾을 수 없습니다: {model_path}")
        return None

    try:
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"))

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)

        model.eval()
        print(f"✅ 모델 로드 성공: {model_path}")
        return model

    except Exception as e:
        print(f"🚨 모델 로드 중 오류 발생: {e}")
    
    return None

# ✅ 모델 로드 실행
model_exercise = load_model(MODEL_EXERCISE_PATH, ExercisePredictionModel, input_dim=13)
model_food = load_model(MODEL_FOOD_PATH, FoodPredictionModel, input_dim=13)

# ✅ Hugging Face AI 모델 로드
@st.cache_resource
def load_gemma_model():
    """📌 Google Gemma AI 모델 로드"""
    model_name = "google/gemma-2b-it"
    
    try:
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not hf_token:
            raise ValueError("🚨 Hugging Face API Token이 설정되지 않았습니다!")

        tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16, token=hf_token)

        print("✅ Gemma 모델 로드 성공")
        return tokenizer, model
    except Exception as e:
        print(f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        return None, None
