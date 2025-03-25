import socket
import struct
import time
from dataclasses import dataclass
from typing import List


@dataclass
class MeasurePoint:
    ID: int
    X: float
    Y: float
    Z: float
    dx: float
    dy: float
    dz: float
    dw: float


class SocketClient:
    def __init__(self, ip: str, port: int):
        self.server_ip = ip
        self.server_port = port
        self.sock = None
        self.measure_points: List[MeasurePoint] = []

    def connect_to_server(self) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # 添加5秒超时
            self.sock.connect((self.server_ip, self.server_port))
            print("Connected to the server!")
            return True
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Connection failed: {str(e)}")
            return False

    def receive_data(self) -> bool:
        try:
            buffer = self.sock.recv(2048)
            if not buffer:
                print("Connection lost. Attempting to reconnect...")
                return self.try_reconnect()
            return self.unpack_data(buffer)
        except socket.timeout:
            print("Receive timeout")
            return True  # 保持连接
        except Exception as e:
            print(f"Receive error: {str(e)}")
            return False

    def unpack_data(self, data: bytes) -> bool:
        if len(data) < 10:
            return False

        # 校验头和尾
        if data[0] != 0x55 or data[1] != 0xAA or data[-2] != 0xAA or data[-1] != 0x55:
            return False

        try:
            num_points = struct.unpack('<H', data[2:4])[0]
            index = 4
            self.measure_points.clear()

            for _ in range(num_points):
                if index + 30 > len(data):
                    break

                point = MeasurePoint(
                    ID=struct.unpack('<H', data[index:index + 2])[0],
                    X=struct.unpack('<f', data[index + 2:index + 6])[0],
                    Y=struct.unpack('<f', data[index + 6:index + 10])[0],
                    Z=struct.unpack('<f', data[index + 10:index + 14])[0],
                    dx=struct.unpack('<f', data[index + 14:index + 18])[0],
                    dy=struct.unpack('<f', data[index + 18:index + 22])[0],
                    dz=struct.unpack('<f', data[index + 22:index + 26])[0],
                    dw=struct.unpack('<f', data[index + 26:index + 30])[0]
                )
                self.measure_points.append(point)
                index += 30
            return True
        except struct.error as e:
            print(f"Unpack error: {str(e)}")
            return False

    def try_reconnect(self) -> bool:
        self.close_connection()
        for attempt in range(5):
            print(f"Reconnect attempt {attempt + 1}/5")
            if self.connect_to_server():
                return True
            time.sleep(2)
        return False

    def close_connection(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Connection closed")

    def get_measure_points(self) -> List[MeasurePoint]:
        return self.measure_points.copy()  # 返回副本保证数据安全