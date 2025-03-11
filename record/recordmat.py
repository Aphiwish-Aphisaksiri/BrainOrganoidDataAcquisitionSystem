import numpy as np
import os
from datetime import datetime
from scipy.io import savemat
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, RECORD_CHANNELS, ON_ELECTRODE_CHANNEL_COUNT, SAMPLING_RATE

class RecordMat(abstractthread):
    def __init__(self):
        super().__init__()
        self.__recordBuffer = None
        self.__data = None
        self.__recording = False
        self.__channelsNumber = CHANNELS_NUMBER
        self.__recordingChannels = []
        self.channelRecordInit()

        print("Current Record format: .mat")

    def assignBuffer(self, target):
        self.__recordBuffer = target

    def channelRecordInit(self):
        for i in range(1, ON_ELECTRODE_CHANNEL_COUNT+1):
            if RECORD_CHANNELS == "even" and i % 2 == 0:
                self.__recordingChannels.append(i)
            elif RECORD_CHANNELS == "odd" and i % 2 == 1:
                self.__recordingChannels.append(i)
            elif RECORD_CHANNELS == "all":
                self.__recordingChannels.append(i)
    
    def getChannelRecordInit(self):
        return self.__recordingChannels
    
    def setChannelRecord(self, channels):
        self.__recordingChannels = channels
        return self.__recordingChannels
    
    def convertRecordingChannel(self):
        converted_channels = np.array(self.__recordingChannels, dtype=np.double).reshape(1, -1)
        return converted_channels
    
    def convertSamplingRate(self):
        return np.array([[SAMPLING_RATE]], dtype=np.double)

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
            # Combine all data into a single dictionary
            mat_data = {
                'dat': self.__data,
                'channels': self.convertRecordingChannel(),
                'fs': self.convertSamplingRate(),
                #'time': datetime.now().strftime("%Y%m%d_%H%M%S")
            }
            # Save the data to a .mat file
            savemat(self.__filename, mat_data)
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