%% 输入四个点，随机生成在这几个点之内的点（20个）

% 输入四边形的四个顶点（按顺序排列，xyz坐标）
% 示例：梯形（z坐标相同，位于XY平面）
points = [-391.7252197265625, 514.4075927734375, 80;    % P1
          -502.1679382324219, 679.584228515625, 80;    % P2
          -684.9249877929688, 463.15460205078125, 80;    % P3
          -520.7676391601562, 315.8489990234375, 80];   % P4

% 提取xy坐标用于二维判断
x = points(:,1);
y = points(:,2);
z_value = points(1,3);  % 假设所有点z坐标相同

% 确定包围盒范围
x_min = min(x);
x_max = max(x);
y_min = min(y);
y_max = max(y);

% 预分配存储
random_points = zeros(20, 3);
count = 0;

% 生成随机点直到满足20个
while count < 20
    % 生成包围盒内的候选点
    x_rand = x_min + (x_max - x_min) * rand();
    y_rand = y_min + (y_max - y_min) * rand();
    
    % 判断是否在四边形内（inpolygon自动处理凸/凹）
    if inpolygon(x_rand, y_rand, x, y)
        count = count + 1;
        random_points(count, :) = [x_rand, y_rand, z_value];
    end
end

% 显示结果
disp('随机生成的内部点坐标：');
disp(random_points);