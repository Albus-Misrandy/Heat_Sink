import numpy as np
from Serial_Port.SerialPort import HardwareInterface


class TemperatureEnv:
    def __init__(self, serial):
        # 环境参数
        self.T_target = 50  # 目标温度
        self.delta_T = 5.0  # 温度分箱间隔
        self.epsilon = 0.01  # 导数零值判定阈值
        self.max_steps = 200  # 最大步数
        self.serial = serial

        # 动态参数
        self.T = 0.0  # 初始温度
        self.dT = 0.0  # 初始导数
        self.time = 0.0  # 当前时间
        self.dt = 1.0  # 时间步长（秒）

        # 状态动作空间
        self.action_space = 6  # 6个离散动作
        self.state_space = 6  # 6个离散状态

    def reset(self):
        """重置环境到初始状态"""
        self.update_dynamics()

        return self.get_state()

    def get_state(self):
        """获取离散化后的状态"""
        if self.T < self.T_target:
            return 0
        
        if self.dT > self.epsilon:
            return 1
        elif abs(self.dT) <= self.epsilon:
            return 2
        else:
            over_T = self.T - self.T_target
            if over_T <= self.delta_T:
                return 3
            elif over_T <= 2*self.delta_T:
                return 4
            else:
                return 5

    def step(self, action):
        """执行动作，返回(next_state, reward, done, info)"""
        # Control the fan velocity
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
        T_list = self.serial.read_sensor()
        if T_list is not None:
            self.time = T_list[0]
            self.T = T_list[1]
            self.dT = T_list[2]

    def calculate_reward(self):
        """计算即时奖励"""
        error = abs(self.T - self.T_target)

        # 基础奖励
        if error < 1.0:
            reward = 10.0
        elif error < 5.0:
            reward = 1.0
        else:
            reward = -error * 0.5  # 惩罚偏离

        # 超调惩罚
        if self.T > self.T_target:
            if self.dT > 0:  # 继续升温
                reward -= 15.0
            elif self.dT < 0:  # 开始降温
                reward -= 5.0

        # 稳定奖励
        if abs(self.dT) < self.epsilon:
            reward += 2.0

        return reward

    def check_done(self):
        """检查终止条件"""
        # 稳定在目标温度附近
        if (abs(self.T - self.T_target) < 0.5 and
                abs(self.dT) < self.epsilon):
            return True
        return False

    def render(self):
        """可选：可视化当前状态"""
        print(f"Time: {self.time:.1f}s | Temp: {self.T:.1f}C | dT: {self.dT:.1f}C/s | State: {self.get_state()}")
