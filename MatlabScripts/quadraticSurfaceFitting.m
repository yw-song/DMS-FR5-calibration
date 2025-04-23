%% 二次曲面拟合
clear; close all; clc;

% 文件提取路径
csv_file = '..\Data\模具标志点_FrameRobot_average.csv';

% 读取 CSV 文件并保留原始列标题
data = readtable(csv_file, 'VariableNamingRule', 'preserve');

% 提取点的名称和坐标
P = readmatrix(csv_file);

x_coords = P(:, 2);
y_coords = P(:, 3);
z_coords = P(:, 4);

% 绘图
figure;
plot3(x_coords, y_coords, z_coords, 'o');
% 设置坐标轴标签
xlabel('X Coordinate (mm)');
ylabel('Y Coordinate (mm)');
zlabel('Z Coordinate (mm)');

%% 求解矩阵
N = length(x_coords);
A=[N sum(y_coords) sum(x_coords) sum(x_coords.*y_coords) sum(y_coords.^2) sum(x_coords.^2);
   sum(y_coords) sum(y_coords.^2) sum(x_coords.*y_coords) sum(x_coords.*y_coords.^2) sum(y_coords.^3) sum(x_coords.^2.*y_coords);
   sum(x_coords) sum(x_coords.*y_coords) sum(x_coords.^2) sum(x_coords.^2.*y_coords) sum(x_coords.*y_coords.^2) sum(x_coords.^3);
   sum(x_coords.*y_coords) sum(x_coords.*y_coords.^2) sum(x_coords.^2.*y_coords) sum(x_coords.^2.*y_coords.^2) sum(x_coords.*y_coords.^3) sum(x_coords.^3.*y_coords);
   sum(y_coords.^2) sum(y_coords.^3) sum(x_coords.*y_coords.^2) sum(x_coords.*y_coords.^3) sum(y_coords.^4) sum(x_coords.^2.*y_coords.^2);
   sum(x_coords.^2) sum(x_coords.^2.*y_coords) sum(x_coords.^3) sum(x_coords.^3.*y_coords) sum(x_coords.^2.*y_coords.^2) sum(x_coords.^4)];
B=[sum(z_coords) sum(z_coords.*y_coords) sum(z_coords.*x_coords) sum(z_coords.*x_coords.*y_coords) sum(z_coords.*y_coords.^2) sum(z_coords.*x_coords.^2)]';
C = A \ B;

% 拟合一个曲面，xy 的范围是坐标值的最小值与最大值
x_grid = min(x_coords) : 5 : max(x_coords);
y_grid = min(y_coords) : 5 : max(y_coords);
[x, y] = meshgrid(x_grid, y_grid);
z = C(6) * x.^2 + C(5) * y.^2 + C(4) * x.*y + C(3) * x+ C(2) * y + C(1);    %拟合结果

hold on;
mesh(x, y, z)

%% 求解使得 z 轴最大的点坐标
% 找出 z 矩阵中的最大值及其对应的线性索引
[max_z, max_index] = max(z(:));

% 将线性索引转换为二维索引
[max_row, max_col] = ind2sub(size(z), max_index);

% 根据二维索引从 x 和 y 矩阵中获取对应的 x 和 y 值
max_x = x(max_row, max_col);

max_y = y(max_row, max_col);

% 转换坐标
max_point = [max_x; max_y; max_z];
R = [-0.755303143870368	0.647496950522556	-0.122665893338629
-0.625815722739923	-0.646247452300571	0.442154919718828
0.206528214769993	0.409748692400655	0.891198163735153];
t = [-504.253127868763	983.664732091453	797.939512808951];
point = R \ (max_point - t);

%% 计算 z 与 z_coords 的误差

% 根据x_coords和y_coords计算拟合的z值
z_fit = C(6) * x_coords.^2 + C(5) * y_coords.^2 + C(4) * x_coords.*y_coords + C(3) * x_coords + C(2) * y_coords + C(1);

% 计算均方误差 (MSE)
mse = mean((z_fit - z_coords).^2);

% 计算均方根误差 (RMSE)
rmse = sqrt(mse);

% 计算平均绝对误差 (MAE)
mae = mean(abs(z_fit - z_coords));

% 显示结果
fprintf('均方误差 (MSE): %.4f\n', mse);
fprintf('均方根误差 (RMSE): %.4f\n', rmse);
fprintf('平均绝对误差 (MAE): %.4f\n', mae);
