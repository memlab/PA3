#---- new to PA3 ----#
#how long to give thie stim/no stim confirmation after key press
CONFIRMATION_DURATION = 1500
#how long to wait between an answer the to "is this a stim trial?" question
#and the beginning of the study sequence
AFTER_STIM_QUESTION = 3000
#how man SECONDS should the sync period be
SYNC_DURATION_SECONDS = 60

#stim parameters
STUDY_STIM_DURATION = 3000

CUE_STIM_DURATION=3000

#how long should the mini-pulses go on for in the 10 x 2 on 10 off cycle
# Brad - 2000
CYCLE_PULSE_ON_DURATION = 2000
#how long should the mini-pulses go off for in the 10 x 2 on 10 off cycle
#Brad - 10000
CYCLE_PULSE_OFF_DURATION = 10000
#number of such cycles
PULSE_CYCLES = 10
#frequency of pulse for stimulating study/cue, and background data. measured in number of pulses per second.
#PyFR_Stim - 100
STIM_PULSE_FREQ = 100

STOP_BEEP_FREQ=400
STOP_BEEP_DUR=300
STOP_BEEP_RISE_FALL=100

#---- from PA2 ----#
# The following parameters were taken from the config.ini file attained
# with the orinal py2 experiment

JITTER=75	        # (+/- jitter) introduced to presentation timing

NUM_PAIRS=6	        # number of pairs in each list (must be even)

NUM_TRIALS=25           # number of trials total (must be odd)

MIN_SPACING=2 	        # min # of items between study and test. 
			# must be less than half of NUM_PAIRS
                        # PA3: Mike says 2 or 1 are possible, 2 should be default

USE_INTERFERENCE=0	# use interference when constructing lists?

USE_CORRELATION=1	# use correlations when constructing pairs?

MIN_CORRELATION=-.1

MAX_CORRELATION=0.3

DURATION_CUE=3000	# PA3: KEEP THIS THE SAME AS RECORD_LEN & CUE_STIM_DURATION
                        # durzation of presentation of the cue (zero indicates 
                        # the the probe should be left on until the 
                        # subject makes a response)

RECORD_LEN=DURATION_CUE # PA3: KEEP THIS THE SAME AS DURATION_CUE
                        # length of time to record subjects response 
                        # (zero indicates record until button is pressed)


# all timing values are in milliseconds
DELAY_ORIENT=1500	# delay before the orienting stimulus (also 
                        #the delay after presentation of a word pair)

DURATION_ORIENT=300	# duration of the orienting stimulus

DELAY_WORD=750	        # delay before presentation of a word

#PA3 changes to 2500
DURATION_WORD=2500	# duration of presentation of a word

DELAY_CUE=750	        # delay before presentation of the cue


# The following parameters were taken from the config.ini file attained
# with the orinal py2 experiment

DATA_DIR="data"
MARKER_FILE="marker.bin"
BEHAV_FILE="behav.txt"
MATLAB_FILE="subdat.csv"
CONF_FILE="config.ini"
SYNC_FILE="syncfile.txt"

CORR_FILE="txt/wordmatrix.txt"
POOL_FILE="txt/nounpool.txt"
INTRO_FILE=open("txt/intro.txt").read()

EXP_NAME="PYPA2"
EXP_VERSION="v1.0"
ORIENTING_STUDY="XXXXXX"
ORIENTING_TEST="??????"

DIR_PERM=0755
ESC_KEY=27
ENTER_KEY=10

# if using word correlations to determine list structure, this
# parameter determines the minimum acceptable difference between the
# minCorr and maxCorr parameters
MIN_CORR_DIFF=0.3
