import argparse
import torch
from Serial_Port.SerialPort import HardwareInterface
from Environment.environment import TemperatureEnv
from Agent.Agent import DQNAgent
from utils.plot_function import *

parser = argparse.ArgumentParser(description="Q Learning of Heat Sink.")

parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate of the serial port.")
parser.add_argument("--COM", type=str, default='COM6', help="The number of the serial port com.")
parser.add_argument("--Iterations", type=int, default=100, help="Training iterations.")
parser.add_argument("--learning_rate", type=float, default=0.001, help="Value of Alpha.")
parser.add_argument("--discount", type=float, default=0.9, help="Value of gamma.")
parser.add_argument("--batch_size", type=int, default=64, help="Value of batch size")
parser.add_argument("--decay", type=float, default=0.995, help="Value of decay")
parser.add_argument("--memory_capacity", type=int, default=100, help="Memory of capacity.")
parser.add_argument("--greedy_start", type=float, default=1.0, help="Initial exploration rate.")
parser.add_argument("--greedy_end", type=float, default=0.9, help="Minimum exploration rate.")

args = parser.parse_args()


def main_train(agent, env, epoch, serial, reward_list, epsilon_list, loss_list):         
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        action = agent.select_action(state)
        next_state, reward, done, _ = env.step(action)
        print(env.time)
        # state = torch.tensor(state, dtype=torch.float32)

        # 存储转换
        agent.store_experience(state, action, reward, next_state, done)
        agent.train()
        state = next_state
        total_reward += reward

    reward_list.append(total_reward)
    epsilon_list.append(agent.epsilon)
    loss_list.append(agent.loss_list[-1])
    print(f"Epoch:{epoch}, Loss:{agent.loss_list[-1]}")

    agent.update_target_network()
    print(f"Epochs:{epoch}, Total reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")
    return reward_list, epsilon_list, loss_list


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    serial_port = HardwareInterface(args.COM, args.baudrate)
    environment = TemperatureEnv(serial_port)
    dqn_agent = DQNAgent(device, environment.state_space, environment.action_space, args.batch_size,
                         args.discount, args.greedy_start, args.greedy_end)

    # Open the serial port first.
    serial_port.connect()

    reward_list = []
    epsilon_list = []
    loss_list = []

    for epoch in range(args.Iterations):
        while True:
            user_input = input(f"按下 'y' 或'a'开始第 {epoch} 轮训练，或按其他键退出程序: ")
            if user_input.lower() == 'y':
                break
            elif user_input.lower() == 'a':
                serial_port.send_float_array([1, 0, 0, 0])
                break
            elif user_input.lower() in ['q', 'exit']:
                print("退出训练。")
                break
            else:
                print("请输入 'y' 来开始，或 'q' 退出。")
        environment.time = 0
        main_train(dqn_agent, environment, args.Iterations, serial_port, reward_list, epsilon_list, loss_list)

    # plot_single_curve(range(epochs), reward_list, "Total Reward Over Episodes", "Episodes", "Total Reward")
    # plot_single_curve(range(epochs), epsilon_list, "Epsilon Over Episodes", "Episodes", "Epsilon", color="green")
    # plot_single_curve(range(epochs), loss_list, "Loss Over Episodes", "Episodes", "Loss", color="red")
