#!/usr/bin/python

#This is a validation script used to analyze the log files to make sure they match the configurations.

import os
import os.path

def validate():
    subjects = map(lambda f: os.path.abspath(f), os.listdir('data'))
    


if __name__ == '__main__':
    validate()
