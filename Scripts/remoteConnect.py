"""
实现功能：
    - 初始化 SocketClient 对象 client，指定服务器的 IP 地址（192.168.1.104）和端口号（5174）
      同时初始化 DataSaver 对象 saver。
    - 调用 client.connect_to_server() 方法尝试连接到服务器，如果连接失败，打印错误信息并退出程序。
    - 创建一个新的线程 input_thread，该线程的目标函数是 input_handler，并将 client 和 saver 作为参数传递给它。
      将该线程设置为守护线程，意味着主线程退出时，该线程也会自动退出。
    - 进入一个无限循环，不断调用 client.receive_data() 方法接收服务器发送的数据。
      如果接收到数据，则调用 display_current_points 函数显示当前点位信息。
    - 当用户按下 Ctrl+C 时，捕获 KeyboardInterrupt 异常，打印关闭信息，
      并在 finally 块中调用 client.close_connection() 方法关闭与服务器的连接。

"""
from remoteConnect.socketClient import SocketClient
from remoteConnect.dataSaver import DataSaver
import sys
import threading


def main():
    # 初始化组件
    client = SocketClient("192.168.1.104", 5174)
    saver = DataSaver()     # 实例化 DataSaver 对象

    if not client.connect_to_server():
        print("× 服务器连接失败")
        sys.exit(1)

    # 启动独立输入线程
    input_thread = threading.Thread(
        target=input_handler,
        args=(client, saver),
        daemon=True
    )
    input_thread.start()

    try:
        while True:
            if client.receive_data():
                display_current_points(client)
            pass
    except KeyboardInterrupt:
        print("\n客户端安全关闭")
    finally:
        client.close_connection()


def input_handler(client, saver):
    """专用输入处理线程"""
    while True:
        input("\n>>> 按Enter保存当前点位 | Ctrl+C退出 → ")
        current_points = client.get_measure_points()
        saver.save_case(current_points)


def display_current_points(client):
    """实时数据显示"""
    points = client.get_measure_points()
    valid_points = sorted(
        [p for p in points if 101 <= p.ID <= 112],
        key=lambda x: x.ID
    )

    print("\n当前点位状态：")
    for p in valid_points:
        print(f"ID {p.ID}: "
              f"X={p.X:.4f} Y={p.Y:.4f} Z={p.Z:.4f}")


if __name__ == "__main__":
    main()
    if sys.platform == "win32":
        input("按Enter退出...")
