function [selectedPointsCloud, selectedPointsImage] = selectPointsFromCloudAndImage(ptCloudFolder, imgFolder)

    % Get list of point cloud and image files
    ptCloudFileList = dir(fullfile(ptCloudFolder, '*.ply'));
    imgFileList = dir(fullfile(imgFolder, '*.jpeg'));

    % Sort files by date to ensure correct pairing
    [~, index] = sortrows({ptCloudFileList.date}.');
    ptCloudFileList = ptCloudFileList(index);

    [~, index] = sortrows({imgFileList.date}.');
    imgFileList = imgFileList(index);

    % Ensure the number of point clouds and images match
    numPtClouds = length(ptCloudFileList);
    numImages = length(imgFileList);
    
    if numPtClouds ~= numImages
        error('Mismatch: %d point clouds and %d images found. Ensure they match 1:1.', numPtClouds, numImages);
    end

    % Preallocate storage for selected points
    selectedPointsCloud = cell(1, numPtClouds);
    selectedPointsImage = cell(1, numImages);

    % Loop through each pair of point cloud and image
    for i = 1:numPtClouds
        ptCloudFile = fullfile(ptCloudFileList(i).folder, ptCloudFileList(i).name);
        imgFile = fullfile(imgFileList(i).folder, imgFileList(i).name);

        fprintf('Processing %d/%d: %s <-> %s\n', i, numPtClouds, ptCloudFileList(i).name, imgFileList(i).name);

        [sel_pts_cloud, sel_pts_img] = selectLidarAndImagePoints(ptCloudFile, imgFile);
        selectedPointsCloud{i} = pointCloud(sel_pts_cloud);
        selectedPointsImage{i} = sel_pts_img;
    end
end

function [selectedPointsCloud, selectedPointsImage] = selectLidarAndImagePoints(ptCloudFile, imgFile)

    % Load or generate a point cloud
    % Replace with your own point cloud data
    ptCloud = pcread(ptCloudFile);

    % Load an image
    image = imread(imgFile); 


    % Initialize storage for selected points
    selectedPointsCloud = [];
    selectedPointsImage = [];

    % Create figure for point cloud
    figureHandleCloud = figure('Name', 'Point Cloud');
    pcshow(ptCloud);
    title('Click on points in the point cloud');
    xlabel('X');
    ylabel('Y');
    zlabel('Z');
    hold on;

    % Create figure for image
    figureHandleImage = figure('Name', 'Image');
    imshow(image);
    title('Adjust pan/zoom. Select corresponding point after cloud point.');
    hold on;

    % Enable pan and zoom in the image figure
    zoomHandle = zoom(figureHandleImage);
    panHandle = pan(figureHandleImage);
    set(zoomHandle, 'Enable', 'on');
    set(panHandle, 'Enable', 'on');

    % Initialize the data cursor mode
    datacursormode(figureHandleCloud, 'off'); % Start with it off

    while isvalid(figureHandleCloud) && isvalid(figureHandleImage)

        % Select point in point cloud
        figure(figureHandleCloud);
        zoom on; pan on;
        disp('Adjust zoom/pan. Press ENTER when ready to select a point in the point cloud.');
        pause;  
        zoom off; pan off;

        disp('Click on a point in the point cloud.');

        % Enable data cursor mode for accurate 3D point selection
        %dcm = datacursormode(figureHandleCloud);
        %datacursormode on;
        %waitforbuttonpress;  % Wait for user input
        % Wait for a point to be selected in the point cloud
        try
            figure(figureHandleCloud);
            dcm = datacursormode(figureHandleCloud);
            datacursormode on;
            waitforbuttonpress;
        catch
            if ~isvalid(figureHandleCloud)
                disp('Point cloud figure closed. Exiting.');
                break;
            end
        end

        info = getCursorInfo(dcm);
        if isempty(info)
            disp('No valid point selected in the point cloud.');
            continue;
        end

        pointCloud = info.Position; % Get the selected 3D point
        selectedPointsCloud = [selectedPointsCloud; pointCloud]; %#ok<AGROW>

        % Mark the selected point with a **larger red dot**
        hold on;
        scatter3(pointCloud(1), pointCloud(2), pointCloud(3), 100, 'r', 'filled'); % Larger marker
        drawnow;  % Force immediate update of the figure
        disp(['Selected Point in Cloud: ', mat2str(pointCloud)]);

        % Select corresponding point in image
        figure(figureHandleImage);
        zoom on; pan on;
        disp('Adjust zoom/pan. Press ENTER when ready to select a point in the image.');
        pause;
        zoom off; pan off;

        disp('Now, click on the corresponding point in the image.');
        hold on;

        try
            [xi, yi] = ginput(1); % Select one point
            selectedPointsImage = [selectedPointsImage; xi, yi]; %#ok<AGROW>

            % Mark the selected point with a **large red cross**
            plot(xi, yi, 'rx', 'LineWidth', 2, 'MarkerSize', 12);
            drawnow;
            disp(['Selected Point in Image: ', mat2str([xi, yi])]);
        catch
            disp('Image point selection canceled.');
            break;
        end
    end


end