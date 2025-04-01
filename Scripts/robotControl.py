"""
实现的功能：
 - 与机械臂进行通信
 - 移动到 pose1
"""
from fairino import Robot

robot = Robot.RPC("192.168.57.2")
ret, version = robot.GetSDKVersion()  # 查询SDK版本号
if ret == 0:
    print("SDK版本号为", version)
else:
    print("查询失败，错误码为", ret)

desc_pos1 = [-499.518221, 351.323714, 80.0000, 26.138206481933594, 1.4802045822143555, -130.331298828125]  # 笛卡尔空间坐标
tool = 0  # 工具坐标系编号
user = 0  # 工件坐标系编号
ret = robot.MoveL(desc_pos1, tool, user)  # 笛卡尔空间直线运动

ret = robot.GetActualToolFlangePose()
print("获取当前关节位置 (角度)", ret)

