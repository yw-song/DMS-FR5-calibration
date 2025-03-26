%% 通过对应点云计算转移矩阵
function [R, t] = compute_rigid_transform(source_points, target_points)
    % SVD点云配准算法计算 R 和 t
    centroid_src = mean(source_points, 1);   % 计算质心 (1x3)
    centroid_tgt = mean(target_points, 1);   % 计算质心 (1x3)
    
    src_centered = source_points - centroid_src; % 去质心化 (Nx3)
    tgt_centered = target_points - centroid_tgt; % 去质心化 (Nx3)
    
    H = src_centered' * tgt_centered;        % 协方差矩阵 (3x3)
    [U, ~, V] = svd(H);                     % SVD分解
    
    R = V * U';                             % 计算旋转矩阵 (3x3)
    
    % 处理反射情况
    if det(R) < 0
        V(:,3) = -V(:,3);
        R = V * U';
    end
    
    t = centroid_tgt' - R * centroid_src';   % 计算平移向量 (3x1)
    t = t';                                  % 转换为行向量显示 (1x3)
end
%% 生成理论点坐标
function points = generate_calibration_points()
    % 生成示例标定板坐标
    [X,Y] = meshgrid(0:30:90, 0:30:90);      % 生成3x3网格
    points = [X(:), Y(:), zeros(numel(X),1)]; % 创建z=0的平面点
    points = points(1:12,:);                % 取前12个点 (12x3)
end

%% 主函数
% 生成标定板坐标系下的点（12x3）
clc,clear;
source_points = generate_calibration_points();

% 定义 Case 的数量
num_cases = 20; 

% 定义 Excel 文件路径
input_excel_file = "../Data/targetPoint.xlsx";
output_excel_file = "../Data/target2Cam.xlsx";

for case_num = 1:num_cases

    % 定义工作表名称
    sheet_name = sprintf('Case%d', case_num);
    
    % 读取 CSV 文件
    try
        target_table = readmatrix(input_excel_file, 'sheet', sheet_name);
        target_points = target_table(:, 2:4); % 提取 XYZ 列
    catch ME
        fprintf('读取 %s 时出错: %s\n', input_excel_file, ME.message);
        continue;
    end    
    
    % 检查点数量
    if size(source_points, 1) ~= size(target_points, 1)
        error('点数量不匹配: 理论点%d个，测量点%d个',...
              size(source_points, 1), size(target_points, 1));
    end
    
    % 计算变换矩阵
    [R, t] = compute_rigid_transform(source_points, target_points);
    
    % 结果输出
    disp(['Case', num2str(case_num), ' 旋转矩阵 R:']);
    disp(round(R, 4));
    disp(['Case', num2str(case_num), ' 平移向量 t (mm):']);
    disp(round(t(:)', 2)); % 显示为行向量
    
    % 验证变换误差
    transformed = (R * source_points') + t';
    transformed = transformed';
    errors = vecnorm(transformed - target_points, 2, 2);
    fprintf('\nCase%d 最大重投影误差: %.2f mm\n', case_num, max(errors));
    fprintf('Case%d 平均重投影误差: %.2f mm\n', case_num, mean(errors));
    
    % 关闭科学计数法输出
    format long g
    T = [R, t'; 0, 0, 0, 1];
    
    % 写入 Excel 中
    try
        writematrix(T, output_excel_file, 'Sheet', sheet_name);
        fprintf('Case%d 数据成功写入文件: %s, Sheet为：%s\n', case_num, output_excel_file, sheet_name);
        fprintf("------------------------------------------\n");
    catch ME
        fprintf('将 Case%d 数据写入 %s 时出错: %s\n', case_num, output_excel_file, ME.message);
    end
end