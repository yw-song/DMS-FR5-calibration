%% 计算机械臂末端到机械臂基底的转移矩阵
clc, clear

% 读取机械臂末端姿态信息
csv_path = '../Data/gripperPose.csv';
Cases = readmatrix(csv_path);

% 循环处理每个 Case
for case_num = 1:length(Cases)
    % 提取当前 Case 的数据
    currentCase = Cases(case_num,:);
    
    % 角度转换为弧度
    RX_rad = deg2rad(currentCase(5));
    RY_rad = deg2rad(currentCase(6));
    RZ_rad = deg2rad(currentCase(7));
    
    % 提取位置数据
    X_mm = currentCase(2);
    Y_mm = currentCase(3);
    Z_mm = currentCase(4);
    
    % 由欧拉角计算转移矩阵
    eul = [RZ_rad RY_rad RX_rad];   % 欧拉角
    rotmZYX = eul2rotm(eul, 'ZYX'); % 旋转矩阵
    T = [X_mm; Y_mm; Z_mm];
    
    % gripper to base
    RT_g2b = [rotmZYX, T; 0, 0, 0, 1];
    % base to gripper
    RT_b2g = inv(RT_g2b);
    
    % 定义工作表名称
    sheetName = sprintf('Case%d', case_num);
    
    % 将矩阵写入 Excel 文件的相应工作表
    writematrix(RT_g2b, '../Data/gripper2Base.xlsx', 'Sheet', sheetName);
    writematrix(RT_b2g, '../Data/base2Gripper.xlsx', 'Sheet', sheetName);
    fprintf('Case%d 数据成功写入文件: %s\n', case_num, "gripper2Base.xlsx");
end