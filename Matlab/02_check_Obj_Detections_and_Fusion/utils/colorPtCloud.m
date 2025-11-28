function ptCloudColored = colorPtCloud(ptCloud,color)
%%A function that takes an input point cloud, and colors all points based
%%on the three element UINT8 vector provided in color
pointscolor=uint8(zeros(ptCloud.Count,3));

pointscolor(:,1)=color(1);
pointscolor(:,2)=color(2);
pointscolor(:,3)=color(3);

ptCloudColored = ptCloud;
ptCloudColored.Color = pointscolor;
end
