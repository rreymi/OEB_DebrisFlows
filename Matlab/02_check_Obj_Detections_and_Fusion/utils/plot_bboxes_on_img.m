% function plot_bboxes_on_img(frame, tracks, img_path)
%     figure
%     img_frame = imread(fullfile(img_path,sprintf('%06d.jpeg',frame)));
% 
%     tracks_in_frame = tracks(tracks.frame_number_img==frame,:); % find all trackIDs within frame number
% 
%     bboxes = [tracks_in_frame.bb_left,tracks_in_frame.bb_top,tracks_in_frame.bb_width,tracks_in_frame.bb_height]; % bboxes for one object
% 
%     imshow(img_frame)
% 
%     hold on
% 
%     for i=1:size(bboxes,1)
%         showShape("rectangle", bboxes(i,:),Label=tracks_in_frame.track_id(i))
%     end


function plot_bboxes_on_img(frame, tracks, img_path, ax)
    % Optional: supply an existing axes handle for reuse

    if nargin < 4
        figure;
        ax = axes;
    end

    % Load image
    img_file = fullfile(img_path, sprintf('%06d.jpeg', frame));
    img_frame = imread(img_file);

    % Show image (only once per frame)
    imshow(img_frame, 'Parent', ax);
    hold(ax, 'on');

    % Select tracks for this frame
    tracks_in_frame = tracks(tracks.frame_number_img == frame, :);
    
    if isempty(tracks_in_frame)
        title(ax, sprintf('Frame %d (no tracks)', frame));
        hold(ax, 'off');
        return;
    end

    % Extract bounding boxes
    bboxes = [tracks_in_frame.bb_left, ...
              tracks_in_frame.bb_top, ...
              tracks_in_frame.bb_width, ...
              tracks_in_frame.bb_height];

    % Fast vectorized rectangle plotting
    for i = 1:size(bboxes, 1)
        rectangle('Position', bboxes(i,:), 'EdgeColor', 'r', 'LineWidth', 1.5, 'Parent', ax);
        text(bboxes(i,1), bboxes(i,2) - 5, ...
            num2str(tracks_in_frame.track_id(i)), ...
            'Color', 'y', 'FontSize', 10, ...
            'FontWeight', 'bold', ...
            'Parent', ax);
    end

    hold(ax, 'off');
end
