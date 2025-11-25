function write_bbox_lidarpt_on_img(video, img_path, lidar_img_points, bbox, points)
    
    open(video);
    
    img_frame = imread(img_path);

    imshow(img_frame)
    hold on
    scatter(lidar_img_points(:,1), lidar_img_points(:,2),5,'k','filled')
    showShape("rectangle", bbox)
    for i=1:size(points,1)
        plot(points(i,1), points(i,2), 'b.', 'MarkerSize',20)
    end
    pause(.1)
    hold off
    f = getframe();
    writeVideo(video,f);
end
