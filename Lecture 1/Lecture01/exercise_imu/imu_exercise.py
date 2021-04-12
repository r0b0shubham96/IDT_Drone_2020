#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMU exercise
# Copyright (c) 2015-2020 Kjeld Jensen kjen@mmmi.sdu.dk kj@kjen.dk

##### Insert initialize code below ###################

## Uncomment the file to read ##
#fileName = 'imu_razor_data_static.txt'
#fileName = 'imu_razor_data_pitch_55deg.txt'
fileName = 'imu_razor_data_roll_65deg.txt'
#fileName = 'imu_razor_data_yaw_90deg.txt'

## IMU type
#imuType = 'vectornav_vn100'
imuType = 'sparkfun_razor'

## Variables for plotting ##
showPlot = True
plotData = []

## Initialize your variables here ##
myValue = 0.0
fs = 100
nyq = fs / 2
T = 1 / fs

import numpy as np

######################################################

# import libraries
from math import pi, sqrt, atan2
import matplotlib.pyplot as plt

# open the imu data file
f = open(fileName, "r")

# initialize variables
count = 0
angle = 0

# looping through file

for line in f:
	count += 1

	# split the line into CSV formatted data
	line = line.replace ('*',',') # make the checkum another csv value
	csv = line.split(',')

	# keep track of the timestamps 
	ts_recv = float(csv[0])
	if count == 1: 
		ts_now = ts_recv # only the first time
	ts_prev = ts_now
	ts_now = ts_recv

	if imuType == 'sparkfun_razor':
		# import data from a SparkFun Razor IMU (SDU firmware)
		acc_x = int(csv[2]) / 1000.0 * 4 * 9.82
		acc_y = int(csv[3]) / 1000.0 * 4 * 9.82
		acc_z = int(csv[4]) / 1000.0 * 4 * 9.82
		gyro_x = int(csv[5]) * 1/14.375 * pi/180.0
		gyro_y = int(csv[6]) * 1/14.375 * pi/180.0
		gyro_z = int(csv[7]) * 1/14.375 * pi/180.0

	elif imuType == 'vectornav_vn100':
		# import data from a VectorNav VN-100 configured to output $VNQMR
		acc_x = float(csv[9])
		acc_y = float(csv[10])
		acc_z = float(csv[11])
		gyro_x = float(csv[12])
		gyro_y = float(csv[13])
		gyro_z = float(csv[14])
	 		
	##### Insert loop code below #########################

	# Variables available
	# ----------------------------------------------------
	# count		Current number of updates		
	# ts_prev	Time stamp at the previous update
	# ts_now	Time stamp at this update
	# acc_x		Acceleration measured along the x axis
	# acc_y		Acceleration measured along the y axis
	# acc_z		Acceleration measured along the z axis
	# gyro_x	Angular velocity measured about the x axis
	# gyro_y	Angular velocity measured about the y axis
	# gyro_z	Angular velocity measured about the z axis

	## Insert your code here ##

	# 3.2.1
	pitch = atan2(acc_y, sqrt(acc_x**2 + acc_z**2))

	# 3.2.2
	roll = atan2(-acc_x, acc_z)

	# 3.3.1 and 3.3.2
	#angle += gyro_z * T

	# 3.3.3
	angle += (gyro_x) * T

	myValue = angle # relevant for the first exercise, then change this.

	# in order to show a plot use this function to append your value to a list:
	#plotData.append (myValue*180.0/pi)
	plotData.append (myValue)

	######################################################

# closing the file	
f.close()

N = len(plotData)
x = np.linspace(0., N * T, N)

print("mean:", np.mean(plotData))
print("var:", np.var(plotData))

from scipy.fft import fft
from scipy.signal import butter, freqz, lfilter, group_delay


# Frequency analysis
yf = fft(plotData)
xf = np.linspace(0., nyq, N//2)

# Butterworth low-pass filter
order = 5
cutoff = 1
norm_cutoff = cutoff / nyq
b, a = butter(order, norm_cutoff, btype='low', analog=False)
w, h = freqz(b, a, worN=8000)
"""plt.subplot(1, 3, 3)
plt.plot(0.5*fs*w/np.pi, np.abs(h), alpha=0.5)
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko', alpha=0.5)
plt.axvline(cutoff, color='k')
plt.xlim(0, cutoff * 3)
plt.ylim(-0.5, 1.5)
plt.grid()
"""
# Resulting freq
y = lfilter(b, a, plotData)
yf2 = fft(y)
plt.subplot(1, 2, 2)
plt.plot(xf, 2./N * np.abs(yf[0:N//2]), alpha=0.5)
#plt.plot(xf, 2./N * np.abs(yf2[0:N//2]), alpha=0.5)
plt.xlabel
plt.ylabel
plt.legend
plt.grid()



# show the plot
if showPlot == True:
	plt.subplot(1, 2, 1)
	plt.plot(x + 0.5, plotData, alpha=0.5)
	plt.plot(x, y, alpha=0.5)
	plt.grid()
	plt.savefig('imu_exercise_plot.png')
	plt.show()

"""w, gd = group_delay((b, a))
plt.plot(w, gd)
plt.grid()
plt.show()"""

