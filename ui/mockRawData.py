import random
import numpy as np
from util.abstractthread import abstractthread
import time
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class MockRawData(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawData = np.zeros(self.__channelsNumber, dtype=int)
        self.count = 0
        self.starttime = time.time()

        # Set mock data frequency
        self.setThreadFrequency(8000)

        print("Current Data source: Mock data")

    def update(self):
        self.__rawData = np.random.randint(-100, 100, size=self.__channelsNumber)
        self.count += 1
        if time.time() - self.starttime >= 1:
            self.starttime = time.time()
            #print(self.count)
            self.count = 0
        self.__rawDataBuffer.addData(self.__rawData.tolist())
        self.__recordBuffer.addData(self.__rawData.tolist())

    def getRawData(self):
        self.__rawDataBuffer.addData(self.__rawData.tolist())
    
    def assignBuffer(self, target):
        self.__rawDataBuffer = target

    def assignRecordBuffer(self, target):
        self.__recordBuffer = target

    def close(self):
        # Just for compatibility with daq.py
        pass