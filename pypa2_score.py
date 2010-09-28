#!/usr/bin/python

#import PyEPL symbols into this namespace:
from pyepl.locals import *
from pypa2 import TrialData


def score(exp,config):
    '''
    Score the results for the participant.
    '''

    #get the state
    state = exp.restoreState()

    if(state.scoreTrial >= state.trial):
	print "DATA ALREADY SCORED FOR SUBJECT"
	return

    # Set up scoring session
    exp.setSession("SCORE")

    # get session specific configuration
    trialconfig = config.sequence(state.trial)

    # create tracks...
    video = VideoTrack("score_video")
    audio = AudioTrack("score_audio")
    keyboard = KeyTrack("score_keyboard")
    log = LogTrack("score_session")

    # create a PresentationClock to handle timing
    clock = PresentationClock()


    choice = 0
    while 1:
	if (choice == -1):
	    buf = Text("%d out of %d lists have already been scored.\nWhich list would you like to score? (1-%d)?"%(state.scoreTrial,state.trial,state.trial))
	else:
	    buf = Text("%d out of %d lists have already been scored.\nWhich list would you like to score? (1-%d)?\n%d"%(state.scoreTrial,state.trial,state.trial,choice))
	video.clear('black')
	video.showCentered(buf)
	video.updateScreen(clock)
		
	response =  buttonChoice(clk = clock, one=Key('1'),one_=Key('[1]'),
				 two=Key('2'),two_=Key('[2]'),
				 three=Key('3'),three_=Key('[3]'),
				 four=Key('4'),four_=Key('[4]'),
				 five=Key('5'),five_=Key('[5]'),
				 six=Key('6'),six_=Key('[6]'),
				 seven=Key('7'),seven_=Key('[7]'),
				 eight=Key('8'),eight_=Key('[8]'),
				 nine=Key('9'),nine_=Key('[9]'),
				 zero=Key('0'),zero_=Key('[0]'),
				 enter=Key('ENTER'),ret=Key('RETURN'))
	if response == 'zero' or response == 'zero_':
	    choice = 10*choice + 0
	elif response == 'one' or response == 'one_':
	    choice = 10*choice + 1
	elif response == 'two' or response == 'two_':
	    choice = 10*choice + 2
	elif response == 'three' or response == 'three_':
	    choice = 10*choice + 3
	elif response == 'four' or response == 'four_':
	    choice = 10*choice + 4
	elif response == 'five' or response == 'five_':
	    choice = 10*choice + 5
	elif response == 'six' or response == 'six_':
	    choice = 10*choice + 6
	elif response == 'seven' or response == 'seven_':
	    choice = 10*choice + 7
	elif response == 'eight' or response == 'eight_':
	    choice = 10*choice + 8
	elif response == 'nine' or response == 'nine_':
	    choice = 10*choice + 9
	elif response == 'enter' or response == 'ret':
	    choice = choice - 1
	    if(choice>=state.scoreTrial and choice<state.trial):
		break
	    else:
		choice = 0
	else:
	    pass

    # Loop through trials remaining to be scored
    while(state.scoreTrial < state.trial):
	# For each pair in the trial
	for pair in range (0,trialconfig.NUM_PAIRS):
	    position = state.scoreTrial*trialconfig.NUM_PAIRS+pair
	    expected = not (state.trialData[position].cueDir)
	    done = 0

	    while (not done):
		# play voice file and output prompt
		fname = "data/%s/session_RUN/%d_%d.wav"%(exp.getOptions()['subject'],
							 state.scoreTrial,pair)
		buf = "Expecting -- %s\n(y)es/(n)o/near (m)iss/(p)ass"%(state.trialData
					   [position].word[expected])
		video.clear('black')
		# Show the expected subject response
		video.showCentered(Text(buf))
		video.updateScreen(clock)

		# And play the recorded repsonse from the subject
		clip = AudioClip(fname)
                clip.present(clock)
		
		# Was the subject's response the correct one?
		response = buttonChoice(clk=clock,yes=Key('Y'),no=Key('N'),
					passkey=Key('P'),
					miss=Key('M'),repeat=Key("RETURN"))
		if response == 'yes':
		    state.trialData[position].response = state.trialData[position].word[expected]
		    state.trialData[position].correct = 1
		    done=1
		    log.logMessage("SCORE\tTRIAL_%d\tPAIR_%d\tCORRECT_YES"%
				   (state.trial,pair))
		elif response == 'passkey':
		    ## Read in what the subject actually said.
		    state.trialData[position].correct = 3
		    done=1
		    log.logMessage("SCORE\tTRIAL_%d\tPAIR_%d\tCORRECT_PASS"%
				   (state.trial,pair))
		elif response == 'no':
		    ## 2=nearmiss, 4=error
		    state.trialData[position].correct = 4
		    done=1
		    log.logMessage("SCORE\tTRIAL_%d\tPAIR_%d\tCORRECT_NO"%
				   (state.trial,pair))
		elif response == 'miss':
		    ## 2=nearmiss, 4=error
		    state.trialData[position].correct = 2
		    done=1
		    log.logMessage("SCORE\tTRIAL_%d\tPAIR_%d\tCORRECT_NEARMISS"%
				   (state.trial,pair))
		elif response == 'repeat':
		    pass

	# Save the state
       	exp.saveState(state,scoreTrial=state.scoreTrial+1)

        #get the state
	state = exp.restoreState()

	# Continue Scoring ?
	if(state.scoreTrial < state.trial):
	    video.clear('black')
	    video.showCentered(Text("Continue? (y/n)"))
	    video.updateScreen(clock)
	    response = buttonChoice(clk=clock,yes=Key('Y'),no=Key('N'))
	    if response == 'no':
		break
	else:
	    video.clear('black')
	    video.showCentered(Text("You scored all current data for this\n"
				    "subject. Press any key to end."))
	    video.updateScreen(clock)
	    waitForAnyKey(clk=clock)
	    
	



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
        print "NO DATA TO SCORE FOR SUBJECT"
    else:
	# now run the subject
	score(exp, config)
 
