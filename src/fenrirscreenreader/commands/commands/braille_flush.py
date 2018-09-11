#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from fenrirscreenreader.core import debug

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
    def shutdown(self):
        pass 
    def getDescription(self):
        return _('Clear the Braille device if it is displaying a message')
    def run(self):
        self.env['runtime']['outputManager'].clearFlushTime()
    def setCallback(self, callback):
        pass
