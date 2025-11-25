%% bbox2ptcloud config file

% CHECK Obj Detection and Fusion - Novemeber 25
% updated for OEB
% Roman 

clc
clear
close all

event_year = "2024";
event_month = "06";
event_day = "14";

station = "Chalberspissi";
sensor = "Karlsson";

path0 = "//tiliva/eg/01_Projects/01_Ambizione/UncompressData/OEB"; 
path_to_event = fullfile(path0, "Events", event_year, sprintf("%s_%s_%s", event_year, event_month, event_day), station);
%%

name = sprintf("%s_%s_%s", event_year, event_month, event_day);

classes                 = "boulder"; % OEB has only Boulders (class 3)

tracks_to_display       = 'all'; % single track ID can be defined: %[10, 20, 32]; % 'all'; // %10; // % [10,25,...]

min_track_length        = 10; % min number of frames for a track to be considered if tracks_to_display='all'

spacing                 = 0.1; % spacing for interpol ptcloud

zCutoff                 = 0;

xLim                    = [-20 20];

yLim                   = [-20 20]; % for events with general coord. system

fps                     = 10;

az                      = 180; % for pt cloud viz

el                      = 30; % for pt cloud viz

frame_start             = 0; % Define start of image frame number

frame_end               = 100000; % end frame

%frame_viz               = 6060; % frame number to visualize ptcloud-img alignment, make sure it exists

%mk_video_img            = true;

%mk_video_cloud          = true;

path_tracks             = sprintf('Data/TrackFiles/%s.csv',name);

path_ldr_cam_sync       = fullfile(path_to_event, "02_PreProcessedData", sprintf("synced_timestamps_%s.csv", name));

path_ptcloud            = fullfile(path_to_event, '02_PreProcessedData/ptClouds_ply/Karlsson');

path_img                = fullfile(path_to_event, '02_PreProcessedData/undistorted_images');

camera_calibRes_path    = 'Transformations/cameraParams.mat';

camera_lidar_tform_path = 'Transformations/best_tform.mat';

time_of_generation      = datetime('now');

config_name             = sprintf('ConfigFiles/config_%s.mat',name);

save(config_name)
fprintf('written config file %s',config_name)