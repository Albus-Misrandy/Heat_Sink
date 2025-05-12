import random
import torch.optim as optim
from collections import deque
from .DQN_net import *


# DQN智能体
class DQNAgent:
    def __init__(self, device, state_space, action_space, batch_size=64, gamma=0.99, epsilon_start=1.0, epsilon_end=0.1, epsilon_decay=200):
        self.state_space = state_space
        self.action_space = action_space
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.device = device

        self.model = DQN(state_space, action_space).to(self.device)
        self.target_model = DQN(state_space, action_space).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = deque(maxlen=1000)
        self.steps_done = 0

        self.reward_list = []
        self.epsilon_list = []
        self.loss_list = []

    def select_action(self, state):
        """选择一个动作"""
        sample = random.random()
        if sample < self.epsilon:
            return random.randint(0, self.action_space - 1)  # 随机选择动作
        else:
            with torch.no_grad():
                state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(self.device)
                q_values = self.model(state)
                return q_values.argmax().item()  # 选择Q值最大的动作

    def store_experience(self, state, action, reward, next_state, done):
        """存储经验"""
        self.memory.append((state, action, reward, next_state, done))

    def optimize_model(self):
        """优化模型"""
        if len(self.memory) < self.batch_size:
            return
        transitions = random.sample(self.memory, self.batch_size)
        batch = list(zip(*transitions))

        state_batch = torch.tensor(batch[0], dtype=torch.float32).to(self.device)
        action_batch = torch.tensor(batch[1], dtype=torch.long).to(self.device)
        reward_batch = torch.tensor(batch[2], dtype=torch.float32).to(self.device)
        next_state_batch = torch.tensor(batch[3], dtype=torch.float32).to(self.device)
        done_batch = torch.tensor(batch[4], dtype=torch.uint8).to(self.device)

        current_q_values = self.model(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze(1)
        next_q_values = self.target_model(next_state_batch).max(1)[0]
        target_q_values = reward_batch + (self.gamma * next_q_values * (1 - done_batch))

        loss = nn.MSELoss()(current_q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.reward_list.append(reward_batch.mean().item())
        self.epsilon_list.append(self.epsilon)
        self.loss_list.append(loss.item())

        if self.epsilon > self.epsilon_end:
            self.epsilon -= (1.0 - self.epsilon_end) / self.epsilon_decay

    def update_target_network(self):
        """更新目标网络"""
        self.target_model.load_state_dict(self.model.state_dict())
