import json
import os
import _thread
import multiprocessing
import time
import logging
import math
import sys

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
from demo_bpm_extract import get_file_bpm

videoOutputPath = "../output/video_out"
webcamOutputPath = "../output/webcam_out"

videoPath = ""
testVideoPath = ""
userWebcamFeedCommand = "../build/examples/openpose/openpose.bin --net_resolution -1x80 -model_pose COCO -write_json %s" %(webcamOutputPath)
showVideoCommand = "../build/examples/openpose/openpose.bin --net_resolution -1x80 --output_resolution -1x80 -model_pose COCO --write_json %s --video " %(videoOutputPath)
bmpComand = "aubio tempo -i"

poseCorrectnessThreshold = 100.0
poseNotDetectedThreshold = 800.0
bodyParts = []
webcamPose = {}
videoPose = {}
poseError = []

class CustomHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global webcamPose, videoPose
        #print(f'event type: {event.event_type}  path : {event.src_path}')
        #print(event.src_path)
        json = readJSON(event.src_path)
        poses = parsePoseData(json)
        if (len(poses) > 0):
            # prettyPrintPoseData(poses[0])
            if webcamOutputPath in event.src_path:
                #print("***updating webcam pose")
                webcamPose = poses[0]
            elif videoOutputPath in event.src_path:
                #print("***updating video pose")
                videoPose = poses[0]

            calculatePoseError(webcamPose, videoPose, poseCorrectnessThreshold, poseNotDetectedThreshold, 'Nose')

def monitorPathForChanges(path):
    before = dict ([(f, None) for f in os.listdir (path)])
    while 1:
        time.sleep (0.1)
        after = dict ([(f, None) for f in os.listdir (path)])
        added = [f for f in after if not f in before]
        # print(added)
        removed = [f for f in before if not f in after]
        if added: print ("Added: ", ", ".join (added))
        if removed: print ("Removed: ", ", ".join (removed))

        for file in added:
           poseJsonData = readJSON("%s/%s" %(path, file))
           poses = parsePoseData(poseJsonData)
           if (len(poses) > 0):
                prettyPrintPoseData(poses[0])
                
        before = after

def euclidianDistance(x, y):
    return math.sqrt(x**2 + y**2)

def calculatePoseError(pose1, pose2, lowerThreshold, upperThreshold, biasPart):
    # the error should be relative since the people in the webcam feed might have a different center than the video feed
    # normalize to the same body part location
    # ideally, limb length should also be accounted for but that's pretty hard to do
    offset1 = 0
    offset2 = 0

    for pose in pose1:
        if pose['part'] == biasPart:
            offset1 = {'x': pose['x'], 'y': pose['y']}

    for pose in pose2:
        if pose['part'] == biasPart:
            offset2 = {'x': pose['x'], 'y': pose['y']}

    #print(len(pose1))
    #print(len(pose2))
    if (len(pose1) != len(pose2) ):
        #print ("different pose lengths, can't calculate error")
        return -1
    
    poseError = []
    for i in range(0, len(pose1)):
        x1 = pose1[i]['x'] - offset1['x']
        x2 = pose2[i]['x'] - offset2['x']
        y1 = pose1[i]['y'] - offset1['y']
        y2 = pose2[i]['y'] - offset2['y']
        distance = euclidianDistance(x2 - x1, y2 - y1)
        poseError.append(distance)

    # if the error is above the upper threshold, it's most likely because a segment was detected in
    # one feed but not the other -> don't count it
    validPoseCount = 0
    totalValidError = 0
    for error in poseError:
        if (error > upperThreshold):
            continue
        validPoseCount += 1.0
        totalValidError += error

    averageError = totalValidError / validPoseCount if validPoseCount > 0 else -1.0

    if (averageError > 0):
        if averageError < lowerThreshold:
            print("Your current error is %s. Keep it up!" %str(averageError), end='\r')
        else:
            print("Your current error is %s. GIT GUD SCRUB!!1!" %str(averageError), end='\r')
    

    #print(poseError)


def readJSON(filePath):
    try:
        #print(filePath)
        with open(filePath) as f:
            data = json.load(f)
            # print (data)
            return data
    except:
        t = 5
        #print ("%s is not a valid JSON file" %filePath)
    

# pose_keypoints_2d contains points in the format x1, y1, c1, x2, y2, c2, ..., x15, y15, c15
# where x and y are coordinates and c is confidence 
def parsePoseData(data):
    """Parses JSON data for poses 
    """

    if (data is None or data["people"] is None):
        return []

    numberOfPeople = len(data["people"])

    if (numberOfPeople == 0):
        return []

    poses = []
    for i in range(0, numberOfPeople):
        current = data["people"][i]["pose_keypoints_2d"]
        # parse the point data from a list of x, y, c into an indexed dictionary of x, y
        posePoints = [{"index": int(j / 3), "part": bodyParts[int(j / 3)], "x": current[j], "y": current[j+1]} for j in range(0, len(current), 3)]
        poses.append(posePoints)

    return poses        

def prettyPrintPoseData(poseSegments):
    for segment in poseSegments:
        print (segment['part'] + ", " + str(segment['x']) + ", " + str(segment['y']))
   
def runSystemCommand(command):
    os.system(command)

def showWebcamFeed():
    os.system(userWebcamFeedCommand)

def showVideoFeed():
    os.system(showVideoCommand + testVideoPath)

def runProcesses():
    videoProcess = multiprocessing.Process(name = 'p1', target = showVideoFeed)
    webcamProcess = multiprocessing.Process(name = 'p2', target = showWebcamFeed)
 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = CustomHandler()

    webcamObserver = Observer()
    webcamObserver.schedule(event_handler, webcamOutputPath, recursive=True)
    webcamObserver.start()

    videoObserver = Observer()
    videoObserver.schedule(event_handler, videoOutputPath, recursive=True)
    videoObserver.start()

    videoProcess.start()
    webcamProcess.start()

    videoProcess.join()
    webcamProcess.join()
   
    webcamObserver.join()
    videoObserver.join()

def parseDataTest():
    path = "output/webcam_out/000000000064_keypoints.json"
    json = readJSON(path)
    poses = parsePoseData(json)
    prettyPrintPoseData(poses[0])

if __name__ == '__main__':
    videoPath = sys.argv[1]

    bodyParts = readJSON('../bodyparts.json')['parts']
    #parseDataTest()

    try:
        runProcesses()
    except:
        print ("Error: unable to start processes")
    
    try:
        while 1:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("swag")
