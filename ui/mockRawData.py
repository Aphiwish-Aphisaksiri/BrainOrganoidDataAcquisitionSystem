import random
import numpy as np
from util.abstractthread import abstractthread
import time

class MockRawData(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = 8
        self.__rawData = np.zeros(self.__channelsNumber, dtype=int)
        self.setThreadFrequency(200)
        self.count = 0
        self.starttime = time.time()

    def update(self):
        self.__rawData = np.random.randint(-100, 100, size=self.__channelsNumber)
        self.count += 1
        if time.time() - self.starttime >= 1:
            self.starttime = time.time()
            #print(self.count)
            self.count = 0
        self.__rawDataBuffer.addData(self.__rawData.tolist())

    def getRawData(self):
        self.__rawDataBuffer.addData(self.__rawData.tolist())
    
    def assignBuffer(self, target):
        self.__rawDataBuffer = target