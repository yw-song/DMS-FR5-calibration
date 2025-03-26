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
base2gripper = read_transform_matrices('../Data/base2Gripper.xlsx', invert=False)  # 读取 base2gripper
target2cam = read_transform_matrices('../Data/target2Cam.xlsx', invert=False)  # 读取 target2cam

# 确保数据顺序一致
assert base2gripper.keys() == target2cam.keys(), "Sheet名称或数量不匹配"
cases = list(base2gripper.keys())

# 准备标定数据
R_base2gripper, t_base2gripper = [], []
R_target2cam, t_target2cam = [], []

for case in cases:
    # 处理机械臂数据（直接读取base2gripper）
    bg_mat = base2gripper[case]
    R_base2gripper.append(bg_mat[:3, :3])
    t_base2gripper.append(bg_mat[:3, 3])

    # 处理视觉数据（直接读取target2cam）
    tc_mat = target2cam[case]
    R_target2cam.append(tc_mat[:3, :3])
    t_target2cam.append(tc_mat[:3, 3])

# 执行手眼标定
methods = [
    cv2.CALIB_HAND_EYE_TSAI,
    cv2.CALIB_HAND_EYE_PARK,
    cv2.CALIB_HAND_EYE_HORAUD,
    cv2.CALIB_HAND_EYE_ANDREFF
]

# 创建 ExcelWriter 对象
with pd.ExcelWriter("../Data/base2Cam.xlsx") as writer:
    for method in methods:
        R, t = cv2.calibrateHandEye(
            R_gripper2base=R_base2gripper,
            t_gripper2base=t_base2gripper,
            R_target2cam=R_target2cam,
            t_target2cam=t_target2cam,
            method=method
        )

        # 组合成4x4变换矩阵
        transform = np.eye(4)
        transform[:3, :3] = R
        transform[:3, 3] = t.flatten()

        # 将变换矩阵转换为 DataFrame 并写入 Excel
        sheet_name = f"method{method}"
        pd.DataFrame(transform).to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            header=False
        )

        # 精简版终端输出
        print(f"\nMethod: {method}")
        print("完整的4x4变换矩阵:")
        print(np.array2string(transform,
                              precision=4,  # 显示4位小数
                              suppress_small=True,  # 抑制科学计数法
                              formatter={'float_kind': "{:.4f}".format}
                              ))
        print(f"已写入工作表 [{sheet_name}]")

print("\n所有标定结果已保存至: ../Data/base2Cam.xlsx")
