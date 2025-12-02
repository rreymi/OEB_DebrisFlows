%% Check Object Detections script
%  
% Script to analyse and visualize decetions over several frames
% 
% 

% Roman Renner 
% November 2025

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

% Load all_stats - pre filtering
load("Data\Input_mat\all_stats_2024_06_14.mat")

% Load - all stats after filtering
df_stats = readtable('Data\Input_csv\df_stats_2024_06_14.csv');

% df_mova - table used for plotting (Moving Average of parameters)
df_mova = readtable('Data\Input_csv\df_mova_2024_06_14.csv');

% All_stats filtered by remaining tracks inside df_stats
all_stats_filtered = all_stats( ...
    ismember(all_stats.track, df_stats.track), :);

%% === FRAME AND TRACK ID of Interest

frame_img_interest = 10943;

%% Track

TrackID_interest = 445408;%2700000;%418459;


%% === 01.1 PLOT all detections (bboxes) on single image frame
fig = figure;
ax  = axes(fig);
plot_bboxes_on_img(frame_img_interest, all_stats, configs.path_img, ax, TrackID_interest)
n_tracks = numel(unique(all_stats.track(all_stats.frame == frame_img_interest)));
fprintf('Frame %d: %d tracks\n', frame_img_interest, n_tracks);
%% === 01.2 PLOT all detections (bboxes) on multiple image frames

n_frames = 15;

unique_Frame = unique(all_stats.frame);
idx = find(unique_Frame >= frame_img_interest, 1, 'first');
next_frames = unique_Frame(idx : min(idx + n_frames - 1, numel(unique_Frame)));

fig = figure;
ax  = axes(fig);

for k = 1:numel(next_frames)
    frame = next_frames(k);

    plot_bboxes_on_img(frame, all_stats, configs.path_img, ax, TrackID_interest);

    n_tracks = numel(unique(all_stats.track(all_stats.frame == frame)));
    fprintf('Frame %d: %d tracks\n', frame, n_tracks);

    waitforbuttonpress;   % press any key → next frame
end

close(fig);

%% === 02.1 PLOT all detections (bboxes) on single image frame - AFTER FILTERING
fig = figure;
ax  = axes(fig);
plot_bboxes_on_img(frame_img_interest, all_stats_filtered, configs.path_img, ax, TrackID_interest)
n_tracks = numel(unique(all_stats_filtered.track(all_stats_filtered.frame == frame_img_interest)));
fprintf('Frame %d: %d tracks\n', frame_img_interest, n_tracks);


%% == 02.2 PLOT all detections (bboxes) on multiple image frames - AFTER FILTERING

n_frames = 15;

unique_Frame = unique(all_stats_filtered.frame);
% find index of the first frame >= frame_img_interest and following n_fr
idx = find(unique_Frame >= frame_img_interest, 1, 'first');
next_frames = unique_Frame(idx : min(idx + n_frames - 1, numel(unique_Frame)));

fig = figure;
ax  = axes(fig);

for k = 1:numel(next_frames)
    frame = next_frames(k);

    plot_bboxes_on_img(frame, all_stats_filtered, configs.path_img, ax, TrackID_interest);

    n_tracks = numel(unique(all_stats_filtered.track(all_stats_filtered.frame == frame)));
    fprintf('Frame %d: %d tracks\n', frame, n_tracks);

   waitforbuttonpress;
end

%% === 03 PLOT all bboxes over all frames where TrackID is shown 

plot_bboxes_over_frames(all_stats, TrackID_interest, configs.path_img, 0.2)

%% === 03.1 Save as Video

%plot_bboxes_over_frames_to_video(all_stats, trackID, pathImg, fps, save_path, video_name)
plot_bboxes_over_frames_to_video(all_stats, TrackID_interest, configs.path_img, 5)


%%  === 04.0 Prepare table to Project bbox on PointCloud

all_stats_of_TrackID = all_stats(all_stats.track == TrackID_interest, :);

% map ldr frames (WORKAROUND)
[tf, idx] = ismember(all_stats_of_TrackID.frame, synced_frames.frame_img);
all_stats_of_TrackID.frame_number_ldr(tf) = synced_frames.frame_ldr(idx(tf));

df_stats_of_TrackID = df_stats(df_stats.track == TrackID_interest, :);


%% === 04.1 03 Project bbox on PointCloud

show_bbox_on_ptcloud(all_stats_of_TrackID, frame_img_interest, configs.path_ptcloud, ...
    cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim)




%%  === 05 Reproject bbox on Pointcloud onto IMAGE
%   === 05.1 Plot single IMG

project_ptcloud_on_img(all_stats_of_TrackID, frame_img_interest, configs.path_img, ...
    configs.path_ptcloud, cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim)


%% === 05.2 Saves as Video

project_ptcloud_on_img_to_video(all_stats_of_TrackID, configs.path_img, ...
    configs.path_ptcloud, cameraParams, tform, configs.spacing, configs.zCutoff,configs.xLim,configs.yLim, 5)






%% verlauf gs und velocity

velo_id = all_stats_of_TrackID.velocity;
gs_id = all_stats_of_TrackID.grainsize;
figure
plot(all_stats_of_TrackID.frame, velo_id)
ylabel('velocity (m/s)')

figure
plot(all_stats_of_TrackID.frame, gs_id)
ylabel('grainsize (m)')


%%
mean(velo_id)
median(velo_id)
std(velo_id)
%%
mean(gs_id)
median(gs_id)
std(gs_id)

%% === 06 Track length table

[counts, trackIDs] = groupcounts(df_stats.track);
track_count_table = table(trackIDs, counts, ...
    'VariableNames', {'track_id', 'count'});


