%% 计算手眼标定的转移矩阵的误差
clc, clear;

% 定义 Excel 文件路径
excel_file_b2c = "../Data/base2Cam.xlsx";
excel_file_b2g = "../Data/base2Gripper.xlsx";
excel_file_t2c = "../Data/target2Cam.xlsx";

% sheet 名称为 method0 method1 method2 method3
method = "method1";
T = readmatrix(excel_file_b2c, "Sheet", method);

% 结构体
cal_ans = struct();

% 定义 Case 的数量
num_cases = 10; 

for case_num = 1:num_cases
    % 定义工作表名称
    sheet_name = sprintf('Case%d', case_num);
    
    % 读取 Excel 文件
    try
        T_base2gripper = readmatrix(excel_file_b2g, 'Sheet', sheet_name);
        T_target2cam = readmatrix(excel_file_t2c, 'Sheet', sheet_name);
        fprintf('Case%d 数据读取成功\n', case_num);
    catch ME
        fprintf('出错: %s\n', ME.message);
    end

    % 计算中间矩阵
    cal_ans(case_num).matrix = T_base2gripper * T * T_target2cam;
end

% 获取数据数量
n = numel(cal_ans);

% 初始化误差矩阵
rotation_errors = zeros(n, n);  % 单位：度
translation_errors = zeros(n, n); % 单位：米

% 计算所有矩阵对之间的误差
for i = 1:n
    for j = 1:n
        if i == j
            % 自身比较误差为0
            rotation_errors(i,j) = 0;
            translation_errors(i,j) = 0;
        else
            % 提取两个变换矩阵
            T_i = cal_ans(i).matrix;
            T_j = cal_ans(j).matrix;
            
            % 计算相对变换矩阵
            T_rel = T_i \ T_j;  % 等价于 inv(T_i) * T_j
            
            % 计算旋转误差（角度差）
            R_rel = T_rel(1:3, 1:3);
            trace_R = trace(R_rel);
            
            % 数值稳定性处理
            % trace_R = max(min(trace_R, 3), -1);  % 保证值在[-1, 3]范围内
            angle_rad = acos((trace_R - 1)/2);   % 计算旋转角度（弧度）
            rotation_errors(i,j) = rad2deg(angle_rad);
            
            % 计算平移误差（欧氏距离）
            t_rel = T_rel(1:3, 4);
            translation_errors(i,j) = norm(t_rel);
        end
    end
end

% 统计结果（排除对角线）
mask = logical(triu(ones(n), 1));  % 取上三角（不包含对角线）

% 旋转误差统计
rot_err_values = rotation_errors(mask);
mean_rot = mean(rot_err_values);
max_rot = max(rot_err_values);
min_rot = min(rot_err_values);
std_rot = std(rot_err_values);

% 平移误差统计
trans_err_values = translation_errors(mask);
mean_trans = mean(trans_err_values);
max_trans = max(trans_err_values);
min_trans = min(trans_err_values);
std_trans = std(trans_err_values);

% 显示统计结果
fprintf('\n旋转误差统计（单位：度）:\n');
fprintf('平均值：%.4f°\t 最大值：%.4f°\t 最小值：%.4f°\t 标准差：%.4f°\n\n',...
        mean_rot, max_rot, min_rot, std_rot);

fprintf('平移误差统计（单位：毫米）:\n');
fprintf('平均值：%.6f mm\t 最大值：%.6f mm\t 最小值：%.6f mm\t 标准差：%.6f mm\n',...
        mean_trans, max_trans, min_trans, std_trans);

% 可视化误差分布（可选）
figure;
subplot(1,2,1)
histogram(rot_err_values, 20);
title('旋转误差分布');
xlabel('角度（度）');
ylabel('频数');

subplot(1,2,2)
histogram(trans_err_values, 20);
title('平移误差分布');
xlabel('距离（毫米）');
ylabel('频数');