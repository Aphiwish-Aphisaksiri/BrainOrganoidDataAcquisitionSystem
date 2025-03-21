import numpy as np
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class Buffer():
    def __init__(self, numChannel=CHANNELS_NUMBER, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE):
        self.__data = np.zeros((numChannel, numSample), dtype=np.float64)
        self.__isUpdated = False
        self.__dataCount = 0  # Counter to track the number of data points added

    def addData(self, data):
        self.__data = np.roll(self.__data, -1, axis=1)
        self.__data[:, -1] = data
        self.__dataCount += 1
        self.setFlagDataUpdated()

    def addBatchData(self, data):
        if data.shape != self.__data.shape:
            raise ValueError(f"Input data must have shape {self.__data.shape}, but got {data.shape}")
        self.__data = np.array(data)
        self.__dataCount = self.__data.shape[1]
        self.setFlagDataUpdated()

    def addMultipleData(self, data):
        num_points = data.shape[1]
        if num_points > self.__data.shape[1]:
            raise ValueError(f"Input data has more points ({num_points}) than buffer can hold ({self.__data.shape[1]})")
        self.__data = np.roll(self.__data, -num_points, axis=1)
        self.__data[:, -num_points:] = data
        self.__dataCount += num_points
        self.setFlagDataUpdated()

    def getData(self, reset_flag=True):
        if reset_flag:
            self.resetFlagDataUpdated()
        return self.__data
    
    def clearData(self):
        self.__data = np.zeros_like(self.__data)
        self.__dataCount = 0  # Reset the counter
        self.setFlagDataUpdated()
        #print("Buffer cleared:", self.__data)  # Debugging statement

    def isBufferFull(self):
        is_full = self.__dataCount >= self.__data.shape[1]
        #print("Buffer full check:", is_full)  # Debugging statement
        return is_full
    
    def isDataUpdated(self):
        return self.__isUpdated
    
    def setFlagDataUpdated(self):
        self.__isUpdated = True

    def resetFlagDataUpdated(self):
        self.__isUpdated = False