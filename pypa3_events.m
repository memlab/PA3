function events = pypa3_events(session_dir, subject_id, session_number)
%PYPA3_EVENTS   Create an events structure for a session of pyEPL pypa3.
%
%  events = pypa3_events(session_dir, subject_id, session_number)
%
%  INPUTS:
%     session_dir:  path to the directory containing data for this session.
%
%      subject_id:  string giving the identifier for this subject.
%
%  session_number:  integer indicating the session number.
%
%  OUTPUTS:
%          events:  structure containing one element for each event in
%                   the experiment.
%
%  EXAMPLE:
%   subject_id = 'LTP031';
%   session_number = 1;
%   session_dir = '/data3/eeg/scalp/apem_e7_ltp/LTP031/session_0';
%   events = pypa3_events(session_dir, subject_id, session_number);

% input checks
if ~exist('session_dir','var')
  error('You must provide the path to the session directory.')
end
if ~exist('subject_id','var')
  warning('EventsCreation:noSubjectId', 'No subject id specified. "subject" field will be empty.')
  subject_id = '';
end
if ~exist('session_number','var')
  warning('EventsCreation:noSessionNumber', 'No session number specified. "session" field will be empty.')
  session_number = [];
end

% create the events structure
event = struct( ...               
               'subject', subject_id,  ...
               'session', session_number, ...
               'mode', '',             ...
               'type', '',             ...
               'mstime', NaN,           ...
               'Xcoord', NaN,           ...
               'Ycoord', NaN,           ...
               'eegfile', '',          ...
               'eegoffset', NaN);

% read the logfile
fid = fopen(fullfile(session_dir, 'session.log'), 'r');
c = textscan(fid, '%s%s%s%s%s%s%s', 'Delimiter','\t', 'EmptyValue',NaN);
[mstime,code,type,stim1a,stim1b,stim2a,stim2b] = deal(c{:});

% initialize with the maximum number of events
events = repmat(event,1,length(mstime));

% fill in the struct with the data
eventno = 0;
for e = 1:length(mstime)
  % check whether this is a line with interesting data
  if ~(strcmp(stim1a(e),'0') | strcmp(stim1a(e),'Logging'))
    eventno = eventno +1;
    thisStim = stim1a(e);
    thismstime = mstime{e};
    events(eventno).mstime = str2num(thismstime);
    if strcmp(type(e),'SOUND')
      switch thisStim{1}(10)
        case 'c'
        events(eventno).mode = 'open_close';
        events(eventno).type = 'close';
        case 'o'
        events(eventno).mode = 'open_close';
        events(eventno).type = 'open';
        case 'l'
        events(eventno).mode = 'left_right';
        events(eventno).type = 'left';
        case 'r' 
        events(eventno).mode = 'left_right';
        events(eventno).type = 'right';
        case 'b'
        events(eventno).mode = 'blink';
        events(eventno).type = 'blink';
        case 'u'
        events(eventno).mode = 'up_down';
        events(eventno).type = 'up';
        case 'd'
        events(eventno).mode = 'up_down';
        events(eventno).type = 'down';
      end %switch over spoken instructions
      else
      x = stim1b(e);
      y = stim2b(e);
      events(eventno).mode = 'track';
      events(eventno).Xcoord = str2num(x{1});
      events(eventno).Ycoord = str2num(y{1});
    end %if then over trackball vs spoken instructions
  end
end %loop over events
events = events(1:eventno);
