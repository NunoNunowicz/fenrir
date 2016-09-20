#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

import difflib
import subprocess
from core import debug

class driver():
    def __init__(self):
        self.vcsaDevicePath = '/dev/vcsa'
    
    def initialize(self, environment):
        pass
    
    def shutdown(self, environment):
        pass
    
    def insert_newlines(self, string, every=64):
        return '\n'.join(string[i:i+every] for i in range(0, len(string), every))
    
    def getCurrScreen(self):
        currScreen = -1
        try:    
            currScreenFile = open('/sys/devices/virtual/tty/tty0/active','r')
            currScreen = currScreenFile.read()[3:-1]
            currScreenFile.close()
        except Exception as e:
            environment['runtime']['debug'].writeDebugOut(environment,str(e),debug.debugLevel.ERROR)   
        return currScreen

    def getIgnoreScreens(self):
        xlist = []
        try:
            x = subprocess.Popen('ps a -o tty,comm | grep Xorg', shell=True, stdout=subprocess.PIPE).stdout.read().decode()[:-1].split('\n')
        except Exception as e:
            print(e)
            return xlist
        for i in x:
            if not "grep" in i and \
              if not "ps" in i:                
                if (i[:3].lower() == 'tty'):
                    xlist.append(i[3])
        return xlist

def getCurrApplication(self):
    apps = []
    appList = []
    try:
        apps = subprocess.Popen('ps a -o comm,tty,stat', shell=True, stdout=subprocess.PIPE).stdout.read().decode()[:-1].split('\n')
    except Exception as e:
        print(e)
        return appList
    currScreen = str(self.getCurrScreen())
    for i in apps:
        i = i.split()
        i[0] = i[0].lower()
        i[1] = i[1].lower()
        if '+' in i[2]:
            if not "grep" == i[0] and \
              not "sh" == i[0] and \
              not "ps" == i[0]:
                if "tty"+currScreen in i[1]:
                    appList.append(i[0])
    return appList
    
    def update(self, environment, trigger='updateScreen'):
        newTTY = ''
        newContentBytes = b''       
        try:
            # read screen
            newTTY = self.getCurrScreen()
            vcsa = open(self.vcsaDevicePath + newTTY,'rb',0)
            newContentBytes = vcsa.read()
            vcsa.close()
            if len(newContentBytes) < 5:
                return
        except Exception as e:
            environment['runtime']['debug'].writeDebugOut(environment,str(e),debug.debugLevel.ERROR)   
            return
        screenEncoding = environment['runtime']['settingsManager'].getSetting(environment,'screen', 'encoding')
        # set new "old" values
        environment['screenData']['oldContentBytes'] = environment['screenData']['newContentBytes']
        environment['screenData']['oldContentText'] = environment['screenData']['newContentText']
        environment['screenData']['oldContentTextAttrib'] = environment['screenData']['newContentAttrib']
        environment['screenData']['oldCursor']['x'] = environment['screenData']['newCursor']['x']
        environment['screenData']['oldCursor']['y'] = environment['screenData']['newCursor']['y']
        if environment['screenData']['oldTTY'] == '-1':
            environment['screenData']['oldTTY'] = newTTY # dont recognice starting fenrir as change
        else:    
            environment['screenData']['oldTTY'] = environment['screenData']['newTTY']
        environment['screenData']['oldDelta'] = environment['screenData']['newDelta']
        environment['screenData']['oldNegativeDelta'] = environment['screenData']['newNegativeDelta']
        environment['screenData']['newTTY'] = newTTY
        environment['screenData']['newContentBytes'] = newContentBytes
        # get metadata like cursor or screensize
        environment['screenData']['lines'] = int( environment['screenData']['newContentBytes'][0])
        environment['screenData']['columns'] = int( environment['screenData']['newContentBytes'][1])
        environment['screenData']['newCursor']['x'] = int( environment['screenData']['newContentBytes'][2])
        environment['screenData']['newCursor']['y'] = int( environment['screenData']['newContentBytes'][3])
        # analyze content
        environment['screenData']['newContentText'] = environment['screenData']['newContentBytes'][4:][::2].decode(screenEncoding, "replace").encode('utf-8').decode('utf-8')
        environment['screenData']['newContentAttrib'] = environment['screenData']['newContentBytes'][5:][::2]
        environment['screenData']['newContentText'] = self.insert_newlines(environment['screenData']['newContentText'], environment['screenData']['columns'])

        if environment['screenData']['newTTY'] != environment['screenData']['oldTTY']:
            environment['screenData']['oldContentBytes'] = b''
            environment['screenData']['oldContentAttrib'] = b''
            environment['screenData']['oldContentText'] = ''
            environment['screenData']['oldCursor']['x'] = 0
            environment['screenData']['oldCursor']['y'] = 0
            environment['screenData']['oldDelta'] = ''
            environment['screenData']['oldNegativeDelta'] = ''
        # always clear current deltas
        environment['screenData']['newNegativeDelta'] = ''
        environment['screenData']['newDelta'] = ''                   
        # changes on the screen
        if (environment['screenData']['oldContentText'] != environment['screenData']['newContentText']) and \
          (environment['screenData']['newContentText'] != '' ):
            if environment['screenData']['oldContentText'] == '' and\
              environment['screenData']['newContentText'] != '':
                environment['screenData']['newDelta'] = environment['screenData']['newContentText']  
            else:
                diffStart = 0
                if environment['screenData']['oldCursor']['x'] != environment['screenData']['newCursor']['x'] and \
                  environment['screenData']['oldCursor']['y'] == environment['screenData']['newCursor']['y'] and \
                  environment['screenData']['newContentText'][:environment['screenData']['newCursor']['y']] == environment['screenData']['oldContentText'][:environment['screenData']['newCursor']['y']]:
                    diffStart = environment['screenData']['newCursor']['y'] * environment['screenData']['columns'] + environment['screenData']['newCursor']['y']
                    diff = difflib.ndiff(environment['screenData']['oldContentText'][diffStart:diffStart  + environment['screenData']['columns']],\
                      environment['screenData']['newContentText'][diffStart:diffStart  + environment['screenData']['columns']])      
                else:
                   diff = difflib.ndiff( environment['screenData']['oldContentText'][diffStart:].split('\n'),\
                     environment['screenData']['newContentText'][diffStart:].split('\n'))
                
                diffList = list(diff)

                environment['screenData']['newDelta'] = ''.join(x[2:] for x in diffList if x.startswith('+ '))             
                environment['screenData']['newNegativeDelta'] = ''.join(x[2:] for x in diffList if x.startswith('- '))

