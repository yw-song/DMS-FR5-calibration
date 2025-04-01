%% ԭʼ����
% alignFrom=[22.818719,33.685246,20;
%     31.141877,32.910819,20;
%     69.637997,30.801305,20;
%     79.849429,30.456253,20];
% alignTo=[535.301103,855.577028,3.718971;
%    543.659983,855.638810,3.722900;
%    582.174082,857.389531,3.743062;
%    592.368832,858.067365,3.748700];

%% ��ȡ�ĵ�
clc, clear;
% Sheet alignFrom ��Ϊԭʼ����
alignFrom = readmatrix("Data_01.xlsx", 'Sheet', 'alignFrom');
% Sheet alignTo   ��Ϊ�������
alignTo = readmatrix("Data_01.xlsx", 'Sheet', 'alignTo');

%% ����ת�ƾ���
[A, T, error, alignedShape] = AlignShapesWithScale(alignFrom, alignTo);

%% ����
% i,j,kֱ��A*;x,y,z��A* +T
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

%% �������
% �����ֵ����
diff_matrix = output - alignTo;

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
