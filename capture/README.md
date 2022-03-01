This directory contains the software used in our experiments to capture images. The capture program displays a stream from a Seekware LWIR camera and captures a collection of images on command. 


This software is designed to run on a Raspberry Pi.

Dependencies:
  OpenCV

To build:
  mkdir build
  cd build
  cmake ..
  cmake --build .
