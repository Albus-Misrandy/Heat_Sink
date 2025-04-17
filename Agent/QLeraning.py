import numpy as np


class Q_Learning:
    def __init__(self, envs, learning_rates=0.01, discount_factor=0.9, epsilon=1.0):
        self.envs = envs
        self.alpha = learning_rates, learning_rates
        self.gamma = discount_factor
        self.epsilon = epsilon

        self.q_table = np.zeros(envs.state, envs.action)

    def choose_action(self, state):
        if np.random.uniform() < self.epsilon:
            return np.random.randint(self.envs.action)
        else:
            return np.argmax(self.q_table[state])

    def update(self, state, action, reward, state_):
        q_predict = self.q_table[state, action]
        q_target = reward + self.gamma * np.max(self.q_table[state_])
        self.q_table[state, action] += self.alpha * (q_target - q_predict)
