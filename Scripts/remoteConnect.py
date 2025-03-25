"""
脚本名称: remoteConnect.py
脚本功能: 此脚本用于建立与远程服务器的连接，接收服务器发送的数据，
          并允许用户通过按Enter键保存当前测量点位的数据，同时支持安全退出。
主要组件:
  - SocketClient: 负责与远程服务器建立连接、接收数据以及获取测量点位信息。
  - DataSaver: 负责将测量点位数据保存到本地。
主要流程:
  1. 初始化SocketClient和DataSaver对象。
  2. 尝试连接到指定的远程服务器。
  3. 若连接成功，启动一个后台线程用于持续接收服务器数据。
  4. 在主线程中等待用户输入，用户按Enter键时保存当前测量点位数据，按Ctrl+C时安全退出。
  5. 退出时关闭与服务器的连接。
注意事项:
  - 服务器的IP地址和端口号在代码中硬编码为 "192.168.1.104" 和 5174，可根据实际情况修改。
  - 仅显示ID范围在101到112之间的测量点位信息。
"""
from remoteConnect.socketClient import SocketClient
from remoteConnect.dataSaver import DataSaver
import sys
import threading

# 全局标志，用于控制线程运行
running = True


def receive_data(client):
    """静默接收数据，不进行显示"""
    global running
    while running:
        client.receive_data()  # 仅接收数据不显示


def input_handler(client, saver):
    global running
    try:
        while running:
            input("\n>>> 按Enter保存当前点位 | Ctrl+C退出 → ")

            # 获取并显示当前点位
            current_points = client.get_measure_points()
            display_current_points(current_points)

            # 保存数据
            saver.save_case(current_points)
            print("✓ 保存成功")

    except KeyboardInterrupt:
        running = False
        print("\n客户端安全关闭")


def main():
    client = SocketClient("192.168.1.104", 5174)
    saver = DataSaver()

    if not client.connect_to_server():
        print("× 服务器连接失败")
        sys.exit(1)

    # 启动后台数据接收线程
    receive_thread = threading.Thread(target=receive_data, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    # 直接在主线程处理输入
    input_handler(client, saver)

    client.close_connection()


def display_current_points(points):
    """按需显示点位信息"""
    valid_points = sorted(
        [p for p in points if 101 <= p.ID <= 112],
        key=lambda x: x.ID
    )

    print("\n当前保存点位：")
    for p in valid_points:
        print(f"ID {p.ID}: "
              f"X={p.X:.4f} Y={p.Y:.4f} Z={p.Z:.4f}")
    print("-" * 40)  # 分隔线


if __name__ == "__main__":
    main()
    if sys.platform == "win32":
        input("按Enter退出...")