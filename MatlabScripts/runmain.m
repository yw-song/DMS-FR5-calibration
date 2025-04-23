%% SVD 计算转移矩阵
clc, clear;
% Sheet alignFrom 作为原始矩阵
alignFrom = readmatrix("../Data/Data_01.xlsx", 'Sheet', 'alignFrom');
% Sheet alignTo   作为输出矩阵
alignTo = readmatrix("../Data/Data_01.xlsx", 'Sheet', 'alignTo');

%% 计算转移矩阵
[A, T, error, alignedShape] = AlignShapesWithScale(alignFrom, alignTo);

%% 测试
error_input = alignFrom';
error_output = (A * error_input + T')';

%% 计算误差
% 计算差值矩阵
diff_matrix = error_output - alignTo;

% 计算每行的2-范数（误差）
errors = sqrt(sum(diff_matrix.^2, 2)); % 或者使用 vecnorm(diff_matrix, 2, 2)

% 求统计量
max_error = max(errors);
min_error = min(errors);
mean_error = mean(errors);

% 输出结果
fprintf('最大误差: %.4f mm \n', max_error);
fprintf('最小误差: %.4f mm \n', min_error);
fprintf('平均误差: %.4f mm \n', mean_error);

%% 提取相机坐标系下模具坐标点：
input = readmatrix("../Data/模具标志点_FrameCam_average.csv");
output = (A * input' + T')';