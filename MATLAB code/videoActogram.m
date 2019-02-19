function frameData = videoActogram(videoFile,frameInterval,resizePx)
% Quantifies changes in pixel values from a video; a surrogate Actogram.
%
%
% Inputs:
%    videoFile - path to [MATLAB compatible format] video
%    frameInterval - skip frames; speed execution by setting this > 1
%    resizePx - resize the video to this pixel size; smaller = faster
%
% Outputs:
%    frameData - m x n matrix where m = frame number, ...
%       n(1) = frame being analyzed
%       n(2) = frame timestamp (in seconds)
%       n(3) = mean change in pixel values from previous frame
% 
frameData = [];
v = VideoReader(videoFile);

v.CurrentTime = 5;
frame = readFrame(v);
v.CurrentTime = 0;

% re-read video at t = 0
v = VideoReader(videoFile);

% prompt user for ROI
frame = imresize(frame,[resizePx NaN]);
h = figure;
imshow(frame);
% select region
hrect = impoly; % rectangle
% hrect = impoly;
% pos = getPosition(hrect);
mask = hrect.createMask;
close(h);
% allFrames = [];
iFrame = 1;
ii = 0;
prevFrame = [];
h = waitbar(0,'Processing actogram...');
while hasFrame(v)
    frame = readFrame(v);
    if mod(ii,frameInterval) ~= 0
        ii = ii + 1;
        continue;
    end
    waitbar(v.CurrentTime/v.Duration,h);
    frame = imresize(frame,[resizePx NaN]);
    frame(~repmat(mask, 1, 1, 3)) = 0; 

    frame = rgb2gray(frame);

    frameData(iFrame,1) = ii + 1;
    frameData(iFrame,2) = ii / v.FrameRate;
    frameData(iFrame,3) = 0;
    if ~isempty(prevFrame)
%         This is Main part i.e. finding abs difference in the frames
        frameData(iFrame,3) = abs(mean2(frame - prevFrame));
    end
    
    prevFrame = frame;
    iFrame = iFrame + 1;
    ii = ii + 1;
end
close(h);