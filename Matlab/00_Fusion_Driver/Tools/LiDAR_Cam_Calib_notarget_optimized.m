function [tform, inlierIdx, tformCam2World] = LiDAR_Cam_Calib_notarget_optimized(LiDARPts, ImgPts, intrinsics)%, seed)


% LiDAR_Cam_Calib_notarget_optimized
% Robust LiDAR-to-camera extrinsic calibration using RANSAC.
%
% Inputs:
%   LiDARPts   - 1xN cell array of pointCloud objects (LiDAR)
%   ImgPts     - 1xN cell array of 2D points (image correspondences)
%   intrinsics - cameraIntrinsics object
%   seed       - (optional) integer to fix random seed
%
% Outputs:
%   tform          - rigid3d object LiDAR->Camera transform
%   inlierIdx      - indices of inlier points used by RANSAC
%   tformCam2World - rigid3d object Camera->World transform (before inversion)

    %% 0) Fix random seed if provided
    % if nargin >= 4
    %     rng(seed);
    % else
    %     rng(0);  % default seed
    % end

    %% 1) Concatenate LiDAR points
    allLiDAR = cellfun(@(pc) pc.Location, LiDARPts, 'UniformOutput', false);
    LiDARPoints = vertcat(allLiDAR{:});

    %% 2) Concatenate image points
    allImg = vertcat(ImgPts{:});
    imagePoints = double(allImg);

    %% 3) Estimate camera pose using RANSAC
    [worldOrientation, worldLocation, inlierIdx] = estimateWorldCameraPose(...
        imagePoints, LiDARPoints, intrinsics, ...
        'MaxReprojectionError', 2, ...
        'Confidence',       99.9, ...
        'MaxNumTrials',     10000);

    %% 4) Create Camera->World transform
    tformCam2World = rigid3d(worldOrientation, worldLocation);

    %% 5) Invert for LiDAR->Camera transform
    tform = invert(tformCam2World);

end
