import argparse
import torch
from Serial_Port.SerialPort import HardwareInterface
from Environment.environment import TemperatureEnv
from Agent.Agent import DQNAgent
from utils.plot_function import *

parser = argparse.ArgumentParser(description="Q Learning of Heat Sink.")

parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate of the serial port.")
parser.add_argument("--COM", type=str, default='COM4', help="The number of the serial port com.")
parser.add_argument("--Iterations", type=int, default=100, help="Training iterations.")
parser.add_argument("--learning_rate", type=float, default=0.001, help="Value of Alpha.")
parser.add_argument("--discount", type=float, default=0.9, help="Value of gamma.")
parser.add_argument("--batch_size", type=int, default=64, help="Value of batch size")
parser.add_argument("--decay", type=float, default=0.995, help="Value of decay")
parser.add_argument("--memory_capacity", type=int, default=100, help="Memory of capacity.")
parser.add_argument("--greedy_start", type=float, default=1.0, help="Initial exploration rate.")
parser.add_argument("--greedy_end", type=float, default=0.9, help="Minimum exploration rate.")

args = parser.parse_args()


def main_train(agent, env, epochs):
    reward_list = []
    epsilon_list = []
    loss_list = []

    for epoch in range(epochs):
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = agent.select_action(state)
            next_state, reward, done, _ = env.step(action)

            # 存储转换
            agent.store_transition(state, action, reward, next_state, done)
            agent.optimize_model()
            state = next_state
            total_reward += reward
        
        reward_list.append(total_reward)
        epsilon_list.append(agent.epsilon)
        loss_list.append(agent.loss_list[-1])

        if epoch % 10 == 0:
            agent.update_target_network()
            print(f"Epochs:{epoch}, Total reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")

    plot_single_curve(range(epochs), reward_list, "Total Reward Over Episodes", "Episodes", "Total Reward")
    plot_single_curve(range(epochs), epsilon_list, "Epsilon Over Episodes", "Episodes", "Epsilon", color="green")
    plot_single_curve(range(epochs), loss_list, "Loss Over Episodes", "Episodes", "Loss", color="red")

            

if __name__ == '__main__':
    serial_port = HardwareInterface(args.COM, args.baudrate)
    environment = TemperatureEnv(serial_port)
    dqn_agent = DQNAgent(environment, environment.state_space, environment.action_space, args.memory_capacity,
                         args.greedy_start, args.greedy_end, args.decay, args.discount, args.learning_rate,
                         args.batch_size)

    # Open the serial port first.
    serial_port.connect()

    main_train(dqn_agent, environment, args.Iterations)
