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
                t, T, dT = struct.unpack('<fff', data)
                data_list = [t, T, dT]
                print(f"Receive: t={t:.4f}, T={T:.4f}, dT={dT:.4f}")
                return data_list
            else:
                print(f"Data is not completed, only receive {len(data)} bytes")

    def send_float_data(self, value):
        if self.ser is not None:
            data_bytes = str(value)
            self.ser.write((data_bytes + '\n').encode('utf-8'))
            print(f"已发送: {data_bytes}")
            # if self.ser.in_waiting > 0:
            #     received_data = self.ser.readline().decode('utf-8').strip()
            #     print(f"收到响应: {received_data}")
        else:
            print("Data could not send!")

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"Connected to {self.ser.name}，Waiting for data...")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise
