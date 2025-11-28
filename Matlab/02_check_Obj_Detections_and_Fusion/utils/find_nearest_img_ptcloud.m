function [nearest_img, nearest_ptcloud] = find_nearest_img_ptcloud(x, y, imPts, ptCloudimg)
    
    % nearest_img: closest lidar point in img coords
    % nearest_ptcloud: closest lidar point in ptcloud coords (x,y,z)

    distances = sqrt(sum(([x,y] - imPts).^2, 2));
    [~, index] = min(distances);
    nearest_img = imPts(index,:);
    nearest_ptcloud = select(ptCloudimg,index);
    nearest_ptcloud = nearest_ptcloud.Location;

end