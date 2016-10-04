#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from core import debug
from utils import line_utils
from utils import char_utils

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
    def shutdown(self):
        pass 
    def getDescription(self):
        return 'set review cursor to end of current line and display the content'        

    def run(self):
        cursorPos = self.env['runtime']['cursorManager'].getReviewOrTextCursor()
        x, y, currLine = \
          line_utils.getCurrentLine(cursorPos['x'], cursorPos['y'], self.env['screenData']['newContentText'])
        
        self.env['runtime']['cursorManager'].setReviewCursorPosition((len(currLine) - len(currLine.lstrip()))
        ,cursorPos['y'])
        self.env['screenData']['newCursorReview']['x'], self.env['screenData']['newCursorReview']['y'], currChar = \
          char_utils.getCurrentChar(self.env['screenData']['newCursorReview']['x'], self.env['screenData']['newCursorReview']['y'], self.env['screenData']['newContentText'])       
        if currChar.isspace():
            self.env['runtime']['outputManager'].presentText("line is empty" ,interrupt=True)
        else:
            self.env['runtime']['outputManager'].presentText(currChar ,interrupt=True, ignorePunctuation=True, announceCapital=True)        
            self.env['runtime']['outputManager'].presentText("first char in line indent " + str(len(currLine) - len(currLine.lstrip())), interrupt=False)
   
    def setCallback(self, callback):
        pass
