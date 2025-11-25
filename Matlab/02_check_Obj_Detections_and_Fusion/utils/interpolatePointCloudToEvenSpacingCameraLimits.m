function [interpolatedPtCloud,F] = interpolatePointCloudToEvenSpacingCameraLimits(ptCloud,spacing,zCutoff,xLim,yLim)
%%A function to create a scattered interpolant of an input point cloud, and
%%generate interpolated values based on an input spacing

warning_id = 'MATLAB:scatteredInterpolant:DupPtsAvValuesWarnId';
warning('off',warning_id)

xyz = double(ptCloud.Location);
x = xyz(:,1);
y=xyz(:,2);
z=xyz(:,3);
F = scatteredInterpolant(x,y,z);
F.Method = 'linear';
F.ExtrapolationMethod = 'none';

[Xq,yQ] = meshgrid(xLim(1):spacing:xLim(2),yLim(1):spacing:yLim(2));
Zq = F(Xq,yQ);

ptCloudData = [Xq(:),yQ(:),Zq(:)];
ptCloudData = ptCloudData(ptCloudData(:,3)<zCutoff,:);
% ptCloudData = ptCloudData(ptCloudData(:,2)>0,:);

interpolatedPtCloud = pointCloud(ptCloudData);
cmatrix = ones(size(interpolatedPtCloud.Location)).*[1 1 1];
interpolatedPtCloud = pointCloud(ptCloudData,'Color',cmatrix);

end