function plot_bboxes_on_img(frame, all_stats, pathImg, ax, highlightTrackID)
    % Optional: supply an existing axes handle for reuse

    if nargin < 4
        figure;
        ax = axes;
    end

    if nargin < 5
        highlightTrackID = [];  % default: no track highlighted
    end

    T = all_stats(all_stats.frame == frame, :);

    % Load image
    img_file = fullfile(pathImg, sprintf('%06d.jpeg', frame));
    img_frame = imread(img_file);

    % Show image (only once per frame)
    imshow(img_frame, 'Parent', ax);
    hold(ax, 'on');


    if isempty(T)
        title(ax, sprintf('Frame %d (no tracks)', frame));
        hold(ax, 'off');
        return;
    end

    % Extract bounding boxes
    bboxes = [T.bb_left, T.bb_top, T.bb_width, T.bb_height];

    % Plot rectangles and track IDs
    for i = 1:size(bboxes, 1)
        if ~isempty(highlightTrackID) && T.track(i) == highlightTrackID
            % Highlight special track
            rectColor = 'g';        % green for special track
            lineWidth = 3;
            textColor = 'c';        % cyan for track label
        else
            % Normal tracks
            rectColor = 'r';
            lineWidth = 1.5;
            textColor = 'y';
        end

        rectangle('Position', bboxes(i,:), 'EdgeColor', rectColor, 'LineWidth', lineWidth, 'Parent', ax);
        text(bboxes(i,1), bboxes(i,2) - 5, ...
            num2str(T.track(i)), ...
            'Color', textColor, 'FontSize', 10, ...
            'FontWeight', 'bold', ...
            'Parent', ax);
    end


    hold(ax, 'off');
end