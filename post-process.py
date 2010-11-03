#!/usr/bin/python

#import PyEPL symbols into this namespace:
from pyepl.locals import *
from pypa3 import TrialData
import os
import os.path

def save_data(exp,config):
    '''
    Save the results for the participant.
    '''

    #get the state
    state = exp.restoreState()

    # Set up scoring session
    exp.setSession("SAVE")

    # create tracks...
    video = VideoTrack("save_video")
    keyboard = KeyTrack("save_keyboard")
    log = LogTrack("score_session")

    # create a PresentationClock to handle timing
    clock = PresentationClock()


    # get session specific configuration
    trialconfig = config.sequence(state.trial)

    data_dir = "data/%s/session_SAVE/"%(exp.getOptions()['subject'])

    mrk_name = data_dir + trialconfig.MARKER_FILE
    eeg_name = data_dir + trialconfig.BEHAV_FILE
    matlab_name = data_dir + trialconfig.MATLAB_FILE

    mrk_file = open(mrk_name,'w')
    eeg_file = open(eeg_name,'w')
    matlab_file = open(matlab_name,'w')

    matlab_file.write("% serial_pos\tprobe_pos\tinterference(0,1)\tdirection(0=F,1=B)\tcorrect(0,1)\tresponse time (ms)\n")
    for i in range(0, trialconfig.NUM_TRIALS * trialconfig.NUM_PAIRS):

        # look at ann file to determine if participant got the word right. only the first word is considered, per Mike's instructions
        cur_trial = i // trialconfig.NUM_PAIRS
        cur_pair = i % trialconfig.NUM_PAIRS
        ann_path = 'data/%s/session_RUN/%d_%d.ann' % (exp.getOptions()['subject'], cur_trial, cur_pair)
        if not os.path.exists(ann_path):
            print 'ann file missing: ' + ann_path
            sys.exit(1)
        annotations = extract_annotations(ann_path)
        first_word = annotations[0][1]

        direction = state.trialData[i].cueDir
        if direction == 1:
            opposite_direction = 0
        else:
            opposite_direction = 1
        if first_word == state.trialData[i].word[opposite_direction]:
            correct = 1
        else:
            correct = 0

        reaction_time = -5

        matlab_file.write("%d\t%d\t%d\t%d\t%d\t%d\n"%
                          (state.trialData[i].presOrder,
                           state.trialData[i].cueOrder,
                           state.trialData[i].interference,
                           state.trialData[i].cueDir,
                           correct,
                           reaction_time))

    mrk_file.close()
    eeg_file.close()
    matlab_file.close()
    video.clear("black")
    waitForAnyKey(clock,Text("Data has been saved to\n" +
			     "%s"%(matlab_name)))


def extract_annotations(path):
    words = []
    lines = open(path, 'r').readlines()
    for line in lines:
        if line == None:
            continue
        elif line.startswith('#'):
            continue
        else:
            columns = line.split('\t')
            if len(columns) == 3:
                words.append([round(float(columns[0])), columns[2].rstrip()])
            else:
                continue
    return words

    

# only do this if the experiment is run as a stand-alone program 
#(not imported as a library)...
if __name__ == "__main__":

    # set up the experiment...
    exp = Experiment()
    exp.parseArgs()
    exp.setup()

    # allow users to break out of the experiment with escape-F1 
    # (the default key combo)

    exp.setBreak()

    # get the subject configuration
    config = exp.getConfig()

    # if there was no saved state, return
    if not exp.restoreState():
        print "NO DATA TO SAVE FOR SUBJECT"
    else:
	# now save the subject data
	save_data(exp, config)
 
