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

## Challenges we ran into
We did not have enough GPU power to run our app at a "playable" frame rate. As a result, we cannot demo our app. We were also trying to get use the AWS credits for GPU computing but nobody would help us.

## Accomplishments that we're proud of
We were able to put everything together and have our project work on a desktop computer with a powerful GPU

## What we learned
Bring and external GPU to the next hackathon or get our hands on cloud computing resources beforehand if we want to work on ML/CV intensive tasks.

## What's next for Just Dance Slayer
We will continue to develop it and try to make the application less GPU intensive so more people can use it (maybe use another pose estimation framework)
