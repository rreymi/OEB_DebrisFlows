function tracks_to_display = filter_tracks(tracks, tracks_to_display_setting, min_track_length)

    if strcmp('all',tracks_to_display_setting)
        all_tracks = tracks.track_id;
        [uniqueValues, ~, idx] = unique(all_tracks);
        counts = histcounts(idx, 1:max(idx));
        indices = find(counts > min_track_length);
        u = uniqueValues(indices);
        tracks_to_display = u;
    else
        tracks_to_display = tracks_to_display_setting;
    end