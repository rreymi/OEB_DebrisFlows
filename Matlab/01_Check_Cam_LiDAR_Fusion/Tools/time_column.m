%% timestamps
%{

Path sind auf Tiliva verwiesen. Verbindung zu Cisco prüfen!


%}

%% Event definition

clear
close all
clc

% Define Event Number
%%
event_year = "2024";
event_month = "06";
event_day = "14";

station = "Chalberspissi";
sensor = "Karlsson";

%% STEP 0: PATH definitions

% ---  Path on Tiliva server
path0 = "//tiliva/eg/01_Projects/01_Ambizione/UncompressData/OEB"; 
% // needed for a network path, only one / interprets as a absolute path

% --- Paths in WD
path_to_event = fullfile(path0, "Events", event_year, sprintf("%s_%s_%s", event_year, event_month, event_day), station);
path_img = fullfile(path_to_event, "02_PreProcessedData", "undistorted_images");
path_ldr = fullfile(path_to_event, "02_PreProcessedData", "ptClouds_ply", "Karlsson");
path_synced_timestamps = fullfile(path_to_event, "02_PreProcessedData", sprintf("synced_timestamps_%s_%s_%s.csv", event_year, event_month, event_day));
path_cameraParams = 'Data/cameraParams.mat';
path_tform = 'Data/best_tform.mat';
addpath('Tools')

% read temporal lidar/cam synchronization file
synced_frames = readtable(path_synced_timestamps);

%%

synced_frames.time = synced_frames.timestamp_img - synced_frames.timestamp_img(1);

% Build filename dynamically
filename = sprintf("time_column_%s_%s_%s.txt", event_year, event_month, event_day);

T = synced_frames(:, {'frame_img','time'});

writetable(T, filename)
