%% 计算时间维度下的平均坐标
% 定义文件路径
clc,clear;
file_path = fullfile('..', 'Data', 'ex02.xlsx');
output_csv = fullfile('..', 'Data', '模具标志点_FrameCam_average.csv');

% 获取所有sheet名
[~, sheets] = xlsfinfo(file_path);
numSheets = numel(sheets);

% 预分配结果存储
SheetName = cell(numSheets, 1);
AvgX = zeros(numSheets, 1);
AvgY = zeros(numSheets, 1);
AvgZ = zeros(numSheets, 1);

% 遍历每个sheet
for i = 1:numSheets
    sheet_name = sheets{i};
    
    % 读取时保留原始列名
    opts = detectImportOptions(file_path, 'Sheet', sheet_name);
    opts.VariableNamingRule = 'preserve';
    data = readtable(file_path, opts);
    
    % 调试输出当前列名
    fprintf('正在处理Sheet: %s\n列名列表：\n', sheet_name);
    disp(data.Properties.VariableNames);
    
    % 精确匹配列名（处理特殊字符）
    colNames = data.Properties.VariableNames;
    
    % 匹配坐标X列的三种可能情况
    xCol = find(...
        strcmpi(colNames, '坐标X[mm]') | ...        % 完全匹配
        strcmpi(colNames, '坐标X(mm)') | ...        % 兼容圆括号
        ~cellfun(@isempty, regexpi(colNames, '^坐标\s*X\s*$$mm$$$'))... % 正则匹配
        , 1);
    
    % 同理处理Y/Z列
    yCol = find(strcmpi(colNames, '坐标Y[mm]'), 1);
    zCol = find(strcmpi(colNames, '坐标Z[mm]'), 1);

    % 详细错误报告
    if isempty(xCol)
        error('Sheet %s 缺失坐标X列，请检查列名是否精确为"坐标X[mm]"\n当前列名：%s',...
              sheet_name, strjoin(colNames, ', '));
    end
    if isempty(yCol)
        error('Sheet %s 缺失坐标Y列，请检查列名是否精确为"坐标Y[mm]"\n当前列名：%s',...
              sheet_name, strjoin(colNames, ', '));
    end
    if isempty(zCol)
        error('Sheet %s 缺失坐标Z列，请检查列名是否精确为"坐标Z[mm]"\n当前列名：%s',...
              sheet_name, strjoin(colNames, ', '));
    end
    
    % 计算平均值（处理空值）
    AvgX(i) = mean(data{:, xCol}, 'omitnan');
    AvgY(i) = mean(data{:, yCol}, 'omitnan');
    AvgZ(i) = mean(data{:, zCol}, 'omitnan');
    SheetName{i} = sheet_name;
end

% 创建结果表格
results = table(SheetName, AvgX, AvgY, AvgZ, ...
    'VariableNames', {'Sheet_Name', 'Avg_X', 'Avg_Y', 'Avg_Z'});

% 将sheet名称转换为数字
numSheetNames = str2double(results.Sheet_Name);

% 验证转换是否全部成功
if any(isnan(numSheetNames))
    error('存在非数字的Sheet名称，无法进行数值排序');
end

% 获取排序索引
[~, index] = sort(numSheetNames);

% 按数字顺序重排结果
results = results(index, :);

% 保存为CSV文件
writetable(results, output_csv);

disp(['处理完成，结果保存至：' output_csv]);