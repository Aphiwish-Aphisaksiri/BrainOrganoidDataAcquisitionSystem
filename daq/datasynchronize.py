import numpy as np
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CHANNELS_PER_PORT, CONVERTED_RAW_DATA_BUFFER_SIZE

class DataSynchronize(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffers = []  # List to hold raw data buffers from multiple DAQ instances
        self.__synchronizedDataBuffer = None
        self.__recordDataBuffer = None

    def assignRawDataBuffer(self, buffer, instance_index):
        # Ensure the list is large enough to hold buffers for all instances
        while len(self.__rawDataBuffers) <= instance_index:
            self.__rawDataBuffers.append(None)
        self.__rawDataBuffers[instance_index] = buffer

    def assignSynchronizedDataBuffer(self, buffer):
        self.__synchronizedDataBuffer = buffer

    def assignRecordDataBuffer(self, buffer):
        self.__recordDataBuffer = buffer

    def update(self):
        if not self.__rawDataBuffers or None in self.__rawDataBuffers:
            print("Not all raw data buffers are assigned.")
            return

        # Collect data from all raw data buffers
        combined_data = []
        for buffer in self.__rawDataBuffers:
            raw_data = buffer.getData(reset_flag=False)  # Get data without resetting the flag
            combined_data.append(raw_data)

        # Combine data along the channel axis
        synchronized_data = np.hstack(combined_data)  # Combine along the second axis (channels)

        # Ensure the shape is (CONVERTED_RAW_DATA_BUFFER_SIZE, CHANNELS_NUMBER)
        if synchronized_data.shape != (CONVERTED_RAW_DATA_BUFFER_SIZE, self.__channelsNumber):
            raise ValueError(f"Unexpected synchronized data shape: {synchronized_data.shape}")

        # Add synchronized data to the synchronized data buffer
        if self.__synchronizedDataBuffer:
            self.__synchronizedDataBuffer.addBatchData(synchronized_data)

        # Optionally, add synchronized data to the record buffer
        if self.__recordDataBuffer:
            self.__recordDataBuffer.addBatchData(synchronized_data)