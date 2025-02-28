import numpy as np
import os
from datetime import datetime
from scipy.io import savemat
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class RecordMat(abstractthread):
    def __init__(self):
        super().__init__()
        self.__recordBuffer = None
        self.__data = None
        self.__recording = False
        self.__channelsNumber = CHANNELS_NUMBER

    def assignBuffer(self, target):
        self.__recordBuffer = target

    def startRecording(self):
        # Generate filename based on the current date and time
        self.__recordBuffer.clearData()
        start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.__filename = os.path.join('datarecord', f'record_{start_time}.mat')
        
        # Ensure the datarecord directory exists
        os.makedirs('datarecord', exist_ok=True)
        
        # Initialize data storage
        self.__data = np.empty((0, self.__channelsNumber))
        self.__recording = True
        print(f"Recording started: {self.__filename}")
        return True

    def stopRecording(self):
        self.__recording = False
        if self.__data is not None:
            # Save the data to a .mat file
            savemat(self.__filename, {'raw_data': self.__data})
            self.__data = None
        print("Recording stopped")
        return True

    def update(self):
        if self.__recording:
            if self.__recordBuffer.isBufferFull():
                data = self.__recordBuffer.getData()
                self.__recordBuffer.clearData()
                # Append new data
                self.__data = np.vstack((self.__data, data.T))
                print("New data added")

    def close(self):
        self.stopRecording()