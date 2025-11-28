function [tracks] = find_frame_index_cut_tracks(tracks, start_frame, end_frame)
%FRAMES_TO_DISPLAY  Find indices of frames closest to start and end frames
%
%   [idx_start, idx_end] = frames_to_display(tracks, start_frame, end_frame)
%
%   Inputs:
%       tracks      - table containing a column 'frame_number'
%       start_frame - scalar value indicating desired starting frame
%       end_frame   - scalar value indicating desired ending frame
%
%   Outputs:
%       idx_start   - index of first row where frame number is closest to start_frame
%       idx_end     - index of last row where frame number is closest to end_frame

    % Extract frame numbers
    frame_numbers = tracks.frame_number;

    % Get unique frame numbers (sorted)
    unique_frames = unique(frame_numbers);

    % ---- Find closest start frame ----
    [~, idx_closest_start] = min(abs(unique_frames - start_frame));
    frame_closest_start = unique_frames(idx_closest_start);
    idx_start = find(frame_numbers == frame_closest_start, 1, 'first');

    % ---- Find closest end frame ----
    [~, idx_closest_end] = min(abs(unique_frames - end_frame));
    frame_closest_end = unique_frames(idx_closest_end);
    idx_end = find(frame_numbers == frame_closest_end, 1, 'last');


     % ---- Cut the table ----
    tracks = tracks(idx_start:idx_end, :);

end
