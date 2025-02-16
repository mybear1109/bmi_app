import torch
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from model import PredictionModel  # ✅ 모델 정의 파일 import

# ✅ 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

# ✅ 스케일러 (입력 데이터를 정규화하기 위한 StandardScaler)
scaler = StandardScaler()

# ✅ 모델 로드 함수
def load_model(model_path, input_dim=7):
    """💡 PyTorch 모델 로드 함수"""
    model = PredictionModel(input_dim)  # ✅ 모델 인스턴스 생성

    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))  # ✅ CPU 환경에서 로드
            model.eval()  # 모델을 평가 모드로 설정
            print(f"✅ 모델 로드 완료: {model_path}")
            return model
        except Exception as e:
            print(f"🚨 모델 로드 실패: {e}")
    else:
        print(f"🚨 모델 파일이 존재하지 않습니다: {model_path}")

    return None  # 모델 로드 실패 시 None 반환

# ✅ 모델 로드 실행
model_exercise = load_model(MODEL_EXERCISE_PATH, input_dim=7)
model_food = load_model(MODEL_FOOD_PATH, input_dim=7)

# ✅ 스케일러 학습 (예제 데이터 활용)
example_data = np.array([[170, 70, 65, 25, 1, 5, 22]])  # 가상의 입력 데이터 (7개 피처)
scaler.fit(example_data)  # 스케일러 학습

# ✅ 데이터 로드 함수
def load_data():
    """📥 데이터 로드 및 전처리"""
    try:
        # ✅ 데이터 파일 존재 여부 확인
        bmi_path = "data/bmi_data.csv"
        exercise_path = "data/exercise_data.csv"
        food_path = "data/food_data.csv"

        if not os.path.exists(bmi_path) or not os.path.exists(exercise_path) or not os.path.exists(food_path):
            print("🚨 일부 데이터 파일이 존재하지 않습니다.")
            return None

        # ✅ CSV 데이터 로드
        bmi_df = pd.read_csv(bmi_path)
        exercise_df = pd.read_csv(exercise_path)
        food_df = pd.read_csv(food_path)

        # ✅ 데이터 병합 (user_id 기준)
        merged_data = bmi_df.merge(exercise_df, on="user_id", how="inner")
        merged_data = merged_data.merge(food_df, on="user_id", how="inner")

        print("✅ 데이터 로드 및 병합 완료")
        return merged_data

    except Exception as e:
        print(f"🚨 데이터 로드 오류: {e}")
        return None
