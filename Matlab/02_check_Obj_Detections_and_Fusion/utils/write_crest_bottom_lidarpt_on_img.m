function write_crest_bottom_lidarpt_on_img(video, img_path, crest_pts, bottom_pts, plot_only)
    
    if ~plot_only
        open(video);
    end
    
    img_frame = imread(img_path);

    imshow(img_frame)
    hold on
    
    scatter(crest_pts(:,1), crest_pts(:,2),'red','filled')
    scatter(bottom_pts(:,1), bottom_pts(:,2),'blue','filled')
    pause(.1)
    hold off
    if ~plot_only
        f = getframe();
        writeVideo(video,f);
    %else
        %pause(0.5)
        %close all
    end
end
