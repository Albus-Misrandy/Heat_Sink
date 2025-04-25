import random
import torch.optim as optim
from collections import deque
from .DQN_net import *


# DQN智能体
class DQNAgent:
    def __init__(self, env, state_dim, action_dim, memory_cap, esp_start, esp_min, decay, gamma, lr, batch_size):
        self.env = env
        self.policy_net = DQN(1, 1)  # 策略网络
        self.target_net = DQN(1, 1)  # 目标网络
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # 目标网络不更新参数

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.memory = deque(maxlen=memory_cap)  # 经验回放缓冲区
        self.epsilon = esp_start
        self.loss = nn.MSELoss()
        self.batch_size = batch_size
        self.gamma = gamma
        self.esp_end = esp_min
        self.decay = decay

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.env.action_space - 1)
        else:
            with torch.no_grad():
                return self.policy_net(state).argmax().item()

    def store_transition(self, state, action, reward, next_state, done):
        # 存储转换到经验回放
        self.memory.append((state, action, reward, next_state, done))

    def update_target_net(self):
        # 更新目标网络
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def train(self):
        if len(self.memory) < self.batch_size:
            return 0

        # 从经验回放中随机采样
        batch = random.sample(self.memory, self.batch_size)
        state_batch = torch.cat([s for s, _, _, _, _ in batch])
        action_batch = torch.tensor([a for _, a, _, _, _ in batch])
        reward_batch = torch.tensor([r for _, _, r, _, _ in batch])
        next_state_batch = torch.cat([s for _, _, _, s, _ in batch])
        done_batch = torch.tensor([d for _, _, _, _, d in batch], dtype=torch.float32)

        # 计算当前Q值
        q_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))

        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values

        # 计算损失
        loss = self.loss(q_values, target_q_values.unsqueeze(1))

        # 优化网络
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 衰减探索率
        self.epsilon = max(self.esp_end, self.epsilon * self.decay)

        return loss.item()
