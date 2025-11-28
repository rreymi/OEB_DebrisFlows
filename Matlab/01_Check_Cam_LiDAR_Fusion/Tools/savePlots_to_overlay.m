function savePlots_to_overlay(idx, pts, z, ims, fri, exportDir)

    % --- Get native image size ---
    [h, w, ~] = size(ims{idx});   % h = 1200, w = 1900

    % --- Create invisible figure in exact image size ---
    fig = figure('Visible','off','Units','pixels', ...
                 'Position',[100 100 w h], ...
                 'MenuBar','none','ToolBar','none', 'Color','white');

    % --- Create axes that fill figure with NO border ---
    ax = axes(fig, 'Units','normalized','Position',[0 0 1 1]);
    ax.Visible = 'off';       % no ticks, no axes lines
    axis(ax,'off');           % turn off all axes visuals
    hold(ax,'on');

    % --- Show image pixel-perfect ---
    imshow(ims{idx}, 'Parent', ax, 'Border','tight');

    % --- Overlay scatter points ---
    scatter(ax, pts{idx}(:,1), pts{idx}(:,2), 10, z{idx}, 'filled');

    % --- Lock axes  to image size ---
    axis(ax,'ij');
    ax.DataAspectRatio = [1 1 1];
    ax.XLim = [0.5 w+0.5];
    ax.YLim = [0.5 h+0.5];

    % --- Export image resolution ---
    filename = fullfile(exportDir, sprintf('frame_%i.jpg', fri(idx)));
    exportgraphics(fig, filename, ...
                   'Resolution', 96, ...
                   'ContentType','image', ...
                   'BackgroundColor','white');
    close(fig);
end