#!/usr/bin/python
from __future__ import with_statement

import glob
import os.path
import sys

csv_file  = "data/yuvi/session_SAVE/subdat.csv"
out_file   = open("data/yuvi/session_SAVE/subdat-rt.csv", 'w')
parse_dir = "data/yuvi/session_RUN/"
ann_ext = ".tmp"

def get_rt(trial_num, pair_num):
    with open(parse_dir + str(trial_num) + "_" + str(pair_num) + ann_ext) as f:
        for line in f:
            els = line.split('\t')
            first = els[0]
            try:
                num = int(round(float(first)))
                return num
            except:
                pass
        return -1

wavfiles = glob.glob(parse_dir + "*.wav")
parsefiles = []
for wf in wavfiles:
    basename = os.path.splitext(wf)
    parsename = basename[0] + ann_ext
    parsefiles.append(parsename)

trial_counter = -1
for line in open(csv_file, 'r'):
    if not line.startswith('%'):
        line_elements = line.split('\t')
        pair_num = int(line_elements[0])
        if pair_num == 0:
            trial_counter += 1
        for el in line_elements[0:-1]:
            out_file.write(el + '\t')
        out_file.write(str(get_rt(trial_counter, pair_num)) + '\n')
        
    else:
        out_file.write(line)

out_file.close()
