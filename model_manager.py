import torch
import os
import streamlit as st
import dill  # ✅ 클래스 import 오류 해결
from transformers import AutoTokenizer, AutoModelForCausalLM
from model import ExercisePredictionModel, FoodPredictionModel  # ✅ 모델 클래스 import


# ✅ 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

# ✅ 모델 로드 함수
def load_model(model_path, model_class, input_dim=13):
    """📌 PyTorch 모델 로드 함수"""
    
    # ✅ 모델 클래스 인스턴스 생성
    model = model_class(input_dim)

    # ✅ 모델 파일 존재 여부 확인
    if not os.path.exists(model_path):
        print(f"🚨 모델 파일이 존재하지 않습니다: {model_path}")
        return None

    try:
        # ✅ PyTorch 모델 로드 (dill을 사용하여 pickle 오류 방지)
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"), pickle_module=dill)
        
        # ✅ 저장 형식 확인 및 모델 로딩
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"], strict=False)  # ✅ strict=False로 mismatch 방지
        else:
            model.load_state_dict(checkpoint, strict=False)

        model.eval()  # ✅ 모델을 평가 모드로 전환
        print(f"✅ 모델 로드 성공: {model_path}")
        return model

    except AttributeError as e:
        print(f"🚨 모델 클래스 오류 발생: {e}")
        print("❗ 해결 방법: `model_manager.py` 파일에서 모델 클래스가 올바르게 정의되었는지 확인하세요.")
    except Exception as e:
        print(f"🚨 모델 로드 중 오류 발생: {e}")
    
    return None

# ✅ 운동 및 식단 예측 모델 로드
model_exercise = load_model(MODEL_EXERCISE_PATH, ExercisePredictionModel, input_dim=13)
if model_exercise is None:
    print("🚨 운동 모델이 로드되지 않았습니다!")

model_food = load_model(MODEL_FOOD_PATH, FoodPredictionModel, input_dim=13)
if model_food is None:
    print("🚨 식단 모델이 로드되지 않았습니다!")



