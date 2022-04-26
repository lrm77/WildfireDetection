# Authors: Luke Majors, Colin Pollard, Ian Lavin
# ECE 6990 - Computational Photography
# Wildfire Demarcation Algorithm Project
# This is used to separate our source data into different
# folders based on the altitude at which each image was 
# captured.

import sys
import os
import shutil

# Dictionary mapping each folder name to an altitude
folderAlt = {
    "FlightCapture_21-11-19_17-01-26-400": "2000ft",
    "FlightCapture_21-11-19_17-05-17-200": "2000ft",
    "FlightCapture_21-11-19_17-08-24-800": "2000ft",
    "FlightCapture_21-11-19_17-15-31-0": "1000ft",
    "FlightCapture_21-11-19_17-19-24-200": "1000ft",
    "FlightCapture_21-11-19_17-22-10-600": "1000ft",
    "FlightCapture_21-11-19_17-29-12-200": "500ft",
    "FlightCapture_21-11-19_17-32-03-600": "500ft",
    "FlightCapture_21-11-19_17-34-52-200": "500ft",
    "FlightCapture_21-11-19_17-45-18-600": "2000ft",
}

srcPath = '/Users/lukemajors/19 Nov 2021 Flight #2 KBMC Linear Targets/'

# Save list of all test images
threshPath = 'thresholded/'
origPath = 'original/'
data = os.listdir(threshPath)
print("Thresholded Size: " + str(len(data)))
print("Original Size: " + str(len(os.listdir(origPath))))

# Loop through all source files to check where each test image came from
# Save each test image into separate directory from its altitude group
for folder in folderAlt:
	dir = os.listdir(srcPath + folder)
	alt = folderAlt[folder]

	thresholded = 'thresholded' + alt + '/'
	original = 'original' + alt + '/'

	# Check if new folders exists yet, if not create them
	if not os.path.exists(thresholded):
		os.makedirs(thresholded)

	if not os.path.exists(original):
		os.makedirs(original)

	for f in dir:
		if f in data:
			shutil.copyfile(threshPath + f, thresholded + f)
			shutil.copyfile(origPath + f, original + f)

# Test to make sure all images were moved properly
threshCount = 0
origCount = 0
for alt in ['500ft', '1000ft', '2000ft']:
	thresh = 'thresholded' + alt + '/'
	orig = 'original' + alt + '/'
	threshCount += len(os.listdir(thresh))
	origCount += len(os.listdir(orig))
	print(thresh + " Size: " + str(len(os.listdir(thresh))))
	print(orig + " Size: " + str(len(os.listdir(orig))))	

print("\nTotals:\nThresholded: " + str(threshCount) +"\nOriginal: " + str(origCount))