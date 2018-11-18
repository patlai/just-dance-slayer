# just-dance-slayer

## How to use
1. Download / clone [https://github.com/CMU-Perceptual-Computing-Lab/openpose](openpose) and follow the installation instructions.
2. Clone this repo into the same directory as openpose
3. Download the necessary python packages (watchdog, open cv, numpy)
4. Run script.py with Python 3

## Inspiration
The game "Just Dance"

## What it does
We are using computer vision to teach people how to dance. 

## How we built it
This was built using Python, OpenCV and OpenPose (pose estimation framework developed by CMU). We are taking a user's webcam feed and comparing it to a dance video, calculating the similarity between the two and then outputting a score that the user can see and keep track of
