% Script to convert .mat table to a txt file

% load and save as chunks and append to one
clear;clc
%% == EVENT
event_year = "2024";
event_month = "06";
event_day = "14";


%% === CONFIG
configs = load(sprintf('ConfigFiles/config_%s_%s_%s.mat', event_year, event_month, event_day));

%% === LOAD .mat file - all_stats
%all_stats = load(configs.path_mat).all_stats;

all_stats = load('Data\Output_mat\all_stats_2024_06_14_tl10_lim2020_100_100000.mat').all_stats;

%% --- SAVE smaller csv as CHUNKS - ONLY temp

chunk_size = 500000; % number of rows per CSV 

output_csv = fullfile('Data', 'Output_csv');
if ~exist(output_csv, 'dir')
    mkdir(output_csv);
end

num_rows = height(all_stats);
num_chunks = ceil(num_rows / chunk_size);

% Save chunks
for i = 1:num_chunks
    start_idx = (i-1)*chunk_size + 1;
    end_idx = min(i*chunk_size, num_rows);
    
    chunk = all_stats(start_idx:end_idx, :);  % extract chunk
    filename = fullfile(output_csv, sprintf('all_stats_chunk_%d.csv', i));
    
    writetable(chunk, filename);
    fprintf('Saved rows %d to %d -> %s\n', start_idx, end_idx, filename);
end

% --- LOAD CSVs and append to TXT

output_txt = fullfile('Data', 'Output_txt');
if ~exist(output_txt, 'dir')
    mkdir(output_txt);
end

txt_filename = sprintf('all_stats_%s.txt', configs.name);
txt_filepath = fullfile(output_txt, txt_filename);

% Get list of all CSV files in the folder
csv_files = dir(fullfile(output_csv, 'all_stats_chunk_*.csv'));

% Initialize a flag to write header only once
write_header = true;

% Loop through CSV chunks and append to text file
for i = 1:length(csv_files)
    chunk_path = fullfile(csv_files(i).folder, csv_files(i).name);
    
    % Read chunk
    chunk = readtable(chunk_path);
    
    % Append to text file
    writetable(chunk, txt_filepath, 'WriteMode', 'append', 'WriteVariableNames', write_header, 'Delimiter', ',');
    
    % After first chunk, turn off header
    write_header = false;
    
    fprintf('Appended %s -> %s\n', csv_files(i).name, txt_filepath);
end

fprintf('All chunks combined into %s\n', txt_filepath);

% Delete CSVs
rmdir(output_csv, 's');
%
fprintf('\n== done ==\n')