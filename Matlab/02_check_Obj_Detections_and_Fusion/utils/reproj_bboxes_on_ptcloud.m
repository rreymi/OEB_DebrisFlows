function reproj_bboxes_on_ptcloud(points_in_frame, bboxes, path_ptcloud, cameraParams, tform, spacing, zCutoff, xLim, yLim)
%REPROJ_BBOXES_ON_PTCLOUD  Project 2D bounding boxes onto LiDAR point cloud
%
% Inputs:
%   frame        - Frame number (e.g., 42)
%   bboxes       - Table or Nx4 matrix [bb_left, bb_top, bb_width, bb_height]
%   path_ptcloud - Path to folder with .ply files
%   cameraParams - Camera parameters with .Intrinsics
%   tform        - Geometric transformation (LiDAR -> Camera)
%   ax           - (Optional) Axes handle for reusing existing figure


    id = bboxes.track_id;
    frame_ldr = bboxes.frame_number_ldr;
    frame_img = bboxes.frame_number_img;
    
    fig1 = figure('Name', sprintf('Frame %d - Point Cloud', frame_img));
    ax = axes;
    
    % Load and color full point cloud
    file_path = fullfile(path_ptcloud, sprintf('%05d.ply', frame_ldr));
    ptcloud = pcread(file_path);
    
    [ptcloud_interpol,~] = interpolatePointCloudToEvenSpacingCameraLimits(ptcloud,spacing,zCutoff,xLim,yLim);
    
    ptcloud = colorPtCloud(ptcloud_interpol, [255 255 255]);
    
    % Project LiDAR points to image
    [imPts, indices_all] = projectLidarPointsOnImage(ptcloud, cameraParams.Intrinsics, tform);
    ptCloudimg = select(ptcloud, indices_all);
    
    % Prepare list of points to highlight
    in_box = false(size(indices_all));
    
    bboxes = [bboxes.bb_left,bboxes.bb_top,bboxes.bb_width,bboxes.bb_height];
    
    for i = 1:size(bboxes, 1)
        bbox = bboxes(i, :);
        pts = bbox2points(bbox);
        xv = pts(:,1);
        yv = pts(:,2);
        in_box = in_box | inpolygon(imPts(:,1), imPts(:,2), xv, yv);
    end
    
    % Select object points once
    objectPts = select(ptCloudimg, in_box);
    objectPts = colorPtCloud(objectPts, 255*[0 0.4470 0.7410]);
    
    cla(ax);  % Clear previous contents

    % 1. Plot full LiDAR point cloud
    pcshow(ptcloud, 'Parent', ax, 'MarkerSize', 15);
    hold(ax, 'on');
    
    % 2. Highlight points inside bbox
    pcshow(objectPts, 'Parent', ax, 'MarkerSize', 40);  % bigger dots for bbox region
    
    % 3. Plot your special points (center, left, right)
    scatter3(points_in_frame{1}(1), points_in_frame{1}(2), points_in_frame{1}(3), 40, 'red', 'filled'); % left
    scatter3(points_in_frame{2}(1), points_in_frame{2}(2), points_in_frame{2}(3), 40, 'magenta', 'filled'); % center
    scatter3(points_in_frame{3}(1), points_in_frame{3}(2), points_in_frame{3}(3), 40, 'green', 'filled'); % right
    
    % 4. Add title, labels, and maybe improve visibility
    title(ax, sprintf('Frame img %d - TrackID %d', frame_img, id));
    xlabel(ax, 'X'); ylabel(ax, 'Y'); zlabel(ax, 'Z');
    grid(ax, 'on');
    hold(ax, 'off');

    drawnow;
    
end