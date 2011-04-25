function events = makePA3events(subjDir)


filename = fullfile(subjDir,'events.csv');
fid = fopen(filename);
C = textscan(fid,'%s%d%d%s%d%d%d%d%d%s%s%d%s%s%d%d%s%d','delimiter','\t','headerlines',1);
fclose(fid);


for te = 1:length(C{1})    
    sessEvents(te) = struct('subj',C{1}(te),'trial',C{2}(te),'pair',C{3}(te),'event_type',C{4}(te),'stimmed',C{5}(te),'elecno',C{6}(te),'current',C{7}(te),'serial_pos',C{8}(te),'probe_pos',C{9}(te),'study_1',C{10}(te),'study_2',C{11}(te),'cue_direction',C{12}(te),'probe_word',C{13}(te),'resp_word',C{14}(te),'intrusion',C{15}(te),'RT',C{16}(te),'mstime',C{17}(te),'msoffset',C{18}(te));
    sessEvents(te).mstime = str2num(sessEvents(te).mstime);
end

rawevents = sessEvents;
syncEvents = rawevents(strcmp({rawevents.event_type},'sync'));
pulseEvents = rawevents(strcmp({rawevents.event_type},'pulse'));
newevents = rawevents((strcmp({rawevents.event_type},'study'))|(strcmp({rawevents.event_type},'cue')));


% LAG calculation assumes the two items next to each other have a lag of 1
% (not 0 items in between). LAG applies only to the word-related events;  
% this code will populate a LAG field for all events, both study and cue, 
% although this is a bit redundant

testPosition = [newevents.serial_pos];
probePosition = [newevents.probe_pos];

%reset the values to make calculations easy
probePosition = probePosition +4;
lag = probePosition - testPosition;

for ne = 1:size(newevents,2)
    
    newevents(ne).lag = lag(ne);
    newevents(ne).pass = strcmp({newevents(ne).resp_word},'PASS');
    
end


forward_events = newevents([newevents.cue_direction]==0);
backward_events = newevents([newevents.cue_direction]==1);

for fe = 1:size(forward_events,2)
    
    forward_events(fe).correct =  strcmp({forward_events(fe).study_2},{forward_events(fe).resp_word});
    if (strcmp({forward_events(fe).study_2},{forward_events(fe).resp_word}) & [forward_events(fe).pass]==0)
        forward_events(fe).intrusion=1;
    else
        forward_events(fe).intrusion=0;        
    end
    
end


for be = 1:size(backward_events,2)
    
    backward_events(be).correct = strcmp({backward_events(be).study_1},{backward_events(be).resp_word});    
    if (strcmp({backward_events(be).study_1},{backward_events(be).resp_word})&[backward_events(be).pass]==0)        
        backward_events(be).intrusion=1;
    else
        backward_events(be).intrusion=0;
    end
    
end

for se = 1:size(syncEvents,2)
    
    syncEvents(se).correct = 999;
    syncEvents(se).lag = 999;
    syncEvents(se).intrusion = 999;
end

for pe = 1:size(pulseEvents,2)
    
    pulseEvents(pe).correct = 999;
    pulseEvents(pe).lag = 999;
    pulseEvents(pe).intrusion = 999;
     
end


%need to add in the pulse events once they have
events = [forward_events backward_events];
