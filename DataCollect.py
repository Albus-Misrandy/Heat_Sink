import argparse
import numpy as np
from utils.plot_function import *
from Serial_Port.SerialPort import HardwareInterface

parser = argparse.ArgumentParser(description="Data Collection.")

parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate of the serial port.")
parser.add_argument("--COM", type=str, default='COM4', help="The number of the serial port com.")

args = parser.parse_args()

if __name__ == '__main__':
    collector = HardwareInterface(args.COM, args.baudrate)
    collector.connect()
    plt_t = []
    plt_T1 = []
    plt_dT1 = []
    plt_T2 = []
    plt_dT2 = []
    while True:
        data = collector.read_sensor_5bits()
        if data is not None:
            if data == [-1.0, -1.0, -1.0, -1.0, -1.0]:
                break
            plt_t.append(data[0])
            plt_T1.append(data[1])
            plt_dT1.append(data[2])
            plt_T2.append(data[3])
            plt_dT2.append(data[4])
        else:
            continue

    data_to_csv(plt_t, plt_T1, plt_dT1)

    # plot_single_curve(plt_t, plt_T1, "T-t plot", "t/s", "T/°c")
    plot_muti_curve([plt_t, plt_t], [plt_T1, plt_T2], "Temperature and Derivative", "t", "T & dT/dt")
