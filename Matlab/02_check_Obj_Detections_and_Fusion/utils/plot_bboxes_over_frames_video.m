function plot_bboxes_over_frames_video(tracks, img_path, pause_time, save_path, video_name)
%plot_bboxes_over_frames Display frames with bounding boxes and save video
%
%   plot_bboxes_over_frames(tracks, img_path)
%   plot_bboxes_over_frames(tracks, img_path, pause_time)
%   plot_bboxes_over_frames(tracks, img_path, pause_time, save_path, video_name)
%
%   Inputs:
%       tracks      - table with columns:
%                     track_id, frame_number_img, bb_left, bb_top, bb_width, bb_height
%       img_path    - folder with image frames
%       pause_time  - pause between frames (default 0.1s)
%       save_path   - folder to save rendered frames (default: 'rendered_frames/')
%       video_name  - output video file name (default: 'tracking_output.mp4')

    if nargin < 3, pause_time = 0.1; end
    if nargin < 4, save_path = "rendered_frames"; end
    if nargin < 5, video_name = "tracking_output.mp4"; end

    % Ensure save directory exists
    if ~isfolder(save_path)
        mkdir(save_path);
    end

    % --- Create figure ---
    fig = figure('Name','Tracking of bbox','NumberTitle','off');
    ax = axes;
    img_handle = imshow([], 'Parent', ax);
    hold(ax, 'on');

    rect_handles = gobjects(0);

    % --- Determine unique frames ---
    frame_numbers = unique(tracks.frame_number_img);

    % --- Prepare video writer ---
    video_file = fullfile(save_path, video_name);
    v = VideoWriter(video_file, 'MPEG-4');  % or 'Motion JPEG AVI'
    v.FrameRate = 1 / pause_time;
    open(v);

    % --- Loop through frames ---
    for i = 1:numel(frame_numbers)
        frame = frame_numbers(i);

        % Load image
        img_file = fullfile(img_path, sprintf('%06d.jpeg', frame));
        if ~isfile(img_file)
            warning('Image not found: %s', img_file);
            continue;
        end
        img = imread(img_file);

        % Update displayed image
        set(img_handle, 'CData', img);

        % Remove old rectangles
        if ~isempty(rect_handles)
            delete(rect_handles);
        end

        % Tracks in frame
        tracks_in_frame = tracks(tracks.frame_number_img == frame, :);

        % Draw bounding boxes
        rect_handles = gobjects(size(tracks_in_frame, 1), 1);
        for j = 1:size(tracks_in_frame, 1)
            bbox = [tracks_in_frame.bb_left(j), tracks_in_frame.bb_top(j), ...
                    tracks_in_frame.bb_width(j), tracks_in_frame.bb_height(j)];
            rect_handles(j) = rectangle('Position', bbox, ...
                                        'EdgeColor', 'r', 'LineWidth', 1.5);
        end

        title(ax, sprintf('Frame %d (%d/%d)', frame, i, numel(frame_numbers)));
        drawnow;

        % --- Save current frame as image ---
        frame_image_path = fullfile(save_path, sprintf('%06d.png', frame));
        exportgraphics(fig, frame_image_path, 'Resolution', 300);

        % --- Add frame to video ---
        writeVideo(v, getframe(fig));

        % Pause
        if pause_time > 0
            pause(pause_time);
        end
    end

    % Finish video
    close(v);
    hold(ax, 'off');

    fprintf("Saved frames to: %s\n", save_path);
    fprintf("Video created: %s\n", video_file);
end
