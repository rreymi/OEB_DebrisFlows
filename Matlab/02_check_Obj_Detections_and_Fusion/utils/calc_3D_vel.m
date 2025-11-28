function velocity = calc_3D_vel(points, fps)
%CALC_3D_VEL Compute 3D (or 2D) velocity from sequential points
%
% Input:
%   points - Nx3 (or Nx2) array, each row = one time step
%   fps    - frames per second
%
% Output:
%   velocity - (N-1)x1 velocity array

    % If empty or only one point, return empty
    if isempty(points) || size(points,1) < 2
        velocity = [];
        return
    end

    % Compute differences between consecutive points
    xyz1 = points(1:end-1, :);
    xyz2 = points(2:end, :);

    % Euclidean distances
    distances = sqrt(sum((xyz2 - xyz1).^2, 2));

    % Convert to velocity
    velocity = distances * fps;
end
