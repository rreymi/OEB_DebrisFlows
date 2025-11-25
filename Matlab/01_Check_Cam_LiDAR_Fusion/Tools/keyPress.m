% Define key press function and update plot function
function keyPress(~, event, xy_imPts, z_imPts, imgs, frames_ldr, frames_img)
    persistent idx
    if isempty(idx)
        idx = 1;
    end

    switch event.Key
        case 'rightarrow'
            idx = mod(idx, numel(xy_imPts)) + 1;
        case 'leftarrow'
            idx = mod(idx - 2, numel(xy_imPts)) + 1;
        otherwise
            return;
    end

    updatePlot(idx, xy_imPts, z_imPts, imgs, frames_ldr, frames_img);
end