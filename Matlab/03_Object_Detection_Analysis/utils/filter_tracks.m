function tracks_to_display = filter_tracks(tracks, tracks_to_display_setting, min_track_length)
    
    % Select which tracks to display based on config settings

    % Show all tracks that are longer than the minimum length 
    if strcmp(tracks_to_display_setting, 'all')

        all_tracks = tracks.track_id;

        % Find unique track IDs and an index vector for mapping
        [uniqueValues, ~, idx] = unique(all_tracks);

        % Count how many times each unique track ID appears
        counts = histcounts(idx, 1:max(idx));

        % Find the indices of tracks that are long enough
        indices = find(counts > min_track_length);

        % Get the actual track IDs that meet the length requirement
        tracks_to_display = uniqueValues(indices);
    else
        tracks_to_display = tracks_to_display_setting;
    end