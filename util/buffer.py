import numpy as np

class Buffer():
    def __init__(self, numChannel, numSample):
        self.__data = np.zeros((numChannel, numSample), dtype=np.float64)

        self.__isUpdated = False

    def addData(self, data):
        self.__data = np.roll(self.__data, -1, axis=1)
        self.__data[:, -1] = data
        self.setFlagDataUpdated()

    def addBatchData(self, data):
        if data.shape != self.__data.shape:
            raise ValueError(f"Input data must have shape {self.__data.shape}, but got {data.shape}")
        self.__data = np.array(data)
        self.setFlagDataUpdated()

    def getData(self):
        self.__isUpdated = False
        self.resetFlagDataUpdated()
        return self.__data
    
    def isDataUpdated(self):
        return self.__isUpdated
    
    def setFlagDataUpdated(self):
        self.__isUpdated = True

    def resetFlagDataUpdated(self):
        self.__isUpdated = False