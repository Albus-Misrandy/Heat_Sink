import argparse
import numpy as np
from utils.plot_function import *
from Serial_Port.SerialPort import HardwareInterface

parser = argparse.ArgumentParser(description="Data Collection.")

parser.add_argument("--baudrate", type=int, default=115200, help="The baudrate of the serial port.")
parser.add_argument("--COM", type=str, default='COM6', help="The number of the serial port com.")

args = parser.parse_args()

if __name__ == '__main__':
    collector = HardwareInterface(args.COM, args.baudrate)
    collector.connect()
    plt_t = []
    plt_T = []
    plt_dT = []
    while True:
        # collector.send_float_data(2)
        data = collector.read_sensor()
        if data != None:
            if data[0] == 20:
                break
            plt_t.append(data[0])
            plt_T.append(data[1])
            plt_dT.append(data[2])
        else:
            continue

    data_to_csv(plt_t, plt_T, plt_dT)
    
    plot_single_curve(plt_t, plt_T, "T-t plot", "t/s", "T/°c")
    plot_muti_curve([plt_t, plt_t], [plt_T, plt_dT], "Temperature and Derivative", "t", "T & dT/dt")
