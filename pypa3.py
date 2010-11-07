#!/usr/bin/python

#standard imports
import sys
import random

#import PyEPL symbols into this namespace:
from pyepl.locals import *
from pyepl import display
from pyepl.hardware import addPollCallback



# The following parameters were taken from the pa2.h file attained
# with the orinal py2 experiment

# Cue Directions
FORWARD = 0
BACKWARD = 1

# Cue Conditions
NO_INTERFERENCE = 0
INTERFERENCE = 1

# All Conditions
FORW_NOINT = 0
BACK_NOINT = 1
FORW_INT   = 2
BACK_INT   = 3
NUM_CONDITIONS = 4

class PulseThread:
    """
    Finer control of pulse timing.
    """
    
    def __init__(self, eeg, config):
        self.sendPulse = False
        self.EEGTrack = eeg
        self.config = config
        self.lastPulse = timing.now()
        self.pulseCount = 0
        addPollCallback(self.EEGpulseCallback)

    def stopPulses(self, clock = None):
        if isinstance(clock, PresentationClock):
            (timeInterval, returnValue) = timing.timedCall(clock.get(), self.stopPulses)
        elif clock and not isinstance(clock, PresentationClock):
            (timeInterval, returnValue) = timing.timedCall(clock, self.stopPulses)
        else:
            self.sendPulse = False
            self.pulseCount = 0

    def startPulses(self, clock = None):
        if (self.pulseLen * self.maxPulses * 2) > 10000:
            print "you are trying to stim for longer than 10 secons. not allowed!"
            sys.exit(1)
        if isinstance(clock, PresentationClock):
            (timeInterval, returnValue) = timing.timedCall(clock.get(), self.startPulses)
        elif clock and not isinstance(clock, PresentationClock):
            (timeInterval, returnValue)=timing.timedCall(clock, self.stopPulses)
        else:
            self.sendPulse = True

    def EEGpulseCallback(self):
        """
        Callback to manage sending pulses.
        """
        if self.sendPulse == True and (timing.now() >= self.lastPulse + self.pulseLen):
            timeInterval = self.EEGTrack.timedPulse(self.pulseLen)
            self.lastPulse = timeInterval[0]
            self.pulseCount += 1
            if self.pulseCount == self.maxPulses:
                self.sendPulse = False
                self.pulseCount = 0





class TrialData:
    '''
    A class to hold data for each trial
    '''
    def __init__(self):
	self.tOrientStudy = 0
	self.tOrientTest = 0
	self.tWord = []
	self.tWord.append(0)
	self.tWord.append(0)
	self.tCue = 0
	self.tResp = 0
	self.correct = -1
	self.reactionTime = -1
	self.pos = []
	self.pos.append(-1)
	self.pos.append(-1)
	self.interference = NO_INTERFERENCE
	self.cueDir = FORWARD
	self.presOrder = 0
	self.response = []
	self.word = []
	self.word.append('') 
	self.word.append('')
	self.cueOrder = -1
	self.reused = -1
        self.stimOdds = False #for each trial, should we stim odd or even study words?
        self.backgroundPulses = []
        self.syncPulses = []
	


def load_correlation(FILE_NAME):
    '''
    This function will load the correlation matrix stored in FILE_NAME.
    '''
    # Open the file
    file = open(FILE_NAME,'r')
    
    # Read the first character
    char = file.read(1)

    # Start with an empy list for the correlations
    correlation_matrix = {}

    # While not EOF
    while(char != ''):
	base = ''

	# A dictionary structure of words and correlations
	correlations = {}

	i = 0

	# Read in the base word
	while(char != '\t'):
	    base = base + char
	    char = file.read(1)
	char = file.read(1)

	# While not end-of-line
	while(char!='\n'):
	    word = ''
	    word_correlation = ''

	    # Read the word 
	    while(char!='\t'):
		word = word + char
		char = file.read(1)
	    char = file.read(1)

	    # Read the correlation between BASE and WORD
	    while(char!='\t'):
		word_correlation = word_correlation + char
		char = file.read(1)
	    char = file.read(1)

	    # Store the word-base correlation
	    correlations[word] = float(word_correlation)

	# Store all correlations for the base word
	correlation_matrix[base] = correlations

	# Read the next character
	char = file.read(1)
    
    file.close()
    return correlation_matrix



def prepare(exp,config):
    """
    This function will create the trial structure for the entire experiment.
    """
    
    #Get session info. from the config file
    jitter = config.JITTER
    num_pairs = config.NUM_PAIRS
    num_trials = config.NUM_TRIALS
    min_spacing = config.MIN_SPACING

    use_interference = config.USE_INTERFERENCE
    use_correlation = config.USE_CORRELATION
    min_correlation = config.MIN_CORRELATION
    max_correlation = config.MAX_CORRELATION

    record_len = config.RECORD_LEN

    #Get Timing info. from the config file
    delay_orient = config.DELAY_ORIENT
    duration_orient = config.DURATION_ORIENT
    delay_word = config.DELAY_WORD
    duration_word = config.DURATION_WORD
    delay_cue = config.DELAY_CUE
    duration_cue = config.DURATION_CUE

    min_corr_diff = config.MIN_CORR_DIFF        

    # Make sure that there are an even number of pairs within a trial.
    # Necessary because half of the pairs use interference and half do not.
    if((num_pairs % 2)==1):
	print "Config: NUM_PAIRS must be an even number of pairs."
	return
    
    # Make sure that there are enough trials to counterbalance across all
    # four conditions
    if(((num_trials-1) * num_pairs % NUM_CONDITIONS) != 0):
        print "Config: (NUM_TRIALS-1) * NUM_PAIRS must be evenly divisible by the number of conditions."
	return
    
    # Make sure that the minimum number of interspersed items between study 
    # and test is less than four
    if (min_spacing > 3):
	print "Config: MIN_SPACING must be less than four."
	return
    
    # Make sure max and min correlation values are within bounds
    if (use_correlation and (max_correlation - min_correlation 
			     < min_corr_diff)):
	print "Config: CORRELATION values out of bounds."
	return

    total_pairs = num_pairs*num_trials

    # Load the word pool
    text_pool = TextPool(config.POOL_FILE)

    # Tracks which words from the pool have already been used.
    pool_used = []
    # Initialize pool_used to 0 ('zero')
    for i in range (0,len(text_pool)):
	pool_used.append(0)

    # Load correlation matrix if necessary
    if(use_correlation):
	correlation = load_correlation(config.CORR_FILE)

    # Initialize trial array to default values
    trialData = []
    for i in range(total_pairs):
	temp = TrialData()
	# Setup Study order
	temp.presOrder = i % num_pairs
	trialData.append(temp)

    # Randomly cue half the trials forward(0) and half backward(1)
    for i in range(total_pairs/2):
	while 1:
	    rint = random.randint(0,total_pairs-1)
	    if(trialData[rint].cueDir == FORWARD):
		trialData[rint].cueDir = BACKWARD
		break

    # For each trial
    for trial in range (0,num_trials):
        trialData[trial].stimOdds = random.choice([True, False])

	# Setup interference. Half of the pairs in each list (except the
	# first) use interference from a previous list
	if((trial!=0) and (use_interference == 1)):
	    for i in range(0,num_pairs/2):
		while 1:
		    rint = random.randint(0,num_pairs-1)
		    pos = trial*num_pairs + rint
		    if(trialData[pos].interference == NO_INTERFERENCE):
			trialData[pos].interference = INTERFERENCE
			break
    
        # Setup testing order, preserving a minimum spacing from study
	taken = []
        # Initialize taken to 0
	for i in range(0,num_pairs):
	    taken.append(0)
	for cueOrder in range(0,num_pairs):
	    while 1:
		rint = random.randint(0,num_pairs-1)
		if( (not taken[rint]) and ((cueOrder+num_pairs - 
					    (trialData[rint].presOrder+1)) 
					   >= min_spacing)):
		    trialData[trial*num_pairs + rint].cueOrder = cueOrder
		    taken[rint] = 1
		    break
    
	# Choose words to present
	for pair in range(0,num_pairs):
	    position = trial*num_pairs + pair
	    if (trialData[position] == INTERFERENCE):
		# Interference condition. Choose a previously presented word
		wordNum = trialData[position].cueDir
		while 1:
		    wordOne = random.randint( (trial-1)*num_pairs,trial*
					      num_pairs-1)
		    if(not trialData[wordOne].reused):
			break
		trialData[position].word[wordNum] = trialData[wordOne].word[wordNum]
		trialData[position].pos[wordNum] = trialData[wordOne].pos[wordNum]
		trialData[position].reused = 1
		trialData[wordOne].reused = 1
	    else:
		# Non-interference condition. Choose new word A
		wordNum = FORWARD
		while 1:
		    wordOne = random.randint(0,len(text_pool)-1)
		    if(pool_used[wordOne] == 0):
			trialData[position].word[wordNum] = text_pool.__getitem__(wordOne)['name']
			trialData[position].pos[wordNum] = wordOne
			pool_used[wordOne] = 1
			break
	    
	    # Make sure we're tracking the right word
	    wordOne = trialData[position].pos[wordNum]
	    
	    # Change the word we're working with
	    wordNum = not wordNum
	    
	    # Choose a (possibly correlated) new word
	    while 1:
		wordTwo = random.randint(0,len(text_pool)-1)
		if ((not pool_used[wordTwo]) and 
		    ((not use_correlation) or 
		     ((correlation[text_pool.__getitem__(wordOne)['name']][text_pool.__getitem__(wordTwo)['name']] >= min_correlation) and 
		      (correlation[text_pool.__getitem__(wordOne)['name']][text_pool.__getitem__(wordTwo)['name']] <= max_correlation)))):
		    break 
	    trialData[position].word[wordNum] = text_pool.__getitem__(wordTwo)['name']
	    trialData[position].pos[wordNum] = wordTwo
	    pool_used[wordTwo] = 1


    exp.saveState(None,trialData=trialData,trial=0,scoreTrial=0)
	

def run(exp,config,t):
    """
    Runs through the experiment trial-by-trial.
    """

    #get the state
    state = exp.restoreState()

    target = Text('*')

    # set up session...
    if state.trial >= len(state.trialData):
        # if all the sessions have been run, don't continue
        print "No more sessions!"
        return

    # set the session number (so PyEPL knows what directory to put the data in)
    exp.setSession("RUN")#state.trial)

    # get session specific configuration
    trialconfig = config.sequence(state.trial)

    # check if mic is recording
    t.vid.clear('black')
    soundgood = micTest(2000, 1.0)
    if not soundgood:
        print "mic not working"
        return

    # present the instructions
    t.vid.clear('black')
    instruct(trialconfig.INTRO_FILE,clk=t.clk)

    while (state.trial < trialconfig.NUM_TRIALS):
#         print
        stimTrial = waitForYKey("Is this a stim trial?\nPress 'y' for yes, any other key for no.")
        if stimTrial:
            msg = "Okay this IS a stim trial"
        else:
            msg = "Okay this is NOT a stim trial"
        flashStimulus(Text(msg), duration=config.CONFIRMATION_DURATION)
        t.log.logMessage("TRIAL_%d STIM_%s"%(state.trial, str(stimTrial)),t.clk)

        doSync = waitForYKey("Would you like to sync?\nPress 'y' for yes, any other key for no.")
        if doSync:
            waitForAnyKey(t.clk, Text("Please plug into EEG RIG.\n\nThen press any key to continue"))
            sync(t.log, t.pulseControl, t.clk, config, state.trialData[state.trial * trialconfig.NUM_PAIRS])
        if stimTrial:
            elec = textInput("Electrodes: ", t.vid, t.key, t.clk)
            t.log.logMessage("TRIAL_%d ELECTRODES_%s" % (state.trial, elec), t.clk)
            cur = textInput("Current: ", t.vid, t.key, t.clk)
            t.log.logMessage("TRIAL_%d CURRENT_%s" % (state.trial, cur), t.clk)

            waitForAnyKey(t.clk, Text("Please plug into STIMULATOR.\n\nThen press any key."))
            stimOnOff(t.log, t.pulseControl, t.clk, config, state.trialData[state.trial * trialconfig.NUM_PAIRS], elec, cur)


        waitForAnyKey(t.clk, Text("Press any key to start trial."))
        flashStimulus(Text(""), duration=config.AFTER_STIM_QUESTION)

        ####### STUDY ######
	t.vid.clear("black")

	# Log the start of the study period
	t.log.logMessage("STUDY_START\tTRIAL_%d"%(state.trial),t.clk)
    
	for pair in range(state.trial*trialconfig.NUM_PAIRS,
			  (state.trial+1)*trialconfig.NUM_PAIRS):
	    # Present the orienting stimulus
	    t.clk.delay(trialconfig.DELAY_ORIENT,jitter=trialconfig.JITTER)
	    state.trialData[pair].tOrientStudy = t.clk.get()
	    stamp = flashStimulus(Text(trialconfig.ORIENTING_STUDY),
				  duration=trialconfig.DURATION_ORIENT,
				  clk=t.clk)
	    # Log the presentation of the orienting stimulus
	    t.log.logMessage("STUDY_ORIENT\tTRIAL_%d"%(state.trial),stamp)

            # present the pair of words
            t.clk.delay(trialconfig.DELAY_WORD,jitter=trialconfig.JITTER)
            now = t.clk.get()
            state.trialData[pair].tWord[0] = now
            state.trialData[pair].tWord[1] = now
            word1 = state.trialData[pair].word[0]
            word2 = state.trialData[pair].word[1]
            text =  word1 + "\n\n" + word2
#             print "trial " + str(state.trial) + " study: " + state.trialData[pair].word[0] + " " + state.trialData[pair].word[1]

            #STIM NOW for config.STUDY_STIM_DURATION
            if stimTrial:
                if (state.trialData[state.trial].stimOdds and pair % 2 == 1) or ((not state.trialData[state.trial].stimOdds) and pair % 2 == 0):
                    duration = trialconfig.STUDY_STIM_DURATION
                    t.log.logMessage("BEGIN_STUDY_STIM DURATION_%d\tTRIAL_%d" % (duration, state.trial))
                    stim(duration, t.pulseControl, t.clk, trialconfig)
                    didStim = True
                else:
                    didStim = False
            else:
                didStim = False

            state.trialData[pair].didStim = didStim
            if didStim:
                state.trialData[pair].elec = elec
                state.trialData[pair].cur = cur
            else:
                state.trialData[pair].elec = 999
                state.trialData[pair].cur = 999
                

            stamp = flashStimulus(Text(text),
                                  duration=trialconfig.DURATION_WORD,
                                  clk=t.clk)
            state.trialData[pair].studyStamp = stamp
            # Log the presentation of each word in the pair
            t.log.logMessage("STUDY_PAIR_%d\tTRIAL_%d\tWORD1_%s\tWORD2_%s"%(pair, state.trial, word1, word2), stamp)

        ######  TEST   ######
	# Cued Recall

	# Log the start of the trial period
	t.log.logMessage("TEST_START\tTRIAL_%d"%(state.trial),t.clk)
    
	# Loop through all the items in the list
	for test in range(0,trialconfig.NUM_PAIRS):

	    # first find the index of the word to be tested
	    index = -1
	    for i in range (state.trial*trialconfig.NUM_PAIRS,
			    (state.trial+1)*trialconfig.NUM_PAIRS):
		if(state.trialData[i].cueOrder == test):
		    index = i
		    pair = index % trialconfig.NUM_PAIRS

    	    direction = state.trialData[index].cueDir

 	    # create the probe
	    probe = "%s"%(state.trialData[index].word[direction])
#             print "trial " + str(state.trial) + " cue: " + probe

	    # create the filename for output
	    fname = "session_RUN/%d_%d"%(state.trial,pair)

            lstname = "data/" + str(exp.options["subject"]) + "/session_RUN/" + str(state.trial) + '_' + str(pair) + '.lst'
            lst = open(lstname, 'w')
            if direction == 1:
                opposite_direction = 0
            else:
                opposite_direction = 1
            expecting = state.trialData[index].word[opposite_direction]
            lst.write(str(expecting) + '\n') 
            lst.close()

    

	       
	    # present the orienting stimulus
	    t.clk.delay(trialconfig.DELAY_ORIENT)
	    stamp = flashStimulus(Text(trialconfig.ORIENTING_TEST),
				  duration=trialconfig.DURATION_ORIENT,
				  clk=t.clk)
	    t.vid.updateScreen(t.clk)
	    # Log the presentation of the orienting stimulus
	    t.log.logMessage("TEST_ORIENT\tTRIAL_%d"%(state.trial),stamp)

	    # present the word
	    t.clk.delay(trialconfig.DELAY_CUE)
	    state.trialData[index].tCue = t.clk.get()
	    probeHandle = t.vid.showCentered(Text(probe))
	    stamp = t.vid.updateScreen(t.clk)
            state.trialData[pair].cueStamp = stamp
	    # Log the presentation of the probe
	    t.log.logMessage("TEST_PROBE_%d\tTRIAL%d\tPROBE_%s\tEXPECTING_%s\tDIRECTION_%d"%(index,state.trial, probe, expecting, direction),stamp)

            if stimTrial:
                if (state.trialData[state.trial].stimOdds and index % 2 ==1) or ((not state.trialData[state.trial].stimOdds) and index % 2 == 0):
                    duration = trialconfig.CUE_STIM_DURATION
                    t.log.logMessage("BEGIN_CUE_STIM DURATION_%d\tTRIAL_%d" % (duration, state.trial))
                    stim(duration, t.pulseControl, t.clk, trialconfig)


	    # Record
	    (rec,timestamp) = t.aud.startRecording(fname,t=t.clk)
	    t.log.logMessage("REC_START"%(),timestamp)

	    # if we need to erase the cue, do so after a delay
	    if(trialconfig.DURATION_CUE > 0):
		t.clk.delay(trialconfig.DURATION_CUE)
		t.vid.unshow(probeHandle)
		t.vid.updateScreen(t.clk)

   	    # record voice after recording for a specified time
	    if(trialconfig.RECORD_LEN > 0):
		t.clk.delay(trialconfig.RECORD_LEN)
	    else:
		waitForAnyKey(clk=t.clk)

   	    # clear the probe (if we haven't done so already)
	    if(trialconfig.DURATION_CUE <= 0):
		t.vid.unshow(probeHandle)
		t.vid.updateScreen(t.clk)

	    (rec,timestamp) = t.aud.stopRecording(t.clk)
	    t.log.logMessage("REC_END"%(),timestamp)

	# Save the State
	exp.saveState(state,trial=state.trial+1)
        #get the state
	state = exp.restoreState()

    waitForAnyKey(t.clk,Text("You have finished.\n"+
			     "Please inform the experimenter"))




def stim(duration, pulseControl, clock, config, notStimmingAHuman=False):
    global lastStimEnd
    if not notStimmingAHuman:
        elapsed = timing.now() - lastStimEnd
        print "elpased: " + str(elapsed)
        if elapsed < 2000:
            print "you have requested two stims less than 2 seconds apart"
            sys.exit()
    lastStimEnd = timing.now() + duration
    pulseControl.pulseLen = (1000 / config.STIM_PULSE_FREQ) / 2
    pulseControl.maxPulses = (duration / pulseControl.pulseLen) / 2
    pulseControl.startPulses(clock)

def stimOnOff(log, pulseControl, clock, config, tdata, elec, cur):
    flashStimulus(Text("Starting test stim cycle"), duration=3000)
    for i in range(config.PULSE_CYCLES):
        log.logMessage("PULSE_CYCLE_START", clock)
        stim(config.CYCLE_PULSE_ON_DURATION, pulseControl, clock, config)
        tdata.backgroundPulses.append([timing.now(), elec, cur])
        flashStimulus(Text("Background stim #" + str(i)), duration=config.CYCLE_PULSE_ON_DURATION + config.CYCLE_PULSE_OFF_DURATION)

def sync(log, pulseControl, clock, config, tdata):
    log.logMessage("START_SYNC_STIMS_AFTER")
    for i in range(config.SYNC_DURATION_SECONDS):
        stim(10, pulseControl, clock, config, notStimmingAHuman=True)
        tdata.syncPulses.append(timing.now())
        flashStimulus(Text(str(config.SYNC_DURATION_SECONDS - i)), duration=1000, jitter=config.JITTER)


def waitForYKey(msg):
    v = VideoTrack.lastInstance()
    v.clear('black')
    shown = v.showCentered(Text(msg))
    v.updateScreen(None)
    k = KeyTrack.lastInstance()
    bc = k.keyChooser()
    but, timestamp = bc.waitWithTime(None)
    v.unshow(shown)
    v.updateScreen(None)
    return but.keyname == 'Y'

def textInput(screenText, video, keyboard, clock):

    # set up keyboard entry
    ans_but = keyboard.keyChooser()

    done = False
    while not done:

        rstr = ''
        field = video.showProportional(Text(screenText),.4,.5)
        input = video.showRelative(Text(rstr),RIGHT,field,20)
        video.updateScreen(clock)

        kret,timestamp = ans_but.waitWithTime(maxDuration = None, clock=clock)

        while kret:
            
            # process the response
            if kret.name == 'BACKSPACE':
                
                # remove last char
                if len(rstr) > 0:
                    rstr = rstr[:-1]

                # update text
                input = video.replace(input,Text(rstr))
                video.updateScreen(clock)
                kret,timestamp = ans_but.waitWithTime(maxDuration = None,clock=clock)
                
            elif kret.name not in ['BACKSPACE','RETURN','ENTER']:
                newstr = kret.name.strip('[]')
                rstr = rstr + newstr

                # update the text
                input = video.replace(input,Text(rstr))
                video.updateScreen(clock)
                kret,timestamp = ans_but.waitWithTime(maxDuration = None,clock=clock)
                
            elif kret.name in ['RETURN','ENTER']:
                video.clear("black")
                return rstr


class Tracks:
    def __init__(self, config):
        self.vid = VideoTrack("video")
        flashStimulus(Text(""), duration=10) #hack to initialize video so PulseThread constructor won't fail                                                         
        self.aud = AudioTrack("audio")
        self.key = KeyTrack("keyboard")
        self.log = LogTrack("session")
        self.clk = PresentationClock()
        self.eeg = EEGTrack("eeg", autoStart=False)
        self.eeg.startService()
        self.eeg.logall = True
        self.pulseControl = PulseThread(self.eeg, config)


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

    t = Tracks(config)

    # if there was no saved state, run the prepare function
    if not exp.restoreState():
        prepare(exp, config)

    lastStimEnd = 0 # safety variable
    # now run the subject
    run(exp, config, t)
