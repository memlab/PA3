#!/usr/bin/python
import sys
from pyepl.locals import *

if __name__ == "__main__":
    #set up the experiment...
    exp = Experiment()
    exp.parseArgs()
    exp.setup()

    #allow users to break out of the experiment with escape-F1 (the default)
    exp.setBreak()

    #get the subject configuration
    config = exp.getConfig()

    vid = VideoTrack("video")
    vid.clear('black')
    eeg = EEGTrack("eeg")
    for i in range(config.NUM_SECONDS):
        flashStimulus(Text(str(config.NUM_SECONDS - i)), duration=1000)
