function sync_time_stamps(path_to_timestamp_file, path_to_save_sync)
% improved version, Roman August 2025

% Load data
timestamps = readtable(path_to_timestamp_file);

is_img = timestamps.pose_or_img == "img";
is_pose = timestamps.pose_or_img == "pose";

% Get indices of poses and images
pose_idx = find(is_pose);
img_idx = find(is_img);

% Map each pose to the NEXT image index using interpolation
next_img_idx = interp1(img_idx, img_idx, pose_idx, 'next', 'extrap');

% Remove invalid matches (poses after last image)
valid = ~isnan(next_img_idx);
pose_idx = pose_idx(valid);
next_img_idx = next_img_idx(valid);

% Extract synced data
poses_nr = timestamps.nr(pose_idx);
imgs_nr = timestamps.nr(next_img_idx);
timestamp_ldr = timestamps.timestamp(pose_idx);
timestamp_img = timestamps.timestamp(next_img_idx);

% Create and save output table
synced_timestamps = table(poses_nr, imgs_nr, timestamp_ldr, timestamp_img, ...
    'VariableNames', {'frame_ldr','frame_img','timestamp_ldr','timestamp_img'});
writetable(synced_timestamps, path_to_save_sync);

% Print confirmation
fprintf("saved sync file to %s with %i poses\n", path_to_save_sync, height(synced_timestamps));

end