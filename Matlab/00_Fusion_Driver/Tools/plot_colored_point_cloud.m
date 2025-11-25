function plot_colored_point_cloud(img_folder, ply_folder_full, plot_index, cameraParams, tform)
%   PLOT_COLORED_POINT_CLOUD Fuse image colors onto a LiDAR point cloud 
%   and visualize both the original and colored point cloud.
%
%   img_folder     : folder containing images (.jpeg)
%   ply_folder_full: folder containing point clouds (.ply)
%   plot_index     : index of the frame to plot
%   cameraParams   : camera intrinsic parameters
%   tform          : rigid transformation from LiDAR to camera

    %% --- Load all images ---
    imgFiles = dir(fullfile(img_folder, '*.jpeg'));
    numImgs  = numel(imgFiles);
    imgs     = cell(1, numImgs);

    for k = 1:numImgs
        imgs{k} = imread(fullfile(imgFiles(k).folder, imgFiles(k).name));
    end

    %% --- Load all point clouds ---
    plyFiles = dir(fullfile(ply_folder_full, '*.ply'));
    numPly   = numel(plyFiles);
    ptClouds = cell(1, numPly);

    for k = 1:numPly
        ptClouds{k} = pcread(fullfile(plyFiles(k).folder, plyFiles(k).name));
    end

    %% --- Fuse camera colors onto point cloud ---
    % Apply camera–LiDAR calibration
    ptCloudColored = fuseCameraToLidar(imgs{plot_index}, ...
                                       ptClouds{plot_index}, ...
                                       cameraParams, invert(tform));

    %% --- Plot results ---
    figure('Name', 'Colored Point Cloud Fusion');
    pcshow(ptClouds{plot_index}, 'MarkerSize', 10);   % Original cloud
    hold on;
    pcshow(ptCloudColored, 'MarkerSize', 100);        % Colored cloud
    title(sprintf('Point Cloud Fusion (Frame %d)', plot_index));
end