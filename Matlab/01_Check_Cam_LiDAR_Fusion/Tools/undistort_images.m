%% Script to undistort the images from the OEB Livecamera
% searches all the images in the 01_RawData folder and saves
% undistored images in the 02_PreProcessedData/undistorted_images folder
%
% Roman, August 2025
clc
clear all 
close all

%% EVENT data

event_year = "2024";
event_month = "07";
event_day = "01c";

station = "Chalberspissi";
sensor = "Karlsson";

%% PATHS

path_0 = "\\tiliva\eg\01_Projects\01_Ambizione\UncompressData\OEB\Events\2024";

% path to camera params
load("\\d.ethz.ch\users\all\rrenner\Desktop\MA_OEB_scripts\cameraParams.mat");

% path to event
path_event = fullfile(path_0, sprintf("%s_%s_%s", event_year, event_month, event_day), station);

% path to distorted images
path_d = fullfile(path_event, "01_RawData/images");

% path to undistorted images
path_ud = fullfile(path_event, "02_PreProcessedData/undistorted_images");

% Get list of JPEG files
files = dir(fullfile(path_d, "*.jpeg")); % if no output, check if file extension is correct

% Make sure output folder exists
if ~exist(path_ud, "dir")
    mkdir(path_ud);
end

%% Loop through files

parfor k = 1:numel(files)
    % Read image
    inFile = fullfile(path_d, files(k).name);
    I = imread(inFile);

    % Undistort
    J = undistortImage(I, cameraParams);

    % Save to output folder (keep same filename)
    outFile = fullfile(path_ud, files(k).name);
    imwrite(J, outFile);

    fprintf("Saved undistorted image: %s\n", outFile);
end
 