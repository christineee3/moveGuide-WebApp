import torch
import torch.nn as nn

class Model(nn.Module):
    def __init__(self, input_dimension):
        super(Model, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dimension, 48),
            nn.ReLU(),
            nn.BatchNorm1d(48),
            nn.Linear(48, 80),
            nn.ReLU(),
            nn.BatchNorm1d(80),
            nn.Dropout(0.3),
            nn.Linear(80, 120),
            nn.ReLU(),
            nn.BatchNorm1d(120),
            nn.Dropout(0.3),
            nn.Linear(120, 60),
            nn.Linear(60, 20),
            nn.Dropout(0.3),
            nn.Linear(20, 1),
        )

    def forward(self, x):
        return self.model(x)
