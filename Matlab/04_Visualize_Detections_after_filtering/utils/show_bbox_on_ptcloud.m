function show_bbox_on_ptcloud(allStats, frameImg, pathPtCloud, cameraParams, tform, spacing, zCutoff, xLim, yLim)
%SHOW_BBOX_ON_PTCLOUD
%   Reprojects 2D image bounding boxes onto the LiDAR point cloud for a
%   given image frame. Highlights:
%       • Full LiDAR cloud
%       • Points falling inside each 2D bounding box
%       • (Optional) special lidar points per object: left, center, right
%
%   Inputs:
%       allStats    - Table containing track data (single track pre-filtered)
%       frameImg    - Image frame number to visualize (scalar)
%       pathPtCloud - Folder path containing *.ply LiDAR files
%       cameraParams - Camera intrinsics
%       tform       - Rigid transform LiDAR → camera
%       spacing, zCutoff, xLim, yLim - point cloud filtering/interpolation


%% 00 Extract row for this image frame

T = allStats(allStats.frame == frameImg, :);

if isempty(T)
    warning('Frame %d does not exist in the provided track table.', frameImg);
    return;
end

trackID = allStats.track(1);                  % the track ID (all rows have same)
frameLdr = T.frame_number_ldr(1);             % LiDAR frame associated (already merged upstream)


%% 01 Load & interpolate LiDAR point cloud

filePath = fullfile(pathPtCloud, sprintf('%05d.ply', frameLdr));

if ~isfile(filePath)
    error('PLY file not found: %s', filePath);
end

ptCloudRaw = pcread(filePath);

% Interpolate & crop to camera limits
[ptCloudInterp, ~] = interpolatePointCloudToEvenSpacingCameraLimits(ptCloudRaw, spacing, zCutoff, xLim, yLim);

% White cloud for background
ptCloudInterp = colorPtCloud(ptCloudInterp, [255 255 255]);


%% 02 Project LiDAR → image

[projImgPoints, idxValid] = projectLidarPointsOnImage(ptCloudInterp, cameraParams.Intrinsics, tform);

ptCloudImg = select(ptCloudInterp, idxValid);


%% 03 Find points inside bounding box

% Extract the single bounding box
bbox = [T.bb_left, T.bb_top, T.bb_width, T.bb_height];

% Convert bbox → polygon points
poly = bbox2points(bbox);
xv = poly(:,1);
yv = poly(:,2);

% Determine which LiDAR-image projected points fall inside the bbox
inBoxMask = inpolygon(projImgPoints(:,1), projImgPoints(:,2), xv, yv);

objectPts = select(ptCloudImg, inBoxMask);
objectPts = colorPtCloud(objectPts, 255 * [0 0.4470 0.7410]); % blue-ish


%% 04 Plot

fig = figure('Name', sprintf('Frame %d – Track %d', frameImg, trackID));
ax  = axes('Parent', fig);

cla(ax);
pcshow(ptCloudInterp, 'Parent', ax, 'MarkerSize', 15);
hold(ax, 'on');

% Highlight bbox points
pcshow(objectPts, 'Parent', ax, 'MarkerSize', 40);

% Special points
scatter3(ax, T.bb_left_lidar_x,   T.bb_left_lidar_y,   T.bb_left_lidar_z,   40, 'red',    'filled');
scatter3(ax, T.bb_center_lidar_x, T.bb_center_lidar_y, T.bb_center_lidar_z, 40, 'magenta','filled');
scatter3(ax, T.bb_right_lidar_x,  T.bb_right_lidar_y,  T.bb_right_lidar_z,  40, 'green',  'filled');

title(ax, sprintf('Reprojection – ImgFrame %d – Track %d', frameImg, trackID));
xlabel(ax,'X'); ylabel(ax,'Y'); zlabel(ax,'Z');
grid(ax,'on');
hold(ax,'off');

drawnow;

end




