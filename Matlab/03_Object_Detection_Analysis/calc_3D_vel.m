function velocity = calc_3D_vel(points, time_steps)
%CALC_3D_VEL Compute 3D (or 2D) velocity using actual time steps
%
% Input:
%   points      - Nx3 (or Nx2) positions
%   time_steps  - Nx1 absolute time values in seconds
%
% Output:
%   velocity - (N-1)x1 velocity array in units/second

    % handle too few points
    if isempty(points) || size(points,1) < 2
        velocity = [];
        return
    end

    % ensure time_steps has correct length
    if length(time_steps) ~= size(points,1)
        error('time_steps must have same length as points');
    end

    % compute distances
    xyz1 = points(1:end-1, :);
    xyz2 = points(2:end, :);
    distances = sqrt(sum((xyz2 - xyz1).^2, 2));

    % compute time differences
    dt = time_steps(2:end) - time_steps(1:end-1);

    % avoid division by zero if identical timestamps occur
    if any(dt == 0)
        warning('Some time steps are zero; setting velocity to NaN for those intervals.');
    end

    % velocity = distance / Δt
    velocity = distances ./ dt;
end


% --> FEHLER!! 

% mit fps = 10 geht man davon aus dass immer nur ein ldr frame zwischen den
% punkten sind. Zumteil werden aber frames geskipped. --> Zu hohe
% Geschwindigkeiten sind das Resultat.


% function velocity = calc_3D_vel(points, fps)
% 
% %CALC_3D_VEL Compute 3D (or 2D) velocity from sequential points
% %
% % Input:
% %   points - Nx3 (or Nx2) array, each row = one time step
% %   fps    - frames per second
% %
% % Output:
% %   velocity - (N-1)x1 velocity array
% 
% % If empty or only one point, return empty
% if isempty(points) || size(points,1) < 2
%     velocity = [];
%     return
% end
% 
% % Compute differences between consecutive points
% xyz1 = points(1:end-1, :);
% xyz2 = points(2:end, :);
% 
% % Euclidean distances
% distances = sqrt(sum((xyz2 - xyz1).^2, 2));
% 
% % Convert to velocity
% velocity = distances * fps;
% end
