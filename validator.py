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
    assert sesslog[0][-1] == 'Logging Begins'
    assert sesslog[-1][-1] == 'Logging Ends'

    validate_study(path)
    validate_recall(path)
    
    print path + ' is valid'
    print


def validate_study(path):
    pass


def validate_recall(path):
    pass
    

if __name__ == '__main__':
    validate()
