"""
实现功能：
    - 读取多个 Excel 文件中的变换矩阵数据
    - 利用 OpenCV 提供的多种手眼标定方法来计算机械臂基座（base）到相机（camera）的变换矩阵
"""
import cv2
import numpy as np
import pandas as pd


def read_transform_matrices(file_path, invert=False):
    """读取矩阵并可选求逆"""
    sheets = pd.read_excel(file_path, sheet_name=None, header=None)
    matrices = {}
    for sheet_name, df in sheets.items():
        matrix = df.iloc[:4, :4].values.astype(np.float64)
        if invert:
            matrix = np.linalg.inv(matrix)  # 正确求逆
        matrices[sheet_name] = matrix
    return matrices


# 读取数据
gripper2base = read_transform_matrices('../Data/gripper2Base.xlsx', invert=False)  # 读取 gripper2bae
base2gripper = read_transform_matrices('../Data/base2Gripper.xlsx', invert=False)  # 读取 base2gripper
target2cam = read_transform_matrices('../Data/points.xlsx', invert=False)      # 读取 target2cam
cam2target = read_transform_matrices('../Data/target2Cam.xlsx', invert=True)       # 读取 cam2target

# 确保数据顺序一致
assert gripper2base.keys() == target2cam.keys(), "Sheet名称或数量不匹配"
cases = list(gripper2base.keys())

# 准备标定数据
R_base2gripper, t_base2gripper = [], []
R_gripper2base, t_gripper2base = [], []
R_target2cam, t_target2cam = [], []
R_cam2target, t_cam2target = [], []

for case in cases:
    # 处理机械臂数据（直接读取base2gripper）
    bg_mat = base2gripper[case]
    R_base2gripper.append(bg_mat[:3, :3])
    t_base2gripper.append(bg_mat[:3, 3])

    # 处理机械臂数据（直接读取gripper2base）
    gb_mat = gripper2base[case]
    R_gripper2base.append(gb_mat[:3, :3])
    t_gripper2base.append(gb_mat[:3, 3])

    # 处理视觉数据（直接读取target2cam）
    tc_mat = target2cam[case]
    R_target2cam.append(tc_mat[:3, :3])
    t_target2cam.append(tc_mat[:3, 3])

    # 处理视觉数据（直接读取target2cam）
    ct_mat = cam2target[case]
    R_cam2target.append(ct_mat[:3, :3])
    t_cam2target.append(ct_mat[:3, 3])

# 执行手眼标定
methods = [
    cv2.CALIB_HAND_EYE_TSAI,
    cv2.CALIB_HAND_EYE_PARK,
    cv2.CALIB_HAND_EYE_HORAUD,
    cv2.CALIB_HAND_EYE_ANDREFF
]

for method in methods:
    R, t = cv2.calibrateHandEye(
        R_gripper2base=R_base2gripper,
        t_gripper2base=t_base2gripper,
        R_target2cam=R_target2cam,
        t_target2cam=t_target2cam,
        method=method
    )
    print(f"Method: {method}")
    # 组合成4x4变换矩阵
    transform = np.eye(4)
    transform[:3, :3] = R
    transform[:3, 3] = t.flatten()

    print("标定结果：基座到相机的变换矩阵（base to camera）")
    print("旋转矩阵 R:\n", R)
    print("平移向量 t:\n", t)
    print("\n完整的4x4变换矩阵:\n", transform)
