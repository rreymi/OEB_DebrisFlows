function plot_selected_points(sel_ptCloud, sel_img, ptCloud_path, img_path, i)
%   PLOT_SELECTED_POINTS Visualize selected 3D points in a point cloud and their 
%   corresponding 2D projections in an image.
%
%   sel_ptCloud : cell array of selected 3D point clouds
%   sel_img     : cell array of selected 2D image points
%   ptCloud_path: file path to the full point cloud
%   img_path    : file path to the image
%   i           : index of the frame to plot

    % Load data
    ptCloud = pcread(ptCloud_path);   % Load point cloud
    img     = imread(img_path);       % Load image
    
    % Extract selected 3D points for the given frame
    points3D = sel_ptCloud{1,i}.Location;

    if isempty(points3D)
        warning('No points to plot for frame %d', i);
        return
    end

    % Assign unique colors for each selected point
    nPoints = size(points3D,1); 
    colors  = lines(nPoints);

    %% --- Plot 3D points on point cloud ---
    figure('Name', 'Point Cloud');
    pcshow(ptCloud);
    xlabel('X'); ylabel('Y'); zlabel('Z');
    hold on;

    % Overlay selected 3D points
    scatter3(points3D(:,1), points3D(:,2), points3D(:,3), ...
             100, colors, 'filled');

    %% --- Plot 2D points on image ---
    figure('Name', 'Image');
    imshow(img); hold on;
    points2D = sel_img{1,i};

    % Overlay selected 2D points
    scatter(points2D(:,1), points2D(:,2), ...
            100, colors, 'filled');
end
    
