%% Synchronize LiDAR point clounds and camera images
% saves snych table in 02_PreProcessedData folder
% as synced_timestamps_2024_06_14.csv

clc
clear all
close all

%% Event data

event_year = "2024";
event_month = "06";
event_day = "15b";

station = "Chalberspissi";
sensor = "Karlsson";

%% PATHS

addpath('Tools')

path0 = "//tiliva/eg/01_Projects/01_Ambizione/UncompressData/OEB";

% start from this lidar pose and ignore the earlier (e.g. if lidar/cam
% already streaming while cam/lidar still starting up
%pose0 = 0;

% paths
path_to_event = fullfile(path0, "Events", event_year, sprintf("%s_%s_%s", event_year, event_month, event_day), station);
path_to_matfiles = fullfile(path_to_event, "01_RawData", "ptClouds", sensor);
path_to_timestamp_file = fullfile(path_to_matfiles, "pose_image_timestamp_map.txt");
path_to_save_sync = fullfile(path_to_event, "02_PreProcessedData", sprintf("synced_timestamps_%s_%s_%s.csv", event_year, event_month, event_day));

%% run sync function

sync_time_stamps(path_to_timestamp_file, path_to_save_sync)

sync_table = readtable(path_to_save_sync); % if you want to check the
% file