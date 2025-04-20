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
                print(f"Receive: x={t:.4f}, y={T:.4f}, z={dT:.4f}")
                return data_list
            else:
                print(f"Data is not completed, only receive {len(data)} bytes")

    def send_float_data(self, value):
        if self.ser is not None:
            data_bytes = struct.pack('<f', value)
            self.ser.write(data_bytes)
            if self.ser.in_waiting > 0:
                received_data = self.ser.readline().decode('utf-8').strip()
                print(f"收到响应: {received_data}")
        else:
            print("Data could not send!")

    # def check_available(self):
    #     ports = serial.tools.list_ports.comports()
    #     print("Availabel USB Port:")
    #     for port in ports:
    #         print(port.device)

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"Connected to {self.ser.name}，Waiting for data...")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise
