import h5py
import numpy as np
import os
from datetime import datetime
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class Record(abstractthread):
    def __init__(self):
        super().__init__()
        self.__recordBuffer = None
        self.__hdf5_file = None
        self.__hdf5_dataset = None
        self.__recording = False
        self.__channelsNumber = CHANNELS_NUMBER

        print("Current Record format: .h5")

    def assignBuffer(self, target):
        self.__recordBuffer = target

    def startRecording(self):
        # Generate filename based on the current date and time
        self.__recordBuffer.clearData()
        start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join('datarecord', f'record_{start_time}.h5')
        
        # Ensure the datarecord directory exists
        os.makedirs('datarecord', exist_ok=True)
        
        # Open the HDF5 file
        self.__hdf5_file = h5py.File(filename, 'w')
        self.__hdf5_dataset = self.__hdf5_file.create_dataset(
            'raw_data',
            shape=(0, self.__channelsNumber),
            maxshape=(None, self.__channelsNumber),
            dtype=np.float64
        )
        self.__recording = True
        print(f"Recording started: {filename}")
        return True

    def stopRecording(self):
        self.__recording = False
        if self.__hdf5_file:
            self.__hdf5_file.close()
            self.__hdf5_file = None
            self.__hdf5_dataset = None
        print("Recording stopped")
        return True

    def update(self):
        if self.__recording:
            if self.__recordBuffer.isBufferFull():
                data = self.__recordBuffer.getData()
                self.__recordBuffer.clearData()
                #print(data.shape)
                #print(data[:, -1])
                current_shape = self.__hdf5_dataset.shape
                new_shape = (current_shape[0] + data.shape[1], self.__channelsNumber)
                self.__hdf5_dataset.resize(new_shape)
                self.__hdf5_dataset[-data.shape[1]:, :] = data.T
                # print("New data added")

    def close(self):
        self.stopRecording()