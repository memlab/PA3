function data = analyze_subject( sub, varargin ) 
%
% DATA = ANALYZE_SUBJECT( SUB [, USECORR, USEINCORR]) reads in
% 'data/SUB/session_SAVE/subdat-rt.csv' and returns a DATA structure with the following
% fields:
%
% LL: List Length
% ACC_SP, RT_SP: Accuracy/RT at each serial position
% ACC_PP, RT_PP: Accuracy/RT at each probe position
% ACC_INT, RT_INT: Accuracy/RT for interference cond. [NO_INT, INT]
% ACC_DIR, RT_DIR: Accuracy/RT for recall direction [FORWARD BACKWARD]
%
% One may also choose which CORRECT flags to include in the analyses
% with the USECORR and USEINCORR vectors. By default, USECORR = [1 2]
% and USEINCORR = [3 4], where (1=correct, 2=nearmiss, 3=pass, 4=error,
% 5=noise)
%

if nargin == 0
  help analyze_subject
  return;
end

% which flags to treat as correct/incorrect 
usecorr = [1 2];
useincorr = [3 4];
if length(varargin) >= 1
  usecorr = varargin{1};
end
if length(varargin) >= 2
  useincorr = varargin{2};
end

% read in the data
fname = sprintf('data/%s/session_SAVE/subdat-rt.csv', sub);
[sp, pp, interference, direction, correct, rt] = ...
textread(fname, '%d%d%d%d%d%d', 'commentstyle', 'matlab');

% create data structures
data = struct('LL', [], 'ACC_SP', [], 'ACC_PP', [], 'ACC_INT', [],...
 'ACC_DIR', [], 'RT_SP', [], 'RT_PP', [], 'RT_INT', [], 'RT_DIR', []);

% find LL for this subject
data.LL = max(sp) + 1;

% loop through the serial positions and probe positions
for i=0:(data.LL-1)
  % percent correct and reaction time for each SP
  pos = find(sp == i);
  corr = pos(ismember(correct(pos), usecorr));
  incorr = pos(ismember(correct(pos), useincorr));
  data.ACC_SP(i+1) = length(corr) / (length(corr) + length(incorr));
  data.RT_SP(i+1) = mean(rt(corr));
  
  % percent correct and reaction time for each PP
  pos = find(pp == i);
  corr = pos(ismember(correct(pos), usecorr));
  incorr = pos(ismember(correct(pos), useincorr));
  data.ACC_PP(i+1) = length(corr) / (length(corr) + length(incorr));
  data.RT_PP(i+1) = mean(rt(corr));
end

for i=0:1
  % percent correct and reaction time for each interference condition
  pos = find(interference == i);
  corr = pos(ismember(correct(pos), usecorr));
  incorr = pos(ismember(correct(pos), useincorr));
  data.ACC_INT(i+1) = length(corr) / (length(corr) + length(incorr));
  data.RT_INT(i+1) = mean(rt(corr));
  
  % percent correct and reaction time for each direction of recall
  pos = find(direction == i);
  corr = pos(ismember(correct(pos), usecorr));
  incorr = pos(ismember(correct(pos), useincorr));
  data.ACC_DIR(i+1) = length(corr) / (length(corr) + length(incorr));
  data.RT_DIR(i+1) = mean(rt(corr));
end
