function plot_bboxes_over_frames(tracks, img_path, pause_time)
%plot_bboxes_over_frames  Display sequence of frames with bounding boxes
%
%   play_tracks_over_frames(tracks, img_path)
%   play_tracks_over_frames(tracks, img_path, pause_time)
%
%   Inputs:
%       tracks      - table with columns:
%                     track_id, frame_number, bb_left, bb_top, bb_width, bb_height
%       img_path    - folder path containing image frames (e.g. 'images/')
%       pause_time  - optional pause between frames in seconds (default = 0.05)
%
%   The function reuses one figure window and smoothly updates the
%   displayed image and bounding boxes for each frame.

    


    if nargin < 3
        pause_time = 0.1; % default pause
    end

    % --- Create figure and axes once ---
    fig = figure('Name','Tracking of bbox','NumberTitle','off');
    ax = axes;
    img_handle = imshow([], 'Parent', ax);
    hold(ax, 'on');

    rect_handles = gobjects(0); % store rectangles for each frame

    % --- Determine unique frames ---
    frame_numbers = unique(tracks.frame_number_img);

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

        % Update the displayed image
        set(img_handle, 'CData', img);

        % Remove previous rectangles
        if ~isempty(rect_handles)
            delete(rect_handles);
        end

        % Select tracks for this frame
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

        % Pause between frames (optional)
        if pause_time > 0
            pause(pause_time);
        end
    end

    hold(ax, 'off');
    %close(fig)
end

