function [crest_loc, bottom_loc] = get_wave_crest(ptcloud, img_pixels, bbox)
    %
    % Input
    %   - img_pixels: image pixel coordinates
    %   - ptcloud: interpolated point cloud
    %   - spacing: spacing used for ptcloud
    %   - poi: point of interest around which lines are chosen (e.g. bbox mid
    %   point) [x y z]
    %   - num_lines: number of lines along y-axis to consider for heigth
    %   estimate
    %
    % Output
    %   - crest_loc: in lidar coords
    %   - bottom_loc: in lidar coords
    %
    % Notes
    %   -
    
    kb = 3; % movmean params, should be fine
    kf = 3; % movmean params, should be fine
    y_window = 20; % bbox size in pointcloud max this size in m in y-direction
    plot_lines = false;
    
    %% draw new bounding box, half as wide and twice as long (?)
    new_bbox_width = 0.5 * bbox(3);
    new_bbox_height = 2 * bbox(4);
    new_bbox_x = bbox(1) + 0.5 * new_bbox_width;
    new_bbox_y = bbox(2);
    new_bbox = [new_bbox_x, new_bbox_y, new_bbox_width, new_bbox_height];

    %% select new point cloud
    [points]=bbox2points(new_bbox);
    xv=points(:,1);
    yv=points(:,2);
    in_box = inpolygon(img_pixels(:,1),img_pixels(:,2),xv,yv);
    %indices=indices_all(in_box);
    
    % select points from bounding box
    object = select(ptcloud,in_box);

    % make object +/- rectangular in x-y space
    y_max = quantile(object.Location(:,2),0.999); % to remove some outliers
    object_sub = object.Location(object.Location(:,2) > y_max-1,:); % look at lower 1 m
    x_max = max(object_sub(:,1));
    x_min = min(object_sub(:,1));
    object2 = object.Location(object.Location(:,1) >= x_min,:);
    object2 = object2(object2(:,1) <= x_max,:);

    % shorten in y-direction
    y_min = y_max - y_window;
    object2 = object2(object2(:,2) >= y_min,:);
    object2 = pointCloud(object2);

    %% find lines along y-axis
    [lines_x, ~, idx] = unique(object2.Location(:,1));
    lines = {};
    for i=1:size(lines_x,1)
        line = object2.Location(idx == i,:);
        line = sortrows(line, 2);
        if size(line,1) > 50 % only chose line if more than 50 points
            lines{end+1} = line;
        end
    end
    
    %% do derivatievs (dz/dy) for lines
    
    % make matrix
    num_lines = size(lines,2);
    max_length = 0;
    for i=1:num_lines
        l = size(lines{i},1);
        if l>max_length
            max_length = l;
        end
    end

    lines_x = zeros(max_length, num_lines);
    lines_y = zeros(max_length, num_lines);
    lines_z = zeros(max_length, num_lines);

    for i = 1:num_lines
        line = lines{i};
        l = size(line,1);
        
        lines_x(1:l,i) = line(:,1);
        lines_y(1:l,i) = line(:,2);
        lines_z(1:l,i) = line(:,3);

        lines_x(l+1:end,i) = NaN;
        lines_y(l+1:end,i) = NaN;
        lines_z(l+1:end,i) = NaN;
    end

    % first derivative
    lines_z_smoothed = movmean(lines_z, [kb, kf]);
    if num_lines > 1
        [~,dz] = gradient(lines_z_smoothed);
        [~,dy] = gradient(lines_y);
    elseif num_lines <= 1
        dz = gradient(lines_z_smoothed);
        dy = gradient(lines_y);
    end
    dz_dy = dz./dy;
    
    % second derivative, note that the 2nd derivative is calculated for a
    % smoothed dz_dy
    dz_dy_smoothed = movmean(dz_dy,[kb kf]);
    if num_lines > 1
        [~,d2z] = gradient(dz_dy_smoothed);
    elseif num_lines <= 1
        d2z = gradient(dz_dy_smoothed);
    end
    d2z_dy2 = d2z ./ dy;

      %% find crest and bottom
    % find max in d2z_dyz
    % first zero upstream is crest
    % first zero downstream is bottom
    
    % the max of the first derivative is the steepest part of the wave
    [~, idx_max_dz_dy] = max(dz_dy);
    
    % find crest
    % the crest is where the second derivative goes back to ~0
    crest_loc =zeros(num_lines,3);
    all_indices = 1:length(d2z_dy2);
    for i=1:num_lines
        % best starting point is the min of second drivative
        [~, idx_min_d2z_dy2] = min(d2z_dy2(:,i));

        %crest_candidates = d2z_dy2(idx_max_dz_dy(i):end,i);
        %crest_candidates_idx = all_indices(idx_max_dz_dy(i):end);
        crest_candidates = d2z_dy2(idx_min_d2z_dy2:end,i);
        crest_candidates_idx = all_indices(idx_min_d2z_dy2:end);
        
        [~,idx_min] = min(crest_candidates);
        if not(idx_min == length(crest_candidates))
            curr_gradient = -99;
            curr_value = -99;
            curr_idx = 1;
            while (curr_gradient < 0) && (curr_value < 0) && (curr_idx < length(crest_candidates_idx)-1) % stops as soon as one of these conditions is not true anymore
                curr_idx = curr_idx + 1;
                curr_gradient =  crest_candidates(curr_idx) - crest_candidates(curr_idx+1);
                curr_value = crest_candidates(curr_idx);
            end
            
            if curr_idx >= length(crest_candidates_idx)-1
                crest_loc(i,1) = NaN;
                crest_loc(i,2) = NaN;
                crest_loc(i,3) = NaN;
            else
                crest_idx_inall = crest_candidates_idx(curr_idx-1);
                crest_loc(i,1) = lines_x(crest_idx_inall,i);
                crest_loc(i,2) = lines_y(crest_idx_inall,i);
                crest_loc(i,3) = lines_z(crest_idx_inall,i);
            end
        else
            crest_loc(i,1) = NaN;
            crest_loc(i,2) = NaN;
            crest_loc(i,3) = NaN;
        end
    end

    %find bottom
    bottom_loc =zeros(num_lines,3);
    for i=1:num_lines
        % best starting point is the max of second drivative
        [~, idx_max_d2z_dy2] = max(d2z_dy2(:,i));

        %bottom_candidates = d2z_dy2(1:idx_max_dz_dy(i),i);
        %bottom_candidates_idx = all_indices(1:idx_max_dz_dy(i));
        bottom_candidates = d2z_dy2(1:idx_max_d2z_dy2,i);
        bottom_candidates_idx = all_indices(1:idx_max_d2z_dy2);
        
        [~,idx_max] = max(bottom_candidates);
        if not(idx_max == 1)
            curr_gradient = 99;
            curr_value = 99;
            curr_idx = length(bottom_candidates);
            while (curr_gradient > 0) && (curr_value > 0) && (curr_idx > 2) % stops as soon as one of these conditions is not true anymore
                curr_idx = curr_idx - 1;
                %curr_gradient = bottom_candidates(curr_idx) - bottom_candidates(curr_idx-1);
                curr_value = bottom_candidates(curr_idx);
            end

            if curr_idx <= 2
                bottom_loc(i,1) = NaN;
                bottom_loc(i,2) = NaN;
                bottom_loc(i,3) = NaN;
            else
                %bottom_idx = max(find(bottom_candidates < 0)+1);
                bottom_idx_inall = bottom_candidates_idx(curr_idx+1);
                bottom_loc(i,1) = lines_x(bottom_idx_inall,i);
                bottom_loc(i,2) = lines_y(bottom_idx_inall,i);
                bottom_loc(i,3) = lines_z(bottom_idx_inall,i);
            end
        else
            bottom_loc(i,1) = NaN;
            bottom_loc(i,2) = NaN;
            bottom_loc(i,3) = NaN;
        end
    end

    %% plot, for debgging
    if plot_lines
        figure
        for ii=1:num_lines
            subplot(3,1,1)
            %plot(lines_y(:,ii), lines_z(:,ii),'r')
            plot(lines_y(:,ii), lines_z_smoothed(:,ii), 'LineWidth', 0.5, 'Color', 'k')
            hold on
            plot(lines_y(bottom_idx_inall,ii),lines_z_smoothed(bottom_idx_inall,ii),'o', 'Color', 'blue')
            plot(lines_y(crest_idx_inall,ii),lines_z_smoothed(crest_idx_inall,ii),'o', 'Color', 'red')
            
            subplot(3,1,2)
            hold on
            plot(lines_y(:,ii), dz_dy(:,ii), 'LineWidth', 0.5, 'Color', 'k')
            plot(lines_y(idx_max_dz_dy(ii),ii),max(dz_dy(:,ii)),'o', 'Color', 'red')
            
            subplot(3,1,3)
            plot(lines_y(:,ii), d2z_dy2(:,ii), 'LineWidth', 0.5, 'Color', 'k')
            hold on
            yline(0,'k')
            plot(lines_y(bottom_idx_inall,ii), d2z_dy2(bottom_idx_inall,ii),'o', 'Color', 'blue')
            plot(lines_y(crest_idx_inall,ii), d2z_dy2(crest_idx_inall,ii),'o', 'Color', 'red')
        end
    end

end