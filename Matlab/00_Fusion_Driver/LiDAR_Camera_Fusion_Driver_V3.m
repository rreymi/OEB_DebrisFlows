%{
script to perform lidar-camera calibration based on features seleted in
both coordinate systems
Jacob Hirschberg, April 2025

adapted Roman Renner, August 2025
 %}

clc 
clear all
close all

%% Step 0: PATHS

if ~exist(fullfile(pwd,"temp"), 'dir')
    mkdir("temp")
end

% Define File paths --> CHANGE !!!
addpath('Tools')
addpath('temp')


%ptCloudFileFolder = 'Data/LiDAR'; % calibration .mat files
%imgFileFolder = 'Data/Cam'; % calibration images .jpg file
%imgFormat = 'jpeg';

IMG_raw_folder = "Data/Cam/raw";
IMG_undistorted_folder = "Data/Cam/undistorted";
ptcloud_full_folder = "Data/LiDAR/PLY_Full";
ptcloud_interp_folder = "Data/LiDAR/PLY_interp";

cam = 'Data/cameraParams.mat';
load(cam);

%% Step 1:  INTERPOLATE Ptclouds

numframes = length(dir(fullfile(IMG_undistorted_folder, '*.jpeg')));

xlim = [-20, 15];
ylim = [-20, 20];
zlim = 3;
spacing = 0.05;

for ii = 1:numframes
    % Interpolate the point cloud
    [ptcloud_interp, F] = interpolatePointCloudToEvenSpacingCameraLimits( ...
        pcread(fullfile(ptcloud_full_folder,sprintf("%d.ply", ii))), ...
        spacing, zlim, xlim, ylim);
    
    % Save the interpolated point cloud
    pcwrite(ptcloud_interp, fullfile(ptcloud_interp_folder,sprintf("%d.ply", ii)));

end


%% Step 1 - optional: LOAD previously selected points

C = load('selectedPointsCloud.mat');
selectedPointsCloud = C.selectedPointsCloud;
I = load('selectedPointsImage.mat');
selectedPointsImage = I.selectedPointsImage;
clear C I 

%% Setp 2: SELECT corresponding points in ptCloud and image

% brittle tool but works :) when done with selecting points of one
% img/ptcloud pair, close both figures, click in command window and hit
% ENTER

% --- !! % 'replace' oder 'append' neue Punkte anhängen oder firsch anfangen

% not interpolated ptclouds
[selectedPointsCloud, selectedPointsImage] = selectPointsFromCloudAndImage_mode(ptcloud_full_folder, IMG_undistorted_folder, 'append');



%% Step 3: PLOT selected points

i = 2; % img nr.
ptCloudPath = fullfile(ptcloud_full_folder,sprintf("%d.ply", i));
imgPath = fullfile(IMG_undistorted_folder, sprintf("%i.jpeg", i));

plot_selected_points(selectedPointsCloud, selectedPointsImage, ptCloudPath, imgPath, i)



%% Step 4: DELETE points?

img_nr = 1;  % frame index
pt_nr  = 4;  % point index to delete

% Delete from image points
img_points = selectedPointsImage{img_nr};  % extract the numeric array
img_points(pt_nr,:) = [];                  % delete the row
selectedPointsImage{img_nr} = img_points;  % assign back

% Delete from point cloud
pc_data = selectedPointsCloud{img_nr}.Location; % extract points
pc_data(pt_nr,:) = [];                          % delete the row
selectedPointsCloud{img_nr} = pointCloud(pc_data);

%% Step 4a: SAVE after deleting points 
%  
save temp/selectedPointsCloud selectedPointsCloud
save temp/selectedPointsImage selectedPointsImage

%% ADD points from earlier selection

% if you want to add points from an earlier selection, load them here
% 
selectedPointsCloud2 = load("temp\selectedPointsCloud_xxx??.mat");
selectedPointsImage2 = load("temp\selectedPointsImage_xxx??.mat");
% 
% % concatenate cell arrays. check if it works!!!
selectedPointsCloud = {selectedPointsCloud, selectedPointsCloud2};
selectedPointsImage = {selectedPointsImage, selectedPointsImage2};

selectedPointsCloud = [selectedPointsCloud{1}, selectedPointsCloud{2}.selectedPointsCloud];
selectedPointsImage = [selectedPointsImage{1}, selectedPointsImage{2}.selectedPointsImage];

%% Step 5: FUSE Lidar and Camera

% select the pictures for the analysis
imgIndices = [1, 2];

% creates new structure with cooridnates for ptCloud and Images
selectedPointsImageIDX = selectedPointsImage(imgIndices);
selectedPointsCloudIDX = selectedPointsCloud(imgIndices);



tform = LiDAR_Cam_Calib_notarget_optimized(selectedPointsCloudIDX,selectedPointsImageIDX,cameraParams.Intrinsics);

save(fullfile('temp','estimated_tform.mat'),'tform');
disp('tform saved')


%% CHECK calibration results

%project LiDAR points on image
c = 2;

point_cloud_on_image(IMG_undistorted_folder, ptcloud_full_folder, c, cameraParams.Intrinsics,tform)

%diplay colored point cloud
plot_colored_point_cloud(IMG_undistorted_folder, ptcloud_full_folder, c, cameraParams.Intrinsics,tform)