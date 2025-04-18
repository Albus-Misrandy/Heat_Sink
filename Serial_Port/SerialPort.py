import serial
import struct
import time


class HardwareInterface:
    def __init__(self, port=None, baudrate=115200):
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        # self.connect()

    """读取温度和导数数据包"""
    def read_sensor(self):
        if self.ser is not None:
            data = self.ser.read(12)
            if len(data) == 12:
                # 将字节转换为3个float
                # '<'表示小端字节序，'fff'表示3个float
                T, dT, t = struct.unpack('<fff', data)
                data_list = [T, dT, t]
                print(f"Receive: x={T:.4f}, y={dT:.4f}, z={t:.4f}")
                return data_list
            else:
                print(f"Data is not completed, only receive {len(data)} bytes")

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"Connected to {self.ser.name}，Waiting for data...")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise
