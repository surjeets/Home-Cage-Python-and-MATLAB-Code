
clear
clc
% setting up the file pathes and parameters
addpath(genpath('chronux_2_11')); 

% loading video file and time stamps and 
videoFilepath = 'E:\Users\mmlab\Documents\Data\2019-01-16_13-53-22_Sia\Test_04_15fps.mp4';
videoTimepath = 'E:\Users\mmlab\Documents\Data\2019-01-16_13-53-22_Sia\Pi1_pts_02_15fps.csv';
emgpath = 'E:\Users\mmlab\Documents\Data\2019-01-16_13-53-22_Sia\EMG1.ncs';
eventpath = 'E:\Users\mmlab\Documents\Data\2019-01-16_13-53-22_Sia\Events.nev';

Fs_vid = 15;       % video sampling rate
Fs_emg = 4000;     % emg sampling rate
emg_perctile = 60; % percentile of emg values used for thresholding
vid_perctile = 60; % percentile of video values used for thresholding
rec_length = 24;   % recording length in hour
frameInterval = 1;  
resizePx = 900;

% passing arguments to videoActogram function
frameData = videoActogram(videoFilepath,frameInterval,resizePx);

%% if you observe periodic peaks after every 60 samples (this is due to 60Hz noise)
% % when choosing 'frameInterval = 1' THEN you need to filter the signal
% filter video-based movement signal below .1 Hz using zero-lag Chebychev filter
[z2,p2,k2] = cheby1(2,0.3,2*.1/Fs_vid,'low');
[sos2,g2] = zp2sos(z2,p2,k2);
video_signal_filtered = filtfilt(sos2, g2, frameData(:,3));

% detrending the video_based movement signal
video_signal_filtered_det = locdetrend(video_signal_filtered, Fs_vid, [10 5]); % 10/5 sec moving window

% calculating the RMS of video_based movement signal 
video_signal_pw = video_signal_filtered_det.^2;
rect_ker  = ones(1,20*Fs_vid)/(20*Fs_vid); 
vid_rms = conv(video_signal_pw, rect_ker, 'same');

%% Load and processing EMG data %%

[emg_raw, Header] = Nlx2MatCSC(emgpath, [0 0 0 0 1], 1, 1); % loading raw emg
bitVoltValue_str = strsplit(Header{17});             % finding bit value of emg singal in millivolt
bitVoltValue = str2num(bitVoltValue_str{2})*1000;
emg_raw = reshape(emg_raw, 1, [])*bitVoltValue;

% find the timing of onset of Picamera recording and trim the emg accordingly
TimeStamps = Nlx2MatEV(eventpath, [1 0 0 0 0], 0, 1);
video_start_sample = floor((TimeStamps(2)-TimeStamps(1))*1e-6*Fs_emg);
emg_raw = emg_raw(video_start_sample:end);

% filtering emg signal between 90 and 1000 Hz using zero-lag Chebychev filter
[z2,p2,k2] = cheby1(4,0.3,2*[90 1000]/Fs_emg,'bandpass');
[sos2,g2] = zp2sos(z2,p2,k2);
emg_filt = filtfilt(sos2, g2, emg_raw);
% calculating the RMS of emg signal 
emg_pw = emg_filt.^2;
rect_ker  = ones(1,20*Fs_emg)/(20*Fs_emg); 
emg_rms = conv(emg_pw, rect_kr, 'same');
% downsampling the emg rms signal to 100 Hz
emg_rms = downsample(emg_rms, 40);
Fs_emg = Fs_emg/40;

t_emg = (1:rec_length*3600*Fs_emg)/Fs_emg; % calculate the emg timing
emg_rms = emg_rms(1:length(t_emg));        % trim the emg


%%
% loading video time stamp and trim the end after 24 hrs
t_vid = csvread(videoTimepath);
t_vid = t_vid'/1e6;
t_vid = t_vid(1:rec_length*3600*Fs_vid);
vid_rms = transpose(vid_rms(1:length(t_vid)));

emg_rms_interp = interp1(t_emg, emg_rms, t_vid); % interpolate the emg signal on the video time stamps

% thresholding the emg and video signal to determine the sleep period
thr_emg = prctile(emg_rms_interp, thr_emg);
thr_vid = prctile(vid_rms, thr_vid);
sleep_emg = double(emg_rms_interp < emg_perctile);
sleep_vid = double(vid_rms < vid_perctile);

% removeing <40 sec sleep epochs
rect_ker = ones(1,80*Fs_vid)/(80*Fs_vid);
sleep_vid = conv(sleep_vid, rect_ker, 'same');
sleep_vid = double(sleep_vid > .5);
sleep_emg = conv(sleep_emg, rect_ker, 'same');
sleep_emg = double(sleep_emg > .5);

accuracy = sum(sleep_vid==sleep_emg)/length(sleep_vid)  % accuracy of video scoring in comparison to emg signal scoring




