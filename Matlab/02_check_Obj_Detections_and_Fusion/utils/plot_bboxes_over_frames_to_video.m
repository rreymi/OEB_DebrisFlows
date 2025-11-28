function plot_bboxes_over_frames_to_video(all_stats, trackID, pathImg, fps, save_path, video_name)

if nargin < 4 || isempty(fps)
    fps = 10;
end
if nargin < 5, save_path = 'Data/Output_videos'; end

if nargin < 6, video_name = 'bbox_track_video.mp4'; end

% Ensure save directory exists
if ~isfolder(save_path)
    mkdir(save_path);
end


%% 00 Handle inputs


T = all_stats(all_stats.track == trackID, :);
if isempty(T)
    error('TrackID %d not found.', trackID);
end

frameNumbers = unique(T.frame);
nFrames = numel(frameNumbers);

%% 01 Setup Video Writer (HIGH QUALITY)
video_file = fullfile(save_path, video_name);
v = VideoWriter(video_file, 'MPEG-4');
v.FrameRate = fps;
v.Quality   = 95;   % for MPEG-4
open(v);

fprintf('Writing video to: %s\n', video_file);

%% 02 Setup Figure
fig = figure('Name', sprintf('Track %d', trackID), ...
             'NumberTitle','off', ...
             'Color','w', ...
             'Units','pixels', ...
             'Position',[20 20 1792 1008]);  % full HD

% 2. Create axes that fill the entire figure
ax = axes('Parent', fig, ...
          'Units', 'normalized');  % hide axes ticks


imgHandle = imshow([], 'Parent', ax);
hold(ax, 'on');

rectHandles = gobjects(0);

%% 03 Loop Through All Frames
for i = 1:nFrames
    frameID = frameNumbers(i);

    % Load the image
    imgFile = fullfile(pathImg, sprintf('%06d.jpeg', frameID));
    if ~isfile(imgFile)
        warning('Missing image: %s', imgFile);
        continue;
    end

    img = imread(imgFile);
    set(imgHandle, 'CData', img);

    % Remove old rectangles
    if ~isempty(rectHandles)
        delete(rectHandles);
    end

    % Select bbox rows for this frame
    Tf = T(T.frame == frameID, :);
    nBoxes = height(Tf);
    rectHandles = gobjects(nBoxes, 1);

    % Draw bounding boxes
    for j = 1:nBoxes
        bbox = [Tf.bb_left(j), Tf.bb_top(j), Tf.bb_width(j), Tf.bb_height(j)];
        
        rectHandles(j) = rectangle('Position', bbox, ...
                                   'EdgeColor', 'red', ...
                                   'LineWidth', 2);
    end

    title(ax, sprintf('Track %d — Frame %d (%d/%d)', ...
                      trackID, frameID, i, nFrames), ...
                      'FontSize', 14);

    drawnow;

    % Capture frame to video (what you see on screen)
    frameRGB = getframe(fig);
    writeVideo(v, frameRGB);
end

%% 04 Finish
close(v);
fprintf('Video saved: %s\n', save_path);

end
