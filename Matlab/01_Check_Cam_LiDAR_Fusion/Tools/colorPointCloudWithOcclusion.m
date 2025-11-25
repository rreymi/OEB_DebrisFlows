function coloredCloud = colorPointCloudWithOcclusion(...
        ptCloud, I, tformCam2Lidar, intrinsics)
    % ptCloud:      pointCloud-Objekt mit LiDAR-Daten
    % I:            HxWx3 RGB-Bild
    % tformCam2Lidar: rigid3d, die LiDAR→Kamera-Extrinsik invertiert (camera→LiDAR)
    % intrinsics:   cameraIntrinsics-Objekt

    % 1) Kameramatrix
    K = intrinsics.IntrinsicMatrix';  % 3×3
    I = imread(I);
    % 2) Bildgröße
    [H, W, ~] = size(I);

    % 3) LiDAR-Punkte in Nx3 double
    ptCloud = pcread(ptCloud);
    pts = ptCloud.Location;  % Nx3

    % 4) Homogene Koordinaten der LiDAR-Punkte
    pts_h = [pts, ones(size(pts,1),1)]';  % 4×N

    % 5) Transform LiDAR→Kamera und Projektionsmatrix
    T_lidar2cam = invert(tformCam2Lidar).T;   % 4×4-Matrix
    P = K * T_lidar2cam(1:3,:);              % 3×4 Projektionsmatrix

    % 6) Projektion aller Punkte
    cam_h = P * pts_h;                       % 3×N
    u_all = cam_h(1,:) ./ cam_h(3,:);
    v_all = cam_h(2,:) ./ cam_h(3,:);
    z_all = cam_h(3,:);

    % 7) Tiefen-Buffer initialisieren
    depthBuffer = inf(H, W);

    % 8) Nur Punkte im Bild und vor der Kamera
    valid = u_all>=1 & u_all<=W & v_all>=1 & v_all<=H & z_all>0;
    u = round(u_all(valid));
    v = round(v_all(valid));
    z = z_all(valid);

    % 9) Z-Buffer füllen (minimale Tiefe je Pixel)
    for k = 1:numel(u)
        row = v(k); col = u(k);
        depthBuffer(row, col) = min(depthBuffer(row, col), z(k));
    end

    % 10) Sichtbarkeits-Check mit Toleranz
    epsDepth = 0.1;  % Toleranz in Metern
    visible = false(size(z));
    for k = 1:numel(u)
        if abs(z(k) - depthBuffer(v(k), u(k))) < epsDepth
            visible(k) = true;
        end
    end

    % 11) Farben zuweisen
    colors = zeros(size(pts), 'uint8');  % Nx3
    idxAll = find(valid);  % Indizes in der Original-Punktwolke
    visIdx = idxAll(visible);

    for i = 1:numel(visIdx)
        pIdx = visIdx(i);
        ui = u(visible(i));
        vi = v(visible(i));
        colors(pIdx, :) = I(vi, ui, :);
    end

    % 12) Neue pointCloud mit RGB zurückgeben
    coloredCloud = pointCloud(pts, 'Color', colors);
end
