'''
TODO: 
[X] implement bandpass filter 0.25-3000 Hz
[X] implement Gain 0.5-2000
'''

from util.abstractthread import abstractthread

class Filter(abstractthread):
    def __init__(self):
        super().__init__()

    def assignInletBuffer(self, target):
        self.__rawDataBuffer = target

    def update(self):
        pass