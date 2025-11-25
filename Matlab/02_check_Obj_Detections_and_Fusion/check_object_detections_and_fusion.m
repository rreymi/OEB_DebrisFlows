%% Check Object Detections script
%  
% Script to analyse and visualize decetions over several frames
% 
%

% Run 03_Object Detection Analysis first! 

clear;clc

%% === EVENT
event_year = "2024";
event_month = "06";
event_day = "14";

%% === 00 - LOAD CONFIG and SYNC

configs = load(sprintf('ConfigFiles/config_%s_%s_%s.mat', event_year, event_month, event_day));
addpath(genpath('utils'))

load(configs.camera_calibRes_path) % Camera Params
load(configs.camera_lidar_tform_path) % tform

synced_frames = readtable(configs.path_ldr_cam_sync); % snyced tabelle

%% 01 - LOAD and pre-FILTER / Cut Tracks

tracks = readtable(configs.path_tracks);
tracks = tracks(tracks.frame_number >= configs.frame_start,:);
tracks = tracks(tracks.frame_number <= configs.frame_end,:);

% find synced ldr cam frames
min_img_frame = synced_frames.frame_img(1);
max_img_frame = synced_frames.frame_img(end);

% be careful here!!
%tracks.frame_number_img = tracks.frame_number + 1; % workaround bcs it falsely starts from 0 (fixed in last version on gitlab)
tracks.frame_number_img = tracks.frame_number;
tracks.frame_number = []; % remove col, not used later, 

tracks = tracks(tracks.frame_number_img >= min_img_frame,:);
tracks = tracks(tracks.frame_number_img <= max_img_frame,:);

[~,idx] = ismember(tracks.frame_number_img,synced_frames.frame_img); % 0 are not in synced frames, other numbers or indices in tracks
tracks = tracks(idx > 0,:); % kick out the ones that do not have a corresponding lidar ptcloud

[~,idx] = ismember(tracks.frame_number_img,synced_frames.frame_img); % repeat for new tracks
tracks.frame_number_ldr = synced_frames.frame_ldr(idx); % Assign corresponding ldr frame numbers
%
tracks = tracks(:, {'frame_number_img', 'frame_number_ldr', 'track_id', 'class_id', 'x', 'y', 'width', 'height'});
%
fprintf('\n === 01 Tracks loaded \n');

%% 02 - Filter Tracks / min length - spec. track ids / change format

% filter tracks 
tracks_to_display = filter_tracks(tracks, configs.tracks_to_display, configs.min_track_length);
tracks = tracks(ismember(tracks.track_id, tracks_to_display), :);

% Pre define Variables from config and change format
path_ptcloud    = configs.path_ptcloud;
path_img        = configs.path_img;
spacing         = configs.spacing;
zCutoff         = configs.zCutoff;
xLim            = configs.xLim;
yLim            = configs.yLim;

% change bbox format
bb_left = tracks.x - tracks.width/2;
bb_top = tracks.y - tracks.height/2;
bb_width = tracks.width;
bb_height = tracks.height;
tracks.bb_left = bb_left;
tracks.bb_top = bb_top;
tracks.bb_width = bb_width;
tracks.bb_height = bb_height;

fprintf('\n === 02 Tracks filtered \n');
fprintf('\n number of Tracks: %d \n', length(tracks_to_display));
fprintf('\n start and end frame: %d - %d \n', tracks.frame_number_img(1), tracks.frame_number_img(end));

%% save it tempo
save('tracks.mat', 'tracks');

%% Reload later
load('tracks.mat'); 

%%  ------- BBOXES ON IMAGES
%
% % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % -% - %

%% PLOT detections (bboxes) on single img

frame_img_interest = 33317;

plot_bboxes_on_img_V2(frame_img_interest, all_stats, configs.path_img)

%plot_bboxes_on_img(frame_img, tracks, configs.path_img)

%% PLOT all frames where TrackID is shown - TODO switch to all stats

TrackID_interest = 2700000;%398836;%418459;

plot_bboxes_over_frames_V2(all_stats, TrackID_interest, configs.path_img, 0.2)

%% Save as Video
plot_bboxes_over_frames_to_video(all_stats, TrackID_interest, configs.path_img)


%tracks_of_trackid = tracks(tracks.track_id == TrackID_interest, :);
%plot_bboxes_over_frames(tracks_of_trackid, configs.path_img, 0.2)
%plot_bboxes_over_frames_video(tracks_of_trackid, configs.path_img, .1)


%%  ------- BBOXES ON Point Clouds + CENTER and EDGE Points
%
% % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % -% - %

frame_img_interest = 33065;
TrackID_interest = 2700000;

all_stats_of_TrackID = all_stats(all_stats.track == TrackID_interest, :);

% map ldr frames (WORKAROUND)
[tf, idx] = ismember(all_stats_of_TrackID.frame, synced_frames.frame_img);
all_stats_of_TrackID.frame_number_ldr(tf) = synced_frames.frame_ldr(idx(tf));

%% Project BBOX on ptcloud
reproj_bbox_on_ptcloud(all_stats_of_TrackID, frame_img_interest, ...
    configs.path_ptcloud, cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim)


%%  ------- ptcloud, BBox and Points on IMG
%
% % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % - % -% - %

%% Plot single IMG
project_ptcloud_on_img(all_stats_of_TrackID, frame_img_interest, configs.path_img, ...
    configs.path_ptcloud, cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim)


%% Plot Video sequence of Track ID

project_ptcloud_on_img_video(all_stats_of_TrackID, configs.path_img, ...
    configs.path_ptcloud, cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim, 5)

%% verlauf gs und velocity

velo_id = velocity_{TrackID_interest};
gs_id = width{TrackID_interest};
figure
plot(tracks_of_trackid.frame_number_img(1:length(velo_id)), velo_id)
ylabel('velocity (m/s)')

figure
plot(tracks_of_trackid.frame_number_img, gs_id)
ylabel('grainsize (m)')


%%
mean(velo_id)
median(velo_id)
std(velo_id)
%%
mean(gs_id)
median(gs_id)
std(gs_id)








