function project_ptcloud_on_img(allStats, frameImg, pathIMG, pathPtCloud, cameraParams, tform, spacing, zCutoff, xLim, yLim)
%REPROJ_BBOX_ON_PTCLOUD
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

[ptcloud_interpol,~] = interpolatePointCloudToEvenSpacingCameraLimits(ptCloudRaw,spacing,zCutoff,xLim,yLim);

ptcloud_interpol = colorPtCloud(ptcloud_interpol, [255 255 255]);

% === Project Lidar points onto image plane ===
[imPts, ~] = projectLidarPointsOnImage(ptcloud_interpol, cameraParams.Intrinsics, tform);



%% Plot

% === Overlay on image ===
figure('Name','Bbox + Lidar on Img','NumberTitle','off');

img_path = fullfile(pathIMG, sprintf('%06d.jpeg', frameImg));
img = imread(img_path);
imshow(img);
hold on;

% Bounding box
bbox = [T.bb_left, T.bb_top,T.bb_width, T.bb_height];

rectangle('Position', bbox, 'EdgeColor', 'blue', 'LineWidth', 1.5);

% Plot the LiDAR projection points
scatter(imPts(:,1), imPts(:,2), 5, 'k', 'filled');  

% Plot the bbox center points (optional)
plot(T.bb_left_img_x, T.bb_left_img_y, 'ro', 'MarkerFaceColor', 'red', 'MarkerSize', 6);
plot(T.bb_center_img_x, T.bb_center_img_y, 'go', 'MarkerFaceColor', 'magenta', 'MarkerSize', 6);
plot(T.bb_right_img_x, T.bb_right_img_y, 'bo', 'MarkerFaceColor', 'green', 'MarkerSize', 6);

hold off;

