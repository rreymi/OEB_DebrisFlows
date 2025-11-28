function make_bbox_video(frames, tracks, path_ptcloud, cameraParams, tform, spacing, zCutoff, xLim, yLim, outputVideoPath)
%MAKE_BBOX_VIDEO  Render multiple frames of reproj_bboxes_on_ptcloud into a video
%
% Inputs:
%   frames - Vector of frame numbers to visualize, e.g. 1:10
%   tracks - Table with bounding boxes and track info
%   outputVideoPath - Path to save the video (e.g. 'output.avi')

    % Create video writer
    v = VideoWriter(outputVideoPath, 'MPEG-4');
    v.FrameRate = 5;  % adjust speed (frames per second)
    open(v);

    % Prepare figure
    fig = figure('Name', 'BBox Projection Video', 'Color', 'w');
    ax = axes('Parent', fig);
    
    % Fix viewpoint parameters (define once)
    fixedView = [45 20];  % azimuth, elevation
    campos([0, 0, 30]);   % camera position in 3D (tune)
    camtarget([0, 0, 0]); % where camera points
    camup([0 0 1]);       % keep z-axis up

    for i = 1:length(frames)
        frame = frames(i);
        fprintf('Rendering frame %d of %d\n', i, length(frames));

        % Get bounding boxes for this frame
        bboxes = tracks(tracks.frame_number_img == frame, ...
                        {'bb_left','bb_top','bb_width','bb_height'});

        % Skip if none
        if isempty(bboxes)
            continue;
        end

        % Render frame (reuse your function)
        reproj_bboxes_on_ptcloud(frame, bboxes, path_ptcloud, cameraParams, tform, spacing, zCutoff, xLim, yLim);

        % Fix camera view for consistency
        view(ax, fixedView);

        % Capture frame
        frameImage = getframe(fig);
        writeVideo(v, frameImage);
    end

    close(v);
    close(fig);

    fprintf('✅ Video saved to %s\n', outputVideoPath);
end
