import h5py
import numpy as np
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class Record(abstractthread):
    def __init__(self):
        super().__init__()
        self.__recordBuffer = None
        self.__hdf5_file = None
        self.__hdf5_dataset = None
        self.__recording = False
        self.__channelsNumber = CHANNELS_NUMBER

    def assignBuffer(self, target):
        self.__recordBuffer = target

    def startRecording(self, filename='raw_data.h5'):
        self.__hdf5_file = h5py.File(filename, 'w')
        self.__hdf5_dataset = self.__hdf5_file.create_dataset(
            'raw_data',
            shape=(0, self.__channelsNumber),
            maxshape=(None, self.__channelsNumber),
            dtype=np.float64
        )
        self.__recording = True
        print("Recording started")

    def stopRecording(self):
        self.__recording = False
        if self.__hdf5_file:
            self.__hdf5_file.close()
            self.__hdf5_file = None
            self.__hdf5_dataset = None
        print("Recording stopped")

    def update(self):
        if self.__recording and self.__recordBuffer.isDataUpdated():
            data = self.__recordBuffer.getData()
            terminator_indices = np.where(data == 99)[1]  # Find terminator indices
            if len(terminator_indices) > 0:
                data = data[:, :terminator_indices[0]]  # Trim data at the first terminator
            current_shape = self.__hdf5_dataset.shape
            new_shape = (current_shape[0] + data.shape[1], self.__channelsNumber)
            self.__hdf5_dataset.resize(new_shape)
            self.__hdf5_dataset[-data.shape[1]:, :] = data.T
            print("New data added")

    def close(self):
        self.stopRecording()