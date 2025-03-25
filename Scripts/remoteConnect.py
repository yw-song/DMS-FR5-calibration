from remoteConnect.socketClient import SocketClient
from remoteConnect.dataSaver import DataSaver
import sys
import threading

# Windows启用ANSI转义码支持
if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# 全局标志，用于控制线程运行
running = True
# 输出锁防止打印冲突
print_lock = threading.Lock()


def receive_data(client):
    global running
    while running:
        if client.receive_data():
            display_current_points(client)


def input_handler(client, saver):
    global running
    while running:
        try:
            with print_lock:
                # 移动光标到输入区域并显示提示
                print("\033[20;1H>>> 按Enter保存当前点位 | Ctrl+C退出 → ", end="")
                sys.stdout.flush()
                input()
            current_points = client.get_measure_points()
            saver.save_case(current_points)
        except KeyboardInterrupt:
            running = False
            print("\n客户端安全关闭")


def main():
    client = SocketClient("192.168.1.104", 5174)
    saver = DataSaver()

    if not client.connect_to_server():
        print("× 服务器连接失败")
        sys.exit(1)

    receive_thread = threading.Thread(target=receive_data, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    input_thread = threading.Thread(target=input_handler, args=(client, saver))
    input_thread.daemon = True
    input_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n客户端安全关闭")
    finally:
        client.close_connection()


def display_current_points(client):
    with print_lock:
        points = client.get_measure_points()
        valid_points = sorted(
            [p for p in points if 101 <= p.ID <= 112],
            key=lambda x: x.ID
        )

        # 更新数据区域
        print("\033[1;1H")  # 光标移动到左上角
        print("当前点位状态：")
        for p in valid_points:
            print(f"ID {p.ID}: X={p.X:.4f} Y={p.Y:.4f} Z={p.Z:.4f}")
        print("\033[J")  # 清除后续残留内容

        # 确保输入提示可见
        print("\033[20;1H>>> 按Enter保存当前点位 | Ctrl+C退出 → ", end="")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
    if sys.platform == "win32":
        input("按Enter退出...")
