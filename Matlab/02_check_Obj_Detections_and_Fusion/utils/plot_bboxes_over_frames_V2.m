function plot_bboxes_over_frames_V2(all_stats, trackID, pathImg, pause_time)
%Visualizes BBOXES of a TrackID across all frames it appears in
%
%   Inputs:
%       all_stats  - Table containing object tracking statistics
%       trackID    - Track ID to visualize
%       pathImg    - Folder path storing image frames
%       pause_time - (optional) Pause in seconds between frames
%
%   The function:
%       • loads each image for the given track
%       • draws its bounding box(es)
%       • updates the figure without reopening it
%       • plays frames in correct chronological order
%

if nargin < 4
    pause_time = 0.1; % default pause

end


% rows for the selected track
T = all_stats(all_stats.track == trackID, :);
if isempty(T)
    error('TrackID %d not found in all_stats.', trackID);
end

% All frames for this track (sorted)
frameNumbers = unique(T.frame);

%% 01 Setup Figure and Axes

fig = figure('Name', sprintf('Tracking of TrackID %d', trackID), ...
    'NumberTitle', 'off');

ax = axes('Parent', fig);
imgHandle = imshow([], 'Parent', ax);   % placeholder image
hold(ax, 'on');                         % keep rectangles on top

rectHandles = gobjects(0);              % storage for rectangle objects


%% === 02 Loop Through All Frames
nFrames = numel(frameNumbers);

for i = 1:nFrames
    frameID = frameNumbers(i);

    % Load image
    imgFile = fullfile(pathImg, sprintf('%06d.jpeg', frameID));

    if ~isfile(imgFile)
        warning('Image not found: %s', imgFile);
        continue;
    end

    img = imread(imgFile);

    % Update the displayed image
    set(imgHandle, 'CData', img);

    % Remove previous rectangles
    if ~isempty(rectHandles)
        delete(rectHandles);
    end

    % Select bbox rows for this frame
    Tf = T(T.frame == frameID, :);
    nBboxes = height(Tf);

    rectHandles = gobjects(nBboxes, 1);

    % Draw bounding boxes
    for j = 1:nBboxes
        bbox = [Tf.bb_left(j), Tf.bb_top(j), Tf.bb_width(j), Tf.bb_height(j)];
        rectHandles(j) = rectangle('Position', bbox, ...
            'EdgeColor', 'r', ...
            'LineWidth', 1.5);
    end

    % Update title
    title(ax, sprintf('Frame %d   (%d / %d)', frameID, i, nFrames));

    % Refresh UI
    drawnow;

    % Optional pause
    if pause_time > 0
        pause(pause_time);
    end
end

hold(ax, 'off');

end