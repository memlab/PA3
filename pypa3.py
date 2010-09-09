#!/usr/bin/python
import random
import sys
from pyepl.locals import *
from pyepl import display
from pyepl.hardware import addPollCallback

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




def runTrial(t, exp, config, stimTrial, state):
    t.vid.clear('black')

    stimOdds = random.choice([True, False])
    t.log.logMessage("STIM_ODDS " + str(stimOdds), t.clk)

    #STUDY
    #log the start of the study period
    t.log.logMessage("STUDY_START\tTRIAL_%d" % (state.trial), t.clk)

    #present orienting stimulus
    stamp = flashStimulus(Text(config.STUDY_ORIENTATION),
                          duration=config.STUDY_ORIENTATION_DURATION,
                          clk=t.clk)
    #log the presentation of the orienting stimulus
    t.log.logMessage("STUDY_ORIENT\tTRIAL_%d" % (state.trial), stamp)

    pairs = state.trialData[0][state.trial]
    for (i, (first, second)) in enumerate(pairs):
        t.clk.delay(config.INTER_STUDY_DURATION, jitter=config.JITTER)
        if stimTrial:
            if ((i % 2 == 1) and stimOdds) or ((i % 2 == 0) and (stimOdds == False)):
                t.log.logMessage("START_STUDY_STIM_AFTER " + str(timing.now()))
                t.pulseControl.pulseLen = (1000 / config.STIM_PULSE_FREQ) / 2
                t.pulseControl.maxPulses = ((config.STUDY_PRESENTATION_DURATION + config.INTER_STUDY_DURATION) / t.pulseControl.pulseLen) / 2
                t.pulseControl.startPulses(t.clk)


        stamp = flashStimulus(Text(first + "\n\n\n" + second), duration=config.STUDY_PRESENTATION_DURATION, jitter=config.JITTER, clk=t.clk)
        #log word presentations
        t.log.logMessage("STUDY_WORDS_%s_%s\tTRIAL_%d" % (first, second, state.trial), stamp)

    #INTER-PERIOD PAUSE
    t.clk.delay(config.INTER_STUDY_DURATION)

    #RECALL
    #log the start of the recall period
    t.log.logMessage("TEST_START\tTRIAL_%d" % (state.trial), t.clk)
    #present orienting stimulus
    stamp = flashStimulus(Text(config.RECALL_ORIENTATION),
                          duration=config.RECALL_ORIENTATION_DURATION,
                          clk=t.clk)
    t.vid.updateScreen(t.clk)
    #log the presentation of the orienting stimulus
    t.log.logMessage("TEST_ORIENT\tTRIAL_%d" % (state.trial), stamp)
    cueIndexes = [i for i in range(len(pairs))]
    random.shuffle(cueIndexes)
    for index in cueIndexes:
        cue = random.choice(pairs[index])
        t.clk.delay(config.INTER_CUE_DURATION)
        probeHandle = t.vid.showCentered(Text(cue))
        t.vid.updateScreen(t.clk)
        #log the presentation of the probe
        t.log.logMessage("TEST_PROBE_%s\tTRIAL%d" % (cue, state.trial), t.clk)

        #stim
        if stimTrial:
            if ((index % 2 == 1) and stimOdds) or ((index % 2 == 0) and (stimOdds == False)):
                t.log.logMessage("START_CUE_STIM_AFTER " + str(timing.now()))
                t.pulseControl.pulseLen = (1000 / config.STIM_PULSE_FREQ) / 2
                t.pulseControl.maxPulses = (config.CUE_PRESENTATION_DURATION / t.pulseControl.pulseLen) / 2
                t.pulseControl.startPulses(t.clk)


        #record
        fname = "%d_%s" % (state.trial, cue)
        (rec, startStamp) = t.aud.startRecording(fname, t=t.clk)
        t.log.logMessage("REC_START"%(), startStamp)

        t.clk.delay(config.CUE_PRESENTATION_DURATION)
        t.vid.unshow(probeHandle)
        t.vid.updateScreen(t.clk)
        
        (rec, stopStamp) = t.aud.stopRecording(t.clk)
        t.log.logMessage("REC_END"%(), stopStamp)



def stimOnOff(t, config):
    flashStimulus(Text("Starting test stim cycle"), duration=3000)
    for i in range(config.PULSE_CYCLES):
        t.log.logMessage("PULSE_CYCLE_START", t.clk)

        t.pulseControl.pulseLen = (1000 / config.STIM_PULSE_FREQ) / 2
        t.pulseControl.maxPulses = (config.CYCLE_PULSE_ON_DURATION / t.pulseControl.pulseLen) / 2
        t.pulseControl.startPulses(t.clk)

        flashStimulus(Text("Background stim #" + str(i)), duration=config.CYCLE_PULSE_ON_DURATION + config.CYCLE_PULSE_OFF_DURATION)

def sync(t, config):
    for i in range(config.SYNC_DURATION_SECONDS):
        flashStimulus(Text(str(config.SYNC_DURATION_SECONDS - i)), duration=1000)




def runSubject(t, exp, config, stimExperiment):
    state = exp.restoreState()

    if state.trial >= len(state.trialData[0]):
        print "No more sessions!"
        return

    print "YOU ARE CURRENTLY ON TRIAL #" + str(state.trial)

    t.vid.clear('black')
    if state.trial == 0:
        instruct(config.INSTRUCTIONS)

    #loop through the trials
    for trialNum in range(state.trial, config.NUM_TRIALS):
        print "RUNNING TRIAL #" + str(state.trial)
        
        if stimExperiment:
            stimTrial = waitForYKey("Is this a stim trial?\nPress 'y' for yes, any other key for no.")
            if stimTrial:
                msg = "Okay this IS a stim trial"
            else:
                msg = "Okay this is NOT a stim trial"
            flashStimulus(Text(msg), duration=config.CONFIRMATION_DURATION)
        else:
            stimTrial = False

        doSync = waitForYKey("Would you like to sync?\nPress 'y' for yes, any other key for no.")
        if doSync:
            waitForAnyKey(t.clk, Text("Please plug into EEG RIG.\n\nThen press any key to continue"))
            sync(t, config)
        if stimTrial:
            elec = textInput("Electrodes: ", t.vid, t.key, t.clk)
            t.log.logMessage("TRIAL_%d ELECTRODES_%s" % (state.trial, elec), t.clk)
            cur = textInput("Current: ", t.vid, t.key, t.clk)
            t.log.logMessage("TRIAL_%d CURRENT_%s" % (state.trial, cur), t.clk)
            
            waitForAnyKey(t.clk, Text("Please plug into STIMULATOR.\n\nThen press any key."))
            stimOnOff(t, config)
            

        waitForAnyKey(t.clk, Text("Press any key to start trial."))
        flashStimulus(Text(""), duration=config.AFTER_STIM_QUESTION)

        runTrial(t, exp, config, stimTrial, state)
        exp.saveState(state, trial=state.trial + 1)
        state = exp.restoreState()
        print "FINISHED TRIAL #" + str(state.trial - 1)
        waitForAnyKey(t.clk, Text("Press any key to continue\n" + "onto the next list."))

    waitForAnyKey(t.clk, Text("You have finished.\n" + "Please inform the experimenter."))




def prepare(exp, config, t):
    pairsPerTrial = config.PAIRS_PER_TRIAL
    numTrials = config.NUM_TRIALS
    
    pool = TextPool(config.POOL_FILE)
    pool.shuffle()
    words = [pool[i]['name'] for i in range(len(pool))]

    if len(words) < (numTrials * pairsPerTrial):
        print "Config: there are not NUM_TRIALS * PAIRS_PER_TRIAL words in POOL_FILE!"
        sys.exit(1)

    #choose words for each trial
    wordPairs = []
    for i in range(0, numTrials * pairsPerTrial, pairsPerTrial * 2):
        singleTrial = []
        for j in range(i, i + pairsPerTrial * 2, 2):
            singleTrial.append([words[j], words[j + 1]])
        wordPairs.append(singleTrial)


    stimExperiment = waitForYKey("Is this a stim experiment?\nPress 'y' for yes, any other key for no.")
    if stimExperiment:
        msg = "Okay this IS a stim experiment"
    else:
        msg = "Okay this is NOT a stim experiment"
    flashStimulus(Text(msg), duration=config.CONFIRMATION_DURATION)
        
    exp.saveState(None, trialData=[wordPairs, stimExperiment], trial=0)




def waitForYKey(msg):
    v = display.VideoTrack.lastInstance()
    v.clear('black')
    shown = v.showCentered(Text(msg))
    v.updateScreen(None)
    k = KeyTrack.lastInstance()
    bc = k.keyChooser()
    but, timestamp = bc.waitWithTime(None)
    v.unshow(shown)
    v.updateScreen(None)
    return but.keyname == 'Y'



if __name__ == "__main__":
    #set up the experiment...
    exp = Experiment()
    exp.parseArgs()
    exp.setup()

    #allow users to break out of the experiment with escape-F1 (the default)
    exp.setBreak()

    #get the subject configuration
    config = exp.getConfig()

    t = Tracks(config)
    #if there was no saved state, run the prepare function
    if not exp.restoreState():
        prepare(exp, config, t)
        print "FIRST RUN"
    else:
        print "NOT FIRST RUN"

    state = exp.restoreState()

    #now run the subject
    runSubject(t, exp, config, state.trialData[1])
