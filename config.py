#how man SECONDS should the sync period be
SYNC_DURATION_SECONDS = 60

#Brad - 6
PAIRS_PER_TRIAL = 6
#Brad - 25
NUM_TRIALS = 25
#Brad - 200
JITTER = 200

#Brad - 1200
#length of time between stimuli, when screen is blank
#also the delay between study and recall periods
INTER_STUDY_DURATION = 1200

#Brad - 1600
#how long a word is on screen for study
STUDY_PRESENTATION_DURATION = 1600

#Brad - 1600
#length of time between cues (i.e. recall words), when screen is blank
INTER_CUE_DURATION = 1600

#Brad - 2600
#how long a cue (recall word) is on screen, also possibly stimming
CUE_PRESENTATION_DURATION = 2600

#how long the study orientation will be on the screen
STUDY_ORIENTATION_DURATION = 1500
STUDY_ORIENTATION ="XXXXXX"

#how long the recall orientation will be on the screen
RECALL_ORIENTATION_DURATION = 1500
RECALL_ORIENTATION = "??????"


POOL_FILE="txt/nounpool.txt"
INSTRUCTIONS = open("txt/intro.txt").read()

#how long to wait between an answer the to "is this a stim trial?" question
#and the beginning of the study sequence
AFTER_STIM_QUESTION = 3000
#how long to give thie stim/no stim confirmation after key press
CONFIRMATION_DURATION = 1500




#stim parameters
#how long should the mini-pulses go on for in the 10 x 2 on 10 off cycle
#Brad - 2000
CYCLE_PULSE_ON_DURATION = 2000
#how long should the mini-pulses go off for in the 10 x 2 on 10 off cycle
#Brad - 10000
CYCLE_PULSE_OFF_DURATION = 10000
#number of such cycles
PULSE_CYCLES = 0

#frequency of pulse for stimulating study/cue, and background data. measured in number of pulses per second.
#PA2 - 100
STIM_PULSE_FREQ = 100


EXP_NAME="PYPA3"
EXP_VERSION="v1.0"
