import sys
import threading
import csv
import datetime
from remoteConnect.socketClient import SocketClient
from remoteConnect.dataSaver import DataSaver
from fairino import Robot

# 全局标志，用于控制线程运行
running = True


def receive_data(client):
    """持续接收网络数据"""
    global running
    while running:
        client.receive_data()


def input_handler(client, saver, robot, csv_writer, csv_file):
    """处理用户输入并执行双数据保存操作"""
    global running
    try:
        while running:
            input("\n>>> 按Enter同时保存点位和位姿 | Ctrl+C退出 → ")

            # 保存Socket数据
            current_points = client.get_measure_points()
            display_current_points(current_points)
            saver.save_case(current_points)
            print("✓ 测量点位保存成功")

            # 保存机器人位姿
            timestamp = datetime.datetime.now().isoformat()
            ret = robot.GetActualToolFlangePose()
            if ret[0] == 0:  # 假设返回码0表示成功
                pose_data = ret[1]
                row_data = [timestamp] + pose_data
                csv_writer.writerow(row_data)
                csv_file.flush()  # 确保数据写入磁盘
                print("✓ 机器人位姿保存成功")
            else:
                print(f"× 获取位姿失败，错误码：{ret[0]}")

    except KeyboardInterrupt:
        running = False
        print("\n安全终止程序...")


def display_current_points(points):
    """展示有效的测量点位信息"""
    valid_points = sorted(
        [p for p in points if 101 <= p.ID <= 112],
        key=lambda x: x.ID
    )
    print("\n当前有效点位：")
    for p in valid_points:
        print(f"ID {p.ID}: X={p.X:.4f} Y={p.Y:.4f} Z={p.Z:.4f}")
    print("-" * 40)


def main():
    global running

    # 初始化测量系统
    measurement_client = SocketClient("192.168.1.104", 5174)
    data_saver = DataSaver()

    if not measurement_client.connect_to_server():
        print("× 测量系统连接失败")
        sys.exit(1)

    # 初始化机器人系统
    robot_arm = Robot.RPC("192.168.57.2")
    robot_arm.Mode(0)  # 切入自动模式

    # 加载机器人程序
    if robot_arm.ProgramLoad('/fruser/calibration.lua') != 0:
        print("× 机器人程序加载失败")
        robot_arm.Mode(1)
        sys.exit(1)

    # 验证加载程序
    program_info = robot_arm.GetLoadedProgram()
    print("当前加载程序：", program_info[1])

    try:
        input("请确认程序名称，按Enter开始执行 → ")
    except KeyboardInterrupt:
        robot_arm.Mode(1)
        print("\n用户取消操作")
        sys.exit(0)

    # 启动机器人程序
    robot_arm.ProgramRun()

    # 初始化数据记录文件
    csv_path = r"..\Data\gripperPose.csv"
    with open(csv_path, 'w', newline='') as csv_fd:
        csv_writer = csv.writer(csv_fd)
        csv_writer.writerow(['时间戳', 'X', 'Y', 'Z', 'Rx', 'Ry', 'Rz'])

        # 启动数据接收线程
        data_thread = threading.Thread(target=receive_data, args=(measurement_client,))
        data_thread.daemon = True
        data_thread.start()

        try:
            input_handler(measurement_client, data_saver, robot_arm, csv_writer, csv_fd)
        finally:
            running = False
            measurement_client.close_connection()
            robot_arm.Mode(1)  # 切回手动模式
            print("所有连接已安全关闭")


if __name__ == "__main__":
    main()
    if sys.platform == "win32":
        input("按Enter退出...")