import time
import datetime
from collections import defaultdict
from pathlib import Path
from remoteConnect.socketClient import SocketClient
from remoteConnect.dataSaver import CSVDataSaver, RobotDataSaver
from fairino import Robot  # 假设机器人SDK模块


def collect_and_save_data():
    # ===================== 初始化连接 =====================
    # 测量系统客户端
    measurement_client = SocketClient("192.168.1.106", 5174)
    if not measurement_client.connect_to_server():
        print("测量系统连接失败")
        return

    # 机器人系统客户端
    try:
        robot_arm = Robot.RPC("192.168.57.2")
        print("机器人连接成功")
    except Exception as e:
        print(f"机器人连接失败: {str(e)}")
        measurement_client.close_connection()
        return

    # ===================== 初始化存储器 =====================
    cam_saver = CSVDataSaver("../Data/pointsInCam.csv")
    robot_saver = RobotDataSaver("../Data/pointsInRobot.csv")

    # ===================== 数据收集 =====================
    all_points = []  # 测量点数据缓存
    all_robot_poses = []  # 机器人位姿数据缓存
    start_time = time.time()

    while (elapsed := time.time() - start_time) < 5:
        # 收集测量系统数据
        if measurement_client.receive_data():
            all_points.extend(measurement_client.get_measure_points())

        # 收集机器人数据（每秒约10次采样）
        if elapsed % 0.1 < 0.01:  # 控制采样频率
            try:
                ret = robot_arm.GetActualToolFlangePose()
                if ret[0] == 0:
                    all_robot_poses.append(ret[1])
                else:
                    print(f"机器人数据错误码: {ret[0]}")
            except Exception as e:
                print(f"机器人通信异常: {str(e)}")

    # ===================== 数据处理 =====================
    timestamp = datetime.datetime.now().isoformat()

    # 处理测量系统数据
    if all_points:
        id_groups = defaultdict(list)
        for p in all_points:
            id_groups[p.ID].append(p)

        averages = {
            id: {
                'X': sum(p.X for p in pts) / len(pts),
                'Y': sum(p.Y for p in pts) / len(pts),
                'Z': sum(p.Z for p in pts) / len(pts)
            }
            for id, pts in id_groups.items()
        }
        cam_saver.save_averages(averages, timestamp)
    else:
        print("测量系统无有效数据")

    # 处理机器人数据
    if all_robot_poses:
        robot_avg = {
            'x': sum(p[0] for p in all_robot_poses) / len(all_robot_poses),
            'y': sum(p[1] for p in all_robot_poses) / len(all_robot_poses),
            'z': sum(p[2] for p in all_robot_poses) / len(all_robot_poses),
            'rx': sum(p[3] for p in all_robot_poses) / len(all_robot_poses),
            'ry': sum(p[4] for p in all_robot_poses) / len(all_robot_poses),
            'rz': sum(p[5] for p in all_robot_poses) / len(all_robot_poses)
        }
        robot_saver.save_robot_averages(robot_avg, timestamp)
    else:
        print("机器人无有效数据")

    # ===================== 清理连接 =====================
    measurement_client.close_connection()
    print("数据采集完成")


if __name__ == "__main__":
    collect_and_save_data()