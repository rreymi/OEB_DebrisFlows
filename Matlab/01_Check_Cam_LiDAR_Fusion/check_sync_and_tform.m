%% Camera Lidar Fusion with sync timestamps and tform
%{
 
26.08.2025 Roman 

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

% camera lens calibration
load(path_cameraParams) 

% lidar/cam transformation matrix
load(path_tform) 

%% STEP 1a: FIND lidar and image frames around desired img frame number

frame_img = 35299; % desired image frame --> img frame muss im synched csv vorhanden sein
window = 0; % frame_img +/- window will be browsed

frame_ldr = synced_frames.frame_ldr(synced_frames.frame_img == frame_img); % logical for corresp. lidar frame
frames_ldr = (frame_ldr-window:frame_ldr+window).';
frames_img = zeros(length(frames_ldr),1);
for i=1:length(frames_img)
    frames_img(i) = synced_frames.frame_img(synced_frames.frame_ldr == frames_ldr(i));
end

%% STEP 1b: FIND lidar and image around desired img frame number but in STEP OF 5 (0.5 sec)

frame_img = 5702; % desired image frame --> img frame muss im synched csv vorhanden sein
window = 500; % frame_img +/- window will be browsed

frame_ldr = synced_frames.frame_ldr(synced_frames.frame_img == frame_img); % logical for corresp. lidar frame
frames_ldr = (frame_ldr-window: 10: frame_ldr+window).';
frames_img = zeros(length(frames_ldr),1);
for i=1:length(frames_img)
    frames_img(i) = synced_frames.frame_img(synced_frames.frame_ldr == frames_ldr(i));
end

%% STEP 2: LOAD images and point clouds
numImgs  = numel(frames_img);
imgs = cell(1, numImgs);
ptclouds = cell(1, numImgs);

for i = 1:numImgs
    
    % load ptcloud
    ptcloud_filename = sprintf('%05d.ply',frames_ldr(i));
    ptcloud_fullfile = fullfile(path_ldr, ptcloud_filename);
    if isfile(ptcloud_fullfile)
        ptclouds{i} = pcread(ptcloud_fullfile);
        fprintf('loaded ptcloud: %s\n',ptcloud_fullfile)
    else
        fprintf('file does not exist: %s\n',ptcloud_fullfile)
    end

    % load img
    img_filename = sprintf('%06d.jpeg',frames_img(i));  % %06d angepasst da neu nichtmehr alle eine null haben vorne  (event 14 6 und 15c noch so)
    img_fullfile = fullfile(path_img, img_filename);
    if isfile(ptcloud_fullfile)
        imgs{i} = imread(img_fullfile);
        fprintf('loaded img: %s\n',img_fullfile)
    else
        fprintf('file does not exist: %s\n',img_fullfile)
    end

end

%% STEP 3: FUSION - tform 

n_imgs = numel(imgs);
xy_imPts    = cell(1, n_imgs);
z_imPts     = cell(1, n_imgs);
for i = 1:n_imgs
    [imPts,indices_all]  = projectLidarPointsOnImage(ptclouds{i},cameraParams.Intrinsics,tform);
    xy_imPts{i} = imPts;
    z_imPts{i} = ptclouds{i}.Location(indices_all,3);
end

%% STEP optional: PLOT single frame

% Initialize figure
fig = figure('Name', 'IMG & PtCloud Viewer');
set(fig, 'WindowKeyPressFcn', @(src,evt) keyPress(src, evt, xy_imPts, z_imPts, imgs, frames_ldr, frames_img));
updatePlot(1, xy_imPts, z_imPts, imgs, frames_ldr, frames_img);


%% STEP 4: SAVE plots to output folder

% --- check for existing folder or create output folder
exportDir = fullfile('Outputs', 'overlay', sprintf("%s_%s_%s", event_year, event_month, event_day), sprintf("%d", frame_img));
if ~exist(exportDir, 'dir')
    mkdir(exportDir);
end

% --- Batch export all frames ---
parfor (idx = 1:n_imgs, 6)
    savePlots_to_overlay(idx, xy_imPts, z_imPts, imgs, frames_img, exportDir);
end


%% GIF 

frameFiles = dir(fullfile(exportDir, 'frame_*.jpg'));

% --- sort by name (numeric index after 'frame_') ---
names   = {frameFiles.name};
tokens  = regexp(names, '^frame_(\d+)\.jpg$', 'tokens', 'once');
idxNum  = cellfun(@(t) iff(isempty(t), NaN, str2double(t{1})), tokens);

if any(~isnan(idxNum))
    [~, idxSort] = sort(idxNum);             % numeric sort by frame number
else
    [~, idxSort] = sort(names);              % fallback: pure lexicographic
end
frameFiles = frameFiles(idxSort);

% --- create GIF ---
gifFile   = fullfile(exportDir, sprintf("GIF_%d.gif", frame_img));
delayTime = 0.2;

for k = 1:numel(frameFiles)
    img = imread(fullfile(exportDir, frameFiles(k).name));
    [A, map] = rgb2ind(img, 256);

    if k == 1
        imwrite(A, map, gifFile, 'gif', 'LoopCount', Inf, 'DelayTime', delayTime);
    else
        imwrite(A, map, gifFile, 'gif', 'WriteMode', 'append', 'DelayTime', delayTime);
    end
end

disp("GIF gespeichert unter: " + gifFile);

% --- helper inline function (works in recent MATLAB) ---
function out = iff(cond, a, b), if cond, out = a; else, out = b; end, end

%% MP4
% Video MP4 erstellen
aviFile = fullfile(exportDir, sprintf("animation_%d.avi", frame_img));
delayTime = 0.2;   % 0.2s pro Frame
fps = 1 / delayTime;    % Frames per second (hier: 2 fps)

v = VideoWriter(aviFile, 'Uncompressed AVI');  % verlustfrei
v.FrameRate = fps;
open(v);

for k = 1:numel(frameFiles)
    img = imread(fullfile(exportDir, frameFiles(k).name));
    writeVideo(v, img);
end

close(v);
disp(['Video gespeichert unter: ' aviFile]);


%% Plot colored point cloud


ptCloudColored = fuseCameraToLidar(imgs{1},ptclouds{1}, ...
                                       cameraParams, invert(tform));

figure('Name', 'Colored Point Cloud Fusion');
    pcshow(ptclouds{1}, 'MarkerSize', 10);   % Original cloud
    hold on;
    pcshow(ptCloudColored, 'MarkerSize', 100);        % Colored cloud
    title(sprintf('Point Cloud Fusion (Frame img %d)', frame_ldr));


    
%% interpret point cloud for fig below

xlim = [-20, 20];
ylim = [-20, 20];
zlim = 5;
spacing = 0.1;


[ptcloud_interp, F] = interpolatePointCloudToEvenSpacingCameraLimits(ptclouds{1}, spacing, zlim, xlim, ylim);
pcwrite(ptcloud_interp, sprintf("%d.ply", frame_ldr));
ptclouds_interp{i} = pcread(sprintf("%d.ply", frame_ldr));

%%


ptCloudColored = fuseCameraToLidar(imgs{1},ptclouds_interp{1}, ...
                                       cameraParams, invert(tform));

figure('Name', 'Colored Point Cloud Fusion');
    pcshow(ptclouds_interp{1}, 'MarkerSize', 10);   % Original cloud
    hold on;
    pcshow(ptCloudColored, 'MarkerSize', 100);        % Colored cloud
    title(sprintf('Point Cloud Fusion (Frame img %d)', frame_ldr));
