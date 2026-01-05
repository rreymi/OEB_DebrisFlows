``` mermaid
  flowchart TD

A[Config file config_YYYY_MM_DD.mat] --> B
C[Camera calibration cameraParams] --> B
D[Camera-LiDAR transform tform] --> B
E[Frame sync table image-LiDAR] --> B
F[Object tracks bboxes and IDs] --> G
H[LiDAR point clouds PLY files] --> J

B[Load config and calibration] --> G

G[Load and filter tracks] --> I

I[Unique synced frames] --> J

J[For each frame parfor] --> K
K[Load LiDAR point cloud] --> L
L[Interpolate and crop point cloud] --> M
M[Project LiDAR to image plane] --> N

N{For each bounding box} --> O
O[Select LiDAR points in bbox] --> P
P[Find nearest LiDAR points center left right] --> Q

Q[Store per frame results] --> R
R[Merge results per track] --> S
S[Velocity calculation] --> U
R --> T[Grain size calculation]

U --> V[Assemble per track tables]
T --> V
V[Concatenate all tracks all_stats] --> W[Save output MAT file]

V[Concatenate all tracks all_stats] --> W[Save output MAT file]





