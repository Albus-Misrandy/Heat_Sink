import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import struct
import time

class TemperatureEnv:
    def __init__(self, serial, target_temp=50, delta_T=5.0, epsilon=0.005, max_steps=500):
        # 环境参数
        self.T_target = target_temp  # 目标温度
        self.delta_T = delta_T  # 温度分箱间隔
        self.epsilon = epsilon  # 导数零值判定阈值
        self.max_steps = max_steps  # 最大步数
        self.serial = serial  # 串口通信接口

        # 动态参数
        self.T = 0.0  # 初始温度
        self.dT = 0.0  # 初始导数
        self.time = 0.0  # 当前时间
        self.dt = 1.0  # 时间步长（秒）

        # 状态动作空间
        self.action_space = 10  # 10个离散动作（风扇转速档次 0-9）
        self.state_space = 6  # 离散状态数量

        # 安全参数
        self.emergency_temp = 65  # 紧急温度阈值(℃)
        self.last_action = 5  # 上次动作（初始中值）

    def reset(self):
        """重置环境到初始状态"""
        self.update_dynamics()
        return self.get_state()

    def get_state(self):
        """获取离散化后的状态"""
        if self.T < self.T_target:
            return 0  # 温度未达到目标
        if self.dT > self.epsilon:
            return 1  # 温度继续升高
        elif abs(self.dT) <= self.epsilon:
            return 2  # 温度趋于平稳
        elif self.dT < 0:
            over_T = self.T - self.T_target
            if over_T <= self.delta_T:
                return 3  # 温度开始降温，接近目标
            elif over_T <= 2*self.delta_T:
                return 4  # 温度降温到一定程度
            else:
                return 5  # 温度远离目标，降温过度

    def step(self, action):
        """执行动作，返回(next_state, reward, done, info)"""
        # 控制风扇转速
        self.serial.send_float_data(action)
        # 更新系统动态
        self.update_dynamics()

        # 计算奖励
        reward = self.calculate_reward()

        # 检查终止条件
        done = self.check_done()

        # 步数限制
        self.time += self.dt
        if self.time >= self.max_steps:
            done = True

        return self.get_state(), reward, done, {}

    def update_dynamics(self):
        """根据动作更新温度动态"""
        T_list = self.serial.read_sensor_5bits()
        if T_list is not None:
            self.time = T_list[0]
            self.T = T_list[1]
            self.dT = T_list[2]

    def calculate_reward(self):
        """计算即时奖励"""
        error = abs(self.T - self.T_target)
        reward = -error * 0.5  # 基本奖励

        if self.T > self.T_target:
            if self.dT > 0:  # 继续升温
                reward -= 10.0  # 强烈惩罚继续加热
            elif self.dT < 0:  # 开始降温
                reward -= 5.0   # 适度惩罚降温

        if abs(self.dT) < self.epsilon:
            reward += 2.0  # 温度稳定奖励

        # 紧急温度超调惩罚
        if self.T > self.emergency_temp:
            reward -= 50.0  # 强烈惩罚超过紧急温度

        return reward

    def check_done(self):
        """检查是否满足终止条件"""
        if self.T > self.emergency_temp:
            return True  # 温度超过紧急阈值
        if abs(self.T - self.T_target) < 0.5 and abs(self.dT) < self.epsilon:
            return True  # 达到目标温度，结束
        return False
