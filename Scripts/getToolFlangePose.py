"""
机器人末端位姿记录脚本
功能：连接机器人并加载校准程序，手动触发保存末端法兰位姿数据（含ISO8601时间戳）
交互逻辑：
  1. 启动自动模式后需人工确认程序名称
  2. 每次按Enter记录当前时刻的位姿数据
  3. Ctrl+C中断时自动切回手动模式
数据格式：CSV文件包含时间戳(X,Y,Z,RotX,RotY,RotZ)
输出路径：..\Data\机器人末端轨迹点测试.csv
依赖配置：需提前部署/fruser/calibration.lua程序文件
"""
from fairino import Robot
import csv
import datetime

# 连接机器人
robot = Robot.RPC("192.168.57.2")

# 机器人切入自动运行模式
robot.Mode(0)
# 加载要执行的机器人程序
ret = robot.ProgramLoad('/fruser/calibration.lua')

# 查询已加载的作业程序名
name = robot.GetLoadedProgram()
print("当前加载程序为：", name[1])

try:
    # 等待用户确认
    input("请确认程序名正确，按Enter键继续运行程序...")
except KeyboardInterrupt:
    robot.Mode(1)
    print("\n用户取消操作，程序终止")
    exit()

robot.ProgramRun()  # 执行机器人程序

# 打开CSV文件以写入数据
csv_file_path = r"..\Data\机器人末端轨迹点测试.csv"
with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # 写入CSV文件的表头
    csv_writer.writerow(['Timestamp', 'X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ'])

    try:
        while True:
            input("按下Enter键保存当前位姿，按Ctrl+C停止...")  # 等待用户输入
            # 获取当前时间戳（ISO 8601格式）
            timestamp = datetime.datetime.now().isoformat()
            # 获取当前末端法兰位姿
            ret = robot.GetActualToolFlangePose()
            pose_data = ret[1]
            print("获取当前末端法兰位姿", pose_data)
            # 合并时间戳和位姿数据
            row_data = [timestamp] + pose_data
            # 将数据写入CSV文件
            csv_writer.writerow(row_data)
    except KeyboardInterrupt:
        # 机器人切入手动模式
        robot.Mode(1)
        print("\n机器人进入手动模式 程序已停止")
