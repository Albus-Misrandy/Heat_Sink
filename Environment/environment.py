import numpy as np


class TemperatureEnv:
    def __init__(self):
        # 环境参数
        self.T_target = 100.0  # 目标温度
        self.delta_T = 5.0  # 温度分箱间隔
        self.epsilon = 0.001  # 导数零值判定阈值
        self.max_steps = 200  # 最大步数

        # 动态参数
        self.T = 20.0  # 初始温度
        self.dT = 0.0  # 初始导数
        self.time = 0.0  # 当前时间
        self.dt = 1.0  # 时间步长（秒）

        # 状态动作空间
        self.action_space = 3  # 3个离散动作
        self.state_space = 6  # 6个离散状态

    def reset(self):
        """重置环境到初始状态"""
        self.T = 20.0
        self.dT = 0.0
        self.time = 0.0
        return self.get_state()

    def get_state(self):
        """获取离散化后的状态"""
        if self.T < self.T_target:
            return 0

        if self.T > self.T_target:
            if self.dT > self.epsilon:
                return 1
            elif abs(self.dT) <= self.epsilon:
                return 2
            elif self.dT < -self.epsilon:
                return 3

    def step(self, action):
        """执行动作，返回(next_state, reward, done, info)"""
        # 更新系统动态
        self.update_dynamics(action)

        # 计算奖励
        reward = self.calculate_reward()

        # 检查终止条件
        done = self._check_done()

        # 步数限制
        self.time += self.dt
        if self.time >= self.max_steps:
            done = True

        return self.get_state(), reward, done, {}

    def update_dynamics(self, action):
        """根据动作更新温度动态"""
        # 动作影响导数
        if action == 0:  # 加热
            self.dT += 2.0
        elif action == 2:  # 冷却
            self.dT -= 1.5

        # 物理约束
        self.dT = np.clip(self.dT, -3.0, 5.0)  # 导数限制

        # 更新温度：二阶系统模拟
        self.T += self.dT * self.dt
        self.T = max(self.T, 0.0)  # 温度不低于0

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

    def _check_done(self):
        """检查终止条件"""
        # 稳定在目标温度附近
        if (abs(self.T - self.T_target) < 0.5 and
                abs(self.dT) < self.epsilon):
            return True
        return False

    def render(self):
        """可选：可视化当前状态"""
        print(f"Time: {self.time:.1f}s | Temp: {self.T:.1f}C | dT: {self.dT:.1f}C/s | State: {self.get_state()}")
