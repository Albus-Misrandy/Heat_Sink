import argparse
import numpy as np
import matplotlib.pyplot as plt
from Serial_Port.SerialPort import HardwareInterface

parser = argparse.ArgumentParser(description="Data Collection.")

parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate of the serial port.")
parser.add_argument("--COM", type=str, default='COM4', help="The number of the serial port com.")

args = parser.parse_args()

if __name__ == '__main__':
    collector = HardwareInterface('COM6', 115200)
    collector.connect()
    while True:
        data = collector.read_sensor()
