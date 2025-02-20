import torch
import torch.nn as nn

# ✅ 운동 예측 모델
import torch.nn.functional as F

class ExercisePredictionModel(nn.Module):
    def __init__(self, input_dim):
        super(ExercisePredictionModel, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return F.sigmoid(x) * 100  # ✅ 0~100 범위로 자동 변환

    
# ✅ 식단 예측 모델
class FoodPredictionModel(nn.Module):
    def __init__(self, input_dim):
        super(FoodPredictionModel, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 1)  # 🔹 점수 예측을 위한 1개의 출력 뉴런 사용
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return F.sigmoid(x) * 100  # ✅ 0~100 범위로 자동 변환