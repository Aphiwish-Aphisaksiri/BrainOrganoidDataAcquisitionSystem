import numpy as np
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import CHANNELS_NUMBER, CHANNELS_PER_PORT, CONVERTED_RAW_DATA_BUFFER_SIZE, COM_PORT

class DataSynchronize(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffers = []  # List to hold raw data buffers from multiple DAQ instances
        self.__synchronizedDataBuffer = None
        self.__recordDataBuffer = None

    def assignRawDataBufferInstances(self, buffers):
        """Assign raw data buffers (multiprocessing.Array) for all DAQ instances."""
        self.__rawDataBuffers = buffers

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
            # Convert multiprocessing.Array to NumPy array
            raw_data = np.frombuffer(buffer.get_obj())  # Convert shared memory to NumPy array
            # Reshape the data to match the expected dimensions (channels x samples)
            raw_data = raw_data.reshape((CHANNELS_PER_PORT, -1))
            combined_data.append(raw_data)

        # Combine data along the channel axis
        synchronized_data = np.vstack(combined_data)  # Combine along the first axis (channels)

        # Ensure the shape is (CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE)
        if synchronized_data.shape != (self.__channelsNumber, CONVERTED_RAW_DATA_BUFFER_SIZE):
            raise ValueError(f"Unexpected synchronized data shape: {synchronized_data.shape}")

        # Add synchronized data to the synchronized data buffer
        if self.__synchronizedDataBuffer:
            self.__synchronizedDataBuffer.addBatchData(synchronized_data)

        # Optionally, add synchronized data to the record buffer
        if self.__recordDataBuffer:
            self.__recordDataBuffer.addBatchData(synchronized_data)