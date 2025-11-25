function project_ptcloud_on_img_video(allStats, pathIMG, pathPtCloud, cameraParams, tform, spacing, zCutoff, xLim, yLim, fps, save_path, video_name)
%PROJECT_PTCLOUD_ON_IMG_VIDEO
%   Loops through all frames in allStats, plots LiDAR points over images
%   with bounding boxes and keypoints, saves each frame, and creates a video.
%
% Inputs:
%   allStats      - table with columns: frame, frame_number_ldr, track, bb_left, bb_top, bb_width, bb_height, bb_left_img_x, bb_left_img_y, bb_center_img_x, bb_center_img_y, bb_right_img_x, bb_right_img_y
%   pathIMG       - folder with image frames
%   pathPtCloud   - folder with LiDAR PLY files
%   cameraParams  - camera parameters struct
%   tform         - transformation from LiDAR to camera
%   spacing, zCutoff, xLim, yLim - interpolation/filtering parameters
%   pause_time    - pause between frames (default 0.3)
%   save_path     - folder to save images (default 'Output_ptcloud_on_img')
%   video_name    - output video file name (default 'ptcloud_on_img.mp4')

    if nargin < 10, fps = 10; end
    if nargin < 11, save_path = 'Data/Output_videos/Output_ptcloud_on_img'; end
    if nargin < 12, video_name = 'ptcloud_on_img.mp4'; end

    % Ensure save directory exists
    if ~isfolder(save_path)
        mkdir(save_path);
    end

    % Unique frames to iterate
    frames_img = unique(allStats.frame);

    % Create figure and axes once
    fig = figure('Name','Bbox + LiDAR on Img','NumberTitle','off', ...
        'Position',[10 10 1920 1080], ...
        'ToolBar', 'none', ...
        'MenuBar', 'none');

    ax = axes('Parent', fig);
    img_handle = imshow([], 'Parent', ax);
    
    %img_handle = imshow(imread(fullfile(pathIMG, sprintf('%06d.jpeg', frames_img(1)))), 'Parent', ax);  % initialize with real image
    hold(ax, 'on');



    % Placeholder graphics handles
    rect_handles = gobjects(0);
    scatter_handle = [];
    left_handle = [];
    center_handle = [];
    right_handle = [];

    % Prepare video writer
    video_file = fullfile(save_path, video_name);
    v = VideoWriter(video_file, 'MPEG-4');
    v.FrameRate = fps;
    v.Quality = 80;
    open(v);

    % --- Loop over frames ---
    for k = 1:numel(frames_img)
        frameImg = frames_img(k);

        % Extract rows for this frame
        T = allStats(allStats.frame == frameImg, :);
        if isempty(T), continue; end

        frameLdr = T.frame_number_ldr(1);

        % --- Load & interpolate LiDAR ---
        filePath = fullfile(pathPtCloud, sprintf('%05d.ply', frameLdr));
        if ~isfile(filePath)
            warning('PLY not found: %s', filePath);
            continue;
        end
        ptCloudRaw = pcread(filePath);
        [ptcloud_interpol, ~] = interpolatePointCloudToEvenSpacingCameraLimits(ptCloudRaw, spacing, zCutoff, xLim, yLim);
        ptcloud_interpol = colorPtCloud(ptcloud_interpol, [255 255 255]);

        % Project LiDAR points onto image
        [imPts, ~] = projectLidarPointsOnImage(ptcloud_interpol, cameraParams.Intrinsics, tform);

        % --- Load image ---
        img_file = fullfile(pathIMG, sprintf('%06d.jpeg', frameImg));
        if ~isfile(img_file), continue; end
        img = imread(img_file);
        set(img_handle, 'CData', img);

        % --- Remove old graphics ---
        if ~isempty(rect_handles), delete(rect_handles); end
        if ~isempty(scatter_handle), delete(scatter_handle); end
        if ~isempty(left_handle), delete(left_handle); end
        if ~isempty(center_handle), delete(center_handle); end
        if ~isempty(right_handle), delete(right_handle); end

        % --- Draw bounding box ---
        rect_handles = gobjects(height(T),1);
        for j = 1:height(T)
            bbox = [T.bb_left(j), T.bb_top(j), T.bb_width(j), T.bb_height(j)];
            rect_handles(j) = rectangle('Position', bbox, 'EdgeColor', 'b', 'LineWidth', 1.5, 'Parent', ax);
        end

        % --- Plot LiDAR points ---
        scatter_handle = scatter(ax, imPts(:,1), imPts(:,2), 5, 'k', 'filled');

        % --- Plot bbox keypoints ---
        left_handle   = plot(ax, T.bb_left_img_x, T.bb_left_img_y, 'ro', 'MarkerFaceColor', 'red', 'MarkerSize', 6);
        center_handle = plot(ax, T.bb_center_img_x, T.bb_center_img_y, 'go', 'MarkerFaceColor', 'magenta', 'MarkerSize', 6);
        right_handle  = plot(ax, T.bb_right_img_x, T.bb_right_img_y, 'bo', 'MarkerFaceColor', 'green', 'MarkerSize', 6);

        % Title
        title(ax, sprintf('Frame %d (%d/%d)', frameImg, k, numel(frames_img)));
        drawnow;

        % --- Save current frame ---
        frame_image_path = fullfile(save_path, sprintf('%06d.png', frameImg));
        exportgraphics(fig, frame_image_path, 'Resolution', 150);

        % --- Add frame to video ---
        writeVideo(v, getframe(fig));
    end

    % Finish video
    close(v);
    hold(ax, 'off');

    fprintf('Saved frames to: %s\n', save_path);
    fprintf('Video created: %s\n', video_file);
end
