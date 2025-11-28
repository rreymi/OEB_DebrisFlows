function point_cloud_on_image(img_folder, ply_folder_full, plot_index, cameraParams, tform)
%   POINT_CLOUD_ON_IMAGE Project a LiDAR point cloud onto a camera image.
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

    %% --- Project point cloud onto image ---
    [imagePoints, indices] = projectLidarPointsOnImage(ptClouds{plot_index}, ...
                                                       cameraParams, tform);

    %% --- Display results ---
    figure('Name', 'Point Cloud Projection');
    imshow(imgs{plot_index}); 
    hold on;

    % Use LiDAR intensity for coloring projected points
    intensity = ptClouds{plot_index}.Intensity(indices);  
    scatter(imagePoints(:,1), imagePoints(:,2), ...
            5, intensity, 'filled');

    % Add colorbar for intensity
    h = colorbar();
    ylabel(h, 'Intensity');
    title(sprintf('LiDAR Projection on Image (Frame %d)', plot_index));
end
