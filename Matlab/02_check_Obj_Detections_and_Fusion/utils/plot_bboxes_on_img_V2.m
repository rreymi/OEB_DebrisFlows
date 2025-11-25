function plot_bboxes_on_img_V2(frame, all_stats, pathImg, ax)
    % Optional: supply an existing axes handle for reuse

    if nargin < 4
        figure;
        ax = axes;
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

    % Fast vectorized rectangle plotting
    for i = 1:size(bboxes, 1)
        rectangle('Position', bboxes(i,:), 'EdgeColor', 'r', 'LineWidth', 1.5, 'Parent', ax);
        text(bboxes(i,1), bboxes(i,2) - 5, ...
            num2str(T.track(i)), ...
            'Color', 'y', 'FontSize', 10, ...
            'FontWeight', 'bold', ...
            'Parent', ax);
    end

    hold(ax, 'off');
end