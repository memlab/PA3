#!/usr/bin/python

#This is a validation script used to analyze the log files to make sure they match the configurations.

import os
import os.path

import config

def validate():
    subjects = map(lambda s: os.getcwd() + os.sep + 'data' + os.sep + s, os.listdir('data'))
    map(lambda s: validate_subject(s), subjects)

def validate_subject(path):
    print "validating: " + path
    sesslog = open(path + os.sep + 'session.log', 'r').readlines()
    sesslog = map(lambda s: s.rstrip(), sesslog)
    sesslog = map(lambda s: s.split('\t'), sesslog)
    print sesslog[0]
    
    


if __name__ == '__main__':
    validate()
