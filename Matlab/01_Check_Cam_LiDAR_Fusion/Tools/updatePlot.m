% Define plot update function
function updatePlot(idx, pts, z, ims, frl, fri)

    % Check if dataset has points
    if isempty(pts{idx})
        clf;
        title(sprintf('Dataset %d is empty or invalid', idx));
        return;
    end

    % Plot image
    clf;
    imshow(ims{idx});
    hold on;

    % Overlay points
    scatter(pts{idx}(:,1), pts{idx}(:,2), 6, z{idx}, 'filled');

    % Title with frame info
    title(sprintf('PtCloud %i & IMG %i', frl(idx), fri(idx)), 'Interpreter', 'none');
end