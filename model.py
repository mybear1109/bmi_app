import torch

# ✅ 모델 클래스 정의
class PredictionModel(torch.nn.Module):
    def __init__(self, input_dim):
        super(PredictionModel, self).__init__()
        self.layer1 = torch.nn.Linear(input_dim, 64)
        self.layer2 = torch.nn.Linear(64, 32)
        self.layer3 = torch.nn.Linear(32, 2)  # 이진 분류 (운동/음식 섭취 여부)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)  # ✅ CrossEntropyLoss 사용 시 Softmax 불필요
        return x
