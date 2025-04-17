import argparse
import numpy as np

parser = argparse.ArgumentParser(description="Q Learning of Heat Sink.")

parser.add_argument("--Iterations", type=int, default=100, help="Training iterations.")
parser.add_argument("--learning_rate", type=float, default=0.001, help="Value of Alpha.")
parser.add_argument("--discount", type=float, default=0.9, help="Value of gamma.")
parser.add_argument("--batch_size", type=int, default=64, help="Value of batch size")
parser.add_argument("--decay", type=float, default=0.995, help="Value of decay")

args = parser.parse_args()


def main_train(epochs):
    epochs_rewards = []
    success_rates = []

    for epoch in range(epochs):
        total_reward = 0
        done = False
        success = False
