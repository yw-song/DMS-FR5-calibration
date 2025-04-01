%% 原始数据
% alignFrom=[22.818719,33.685246,20;
%     31.141877,32.910819,20;
%     69.637997,30.801305,20;
%     79.849429,30.456253,20];
% alignTo=[535.301103,855.577028,3.718971;
%    543.659983,855.638810,3.722900;
%    582.174082,857.389531,3.743062;
%    592.368832,858.067365,3.748700];

%% 读取文档
clc, clear;
% Sheet alignFrom 作为原始矩阵
alignFrom = readmatrix("Data_01.xlsx", 'Sheet', 'alignFrom');
% Sheet alignTo   作为输出矩阵
alignTo = readmatrix("Data_01.xlsx", 'Sheet', 'alignTo');

%% 计算转移矩阵
[A, T, error, alignedShape] = AlignShapesWithScale(alignFrom, alignTo);

%% 测试
% i,j,k直接A*;x,y,z则A* +T
% ijk1=[0,0,1]';
% ijk2=[-0.691203,0.571278,0.442583]';
% ijko1=A*ijk1;
% ijko2=A*ijk2;
% xyz=[22.818719,33.685246,20]';
% xyzo=A*xyz+T';
% oula=[116.815260,26.144288,180.000000];
% oula=pi/180*oula;

% input = readmatrix("Data_01.xlsx", 'Sheet', 'From');
input = alignFrom';
output = (A * input + T')';

%% 计算误差
% 计算差值矩阵
diff_matrix = output - alignTo;

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
