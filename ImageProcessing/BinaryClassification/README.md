This directory contains the software used to build and train a machine learing model to perform binary classifications of LWIR images to detect the presence of wildfire hotspots.

clean_dataset is used to generate a dataset of LWIR that are labeled with their ground truth.

BinaryClassification defines models and performs training of a CNN to perfom the binary classification.

original/ Contains raw LWIR images

thresholded/ Contains the same images from original, but all are thresholded to show white pixels where hotspots are present, and black everywhere else.
