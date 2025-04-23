%% SVD ����ת�ƾ���
clc, clear;
% Sheet alignFrom ��Ϊԭʼ����
alignFrom = readmatrix("../Data/Data_01.xlsx", 'Sheet', 'alignFrom');
% Sheet alignTo   ��Ϊ�������
alignTo = readmatrix("../Data/Data_01.xlsx", 'Sheet', 'alignTo');

%% ����ת�ƾ���
[A, T, error, alignedShape] = AlignShapesWithScale(alignFrom, alignTo);

%% ����
error_input = alignFrom';
error_output = (A * error_input + T')';

%% �������
% �����ֵ����
diff_matrix = error_output - alignTo;

% ����ÿ�е�2-��������
errors = sqrt(sum(diff_matrix.^2, 2)); % ����ʹ�� vecnorm(diff_matrix, 2, 2)

% ��ͳ����
max_error = max(errors);
min_error = min(errors);
mean_error = mean(errors);

% ������
fprintf('������: %.4f mm \n', max_error);
fprintf('��С���: %.4f mm \n', min_error);
fprintf('ƽ�����: %.4f mm \n', mean_error);

%% ��ȡ�������ϵ��ģ������㣺
input = readmatrix("../Data/ģ�߱�־��_FrameCam_average.csv");
output = (A * input' + T')';