%% bbox2ptcloud VERSION (loop through frames)

% this script projects bounding boxes onto the lidar point cloud and
% computes velocities and grain sizes

% new version - Novemeber 25
% updated for OEB
% Roman 

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
path_ptcloud = configs.path_ptcloud;
spacing      = configs.spacing;
zCutoff      = configs.zCutoff;
xLim         = configs.xLim;
yLim         = configs.yLim;

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

%% - 02a drop cols of tracks

tracks.width = [];
tracks.height = [];
tracks.class_id = [];
tracks.x = [];
tracks.y = [];


%% 03 - REPROJECT all bboxes and find bbox center and width

% == Initialize  
n_tracks = max(tracks.track_id);
% Preallocate arrays for each track (Nx3 for LiDAR, Nx2 for image)
bbox_centers_lidar       = cell(1, n_tracks);
bbox_centers_left_lidar  = cell(1, n_tracks);
bbox_centers_right_lidar = cell(1, n_tracks);
bbox_centers_img         = cell(1, n_tracks);
bbox_centers_left_img    = cell(1, n_tracks);
bbox_centers_right_img   = cell(1, n_tracks);

% Initialize as empty numeric arrays
for t = 1:n_tracks
    bbox_centers_lidar{t}       = zeros(0,3);
    bbox_centers_left_lidar{t}  = zeros(0,3);
    bbox_centers_right_lidar{t} = zeros(0,3);
    bbox_centers_img{t}         = zeros(0,2);
    bbox_centers_left_img{t}    = zeros(0,2);
    bbox_centers_right_img{t}   = zeros(0,2);
end

% == parfor loop, loop through frames, reproject bboxes --- main part
frame_pairs = unique(tracks(:, {'frame_number_img', 'frame_number_ldr'}));
frames_img = frame_pairs.frame_number_img;
frames_ldr = frame_pairs.frame_number_ldr;

n_frames = length(frames_img);
frame_results = cell(1, n_frames);  % store temporary results per frame

tic
parfor f_idx = 1:n_frames    
    f_img = frames_img(f_idx); % frame image number
    
    % gather all tracks data within frame
    frame_data = tracks(tracks.frame_number_img == f_img, :);
    fprintf('\n === Processing frame %d of %d (frame %d) ===\n', f_idx, n_frames, f_img);

    % Temporary storage for all detections in this frame
    tmp_lidar       = cell(1, height(frame_data));
    tmp_left_lidar  = cell(1, height(frame_data));
    tmp_right_lidar = cell(1, height(frame_data));
    tmp_img         = cell(1, height(frame_data));
    tmp_left_img    = cell(1, height(frame_data));
    tmp_right_img   = cell(1, height(frame_data));

    % Load point cloud
    ptcloud_filename = sprintf('%05d.ply', frames_ldr(f_idx));
    ptcloud_fullfile = fullfile(path_ptcloud, ptcloud_filename);
    ptcloud = pcread(ptcloud_fullfile);
    [ptcloud_interpol,~] = interpolatePointCloudToEvenSpacingCameraLimits(ptcloud, spacing, zCutoff, xLim, yLim);

    % Project LiDAR to image
    [imPts, indices_all] = projectLidarPointsOnImage(ptcloud_interpol, cameraParams.Intrinsics, tform);
    ptCloudimg = select(ptcloud_interpol, indices_all);
    
    % Loop over detections in this frame
    for d_idx = 1:height(frame_data)
        track_id = frame_data.track_id(d_idx); % track_id

        % Bounding box in the image: [x, y, width, height]
        bbox = [frame_data.bb_left(d_idx), frame_data.bb_top(d_idx), ...
                frame_data.bb_width(d_idx), frame_data.bb_height(d_idx)];

        points = bbox2points(bbox); % converts [x, y, w, h] → 4 (x,y) corner points
        xv = points(:,1); yv = points(:,2);

        % Find which image pixels fall inside the box and select points
        in_box = inpolygon(imPts(:,1), imPts(:,2), xv, yv);
        object = select(ptCloudimg, in_box);

        % Center of the bounding box
        Xm = bbox(1) + 0.5*bbox(3);
        Ym = bbox(2) + 0.5*bbox(4);
        [nearest_img_center, nearest_ptcloud_center] = find_nearest_img_ptcloud(Xm, Ym, imPts, ptCloudimg);
        
        % Left middle point of the box
        Xl = bbox(1); Yl = bbox(2) + 0.5*bbox(4);
        [nearest_img_left, nearest_ptcloud_left] = find_nearest_img_ptcloud(Xl, Yl, imPts, ptCloudimg);
        
        % Right middle point of the box
        Xr = bbox(1) + bbox(3); Yr = bbox(2) + 0.5*bbox(4);
        [nearest_img_right, nearest_ptcloud_right] = find_nearest_img_ptcloud(Xr, Yr, imPts, ptCloudimg);

        % Each temporary array stores results for this frame and detection.
        tmp_lidar{d_idx}       = struct('track_id', track_id, 'data', nearest_ptcloud_center);
        tmp_left_lidar{d_idx}  = struct('track_id', track_id, 'data', nearest_ptcloud_left);
        tmp_right_lidar{d_idx} = struct('track_id', track_id, 'data', nearest_ptcloud_right);
        tmp_img{d_idx}         = struct('track_id', track_id, 'data', nearest_img_center);
        tmp_left_img{d_idx}    = struct('track_id', track_id, 'data', nearest_img_left);
        tmp_right_img{d_idx}   = struct('track_id', track_id, 'data', nearest_img_right);
    end

    % Save temporary results for merging after parfor
    frame_results{f_idx} = struct('tmp_lidar', tmp_lidar, 'tmp_left_lidar', tmp_left_lidar, ...
                                  'tmp_right_lidar', tmp_right_lidar, 'tmp_img', tmp_img, ...
                                  'tmp_left_img', tmp_left_img, 'tmp_right_img', tmp_right_img);
end
toc
fprintf(' === Finished processing all frames.\n');



% == Write final cell arrays after parfor loop
tic
for f_idx = 1:n_frames
    tmp = frame_results{f_idx};  
    
    if isempty(tmp)     % Skip empty frames
        continue
    end
    
    nDetections = numel(tmp);   % number of detections in this frame
    
    for d_idx = 1:nDetections
        s = tmp(d_idx);  % struct for this detection
         
        track_id = s.tmp_lidar.track_id; % get track id of detection
               
        % Append detection data from nested structs
        bbox_centers_lidar{track_id}       = [bbox_centers_lidar{track_id}; s.tmp_lidar.data];
        bbox_centers_left_lidar{track_id}  = [bbox_centers_left_lidar{track_id}; s.tmp_left_lidar.data];
        bbox_centers_right_lidar{track_id} = [bbox_centers_right_lidar{track_id}; s.tmp_right_lidar.data];
        bbox_centers_img{track_id}         = [bbox_centers_img{track_id}; s.tmp_img.data];
        bbox_centers_left_img{track_id}    = [bbox_centers_left_img{track_id}; s.tmp_left_img.data];
        bbox_centers_right_img{track_id}   = [bbox_centers_right_img{track_id}; s.tmp_right_img.data];
    end
end

fprintf('\n === REPROJECT completed === \n');



% === VELOCITY CALCULATION ===
velocity_ = cell(size(bbox_centers_lidar)); % preallocate same size

for i = 1:numel(bbox_centers_lidar)
    points = bbox_centers_lidar{i};
    if isempty(points) || size(points,1) < 2
        velocity_{i} = []; % no velocity for empty or single-point tracks
        continue
    end
   ldr_numbers = tracks.frame_number_ldr(tracks.track_id == i);
   time_steps = (ldr_numbers - ldr_numbers(1)) / 10; % in secs
   velocity_{i} = calc_3D_vel(points, time_steps); % calculate 3D velocity 
end

fprintf('=== Velocity complete \n');


% === WIDTH (GRAIN SIZE) CALCULATION ===
width = cell(size(bbox_centers_left_lidar)); % preallocate same size

for i = 1:numel(bbox_centers_left_lidar)
    points_l = bbox_centers_left_lidar{i};
    points_r = bbox_centers_right_lidar{i};

    if isempty(points_l) || isempty(points_r)
        width{i} = [];
        continue
    end

    % ensure same length before subtraction
    n = min(size(points_l,1), size(points_r,1));
    points_l = points_l(1:n, :);
    points_r = points_r(1:n, :);

    % calculate Euclidean distance between left/right edges
    distances = sqrt(sum((points_l - points_r).^2, 2));
    width{i} = distances;
end
fprintf('\n === Grain size complete \n');



% === Create and SAVE tables

% --- Define output paths ---
all_stats_file = sprintf('all_stats_%s.txt', configs.name);
all_stats_path = fullfile('Data', 'Output', all_stats_file);

% Preallocate
all_stats_cells = cell(length(tracks_to_display),1); % tmp storage
all_stats = table(); % final storage

% Create a Map where key = track_id, value = row index in tracks
% Get all unique track IDs
unique_tracks = unique(tracks.track_id);
% Initialize map: key = track_id, value = vector of row indices
track_map = containers.Map('KeyType', 'double', 'ValueType', 'any');
for i = 1:length(unique_tracks)
    id = unique_tracks(i);
    % Find all rows in 'tracks' with this track_id
    track_map(id) = find(tracks.track_id == id);
end


% --- Loop over all displayed tracks ---
tic
for x = 1:length(tracks_to_display)

    i = tracks_to_display(x);

    % Skip if this track_id doesnt exist in tracks
    if ~isKey(track_map, i) || isempty(bbox_centers_lidar{i}) || isempty(velocity_{i}) || isempty(width{i})
        continue
    end

    % Lookup row index directly
    idx = track_map(i);
    t = tracks(idx, :);

    % --- Velocity (pad with one extra row as before) ---
    velocity = [0; velocity_{i}(:)];

    % --- Grainsize ---
    grainsize = width{i};

    track = t.track_id;
    frame = t.frame_number_img;
    %class = t.class_id;

    % --- Bounding boxes ---
    bb_left   = t.bb_left;
    bb_top    = t.bb_top;
    bb_width  = t.bb_width;
    bb_height = t.bb_height;

   % --- LIDAR center extraction ---
    bb_center_lidar_x = bbox_centers_lidar{i}(:,1);
    bb_center_lidar_y = bbox_centers_lidar{i}(:,2);
    bb_center_lidar_z = bbox_centers_lidar{i}(:,3);
    bb_left_lidar_x = bbox_centers_left_lidar{i}(:,1);
    bb_left_lidar_y = bbox_centers_left_lidar{i}(:,2);
    bb_left_lidar_z = bbox_centers_left_lidar{i}(:,3);
    bb_right_lidar_x = bbox_centers_right_lidar{i}(:,1);
    bb_right_lidar_y = bbox_centers_right_lidar{i}(:,2);
    bb_right_lidar_z = bbox_centers_right_lidar{i}(:,3);

    % --- Image center extraction ---
    bb_center_img_x = bbox_centers_img{i}(:,1);
    bb_center_img_y = bbox_centers_img{i}(:,2);
    bb_left_img_x = bbox_centers_left_img{i}(:,1);
    bb_left_img_y = bbox_centers_left_img{i}(:,2);
    bb_right_img_x = bbox_centers_right_img{i}(:,1);
    bb_right_img_y = bbox_centers_right_img{i}(:,2);

    % --- Make sure all vectors have same length ---
    lens = [numel(frame), numel(velocity), numel(grainsize), numel(bb_center_lidar_x)];
    n = min(lens);
    
    frame = frame(1:n);
    track = track(1:n);
    %class = class(1:n);
    velocity = velocity(1:n);
    grainsize = grainsize(1:n);
    bb_left = bb_left(1:n);
    bb_top = bb_top(1:n);
    bb_width = bb_width(1:n);
    bb_height = bb_height(1:n);

    bb_center_lidar_x = bb_center_lidar_x(1:n);
    bb_center_lidar_y = bb_center_lidar_y(1:n);
    bb_center_lidar_z = bb_center_lidar_z(1:n);
    bb_left_lidar_x   = bb_left_lidar_x(1:n);
    bb_left_lidar_y   = bb_left_lidar_y(1:n);
    bb_left_lidar_z   = bb_left_lidar_z(1:n);
    bb_right_lidar_x  = bb_right_lidar_x(1:n);
    bb_right_lidar_y  = bb_right_lidar_y(1:n);
    bb_right_lidar_z  = bb_right_lidar_z(1:n);

    bb_center_img_x = bb_center_img_x(1:n);
    bb_center_img_y = bb_center_img_y(1:n);
    bb_left_img_x   = bb_left_img_x(1:n);
    bb_left_img_y   = bb_left_img_y(1:n);
    bb_right_img_x  = bb_right_img_x(1:n);
    bb_right_img_y  = bb_right_img_y(1:n);

    % --- Assemble full track table ---
    t = table(frame, track, velocity, grainsize, ...
              bb_left, bb_top, bb_width, bb_height, ...
              bb_center_lidar_x, bb_center_lidar_y, bb_center_lidar_z, ...
              bb_left_lidar_x, bb_left_lidar_y, bb_left_lidar_z, ...
              bb_right_lidar_x, bb_right_lidar_y, bb_right_lidar_z, ...
              bb_center_img_x, bb_center_img_y, ...
              bb_left_img_x, bb_left_img_y, ...
              bb_right_img_x, bb_right_img_y);

    all_stats_cells{x} = t; % store per iteration   
end

% --- Concatenate once at the end
all_stats = vertcat(all_stats_cells{:});
toc

% === SAVE as .MAT File
outputfolder_mat = fullfile('Data', 'Output_mat');
all_stats_file = sprintf('all_stats_%s.mat', configs.name);
all_stats_path = fullfile(outputfolder_mat, all_stats_file);
if ~exist(outputfolder_mat, 'dir')
    mkdir(outputfolder_mat);
end
save(all_stats_path, 'all_stats', '-v7.3');
%clear 
fprintf('\n === All_stats saved as .mat \n');
fprintf('\n === all finsihed \n');



