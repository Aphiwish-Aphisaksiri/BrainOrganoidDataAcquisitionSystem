import numpy as np
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import CHANNELS_NUMBER, CHANNEL_ASSIGNMENT, CONVERTED_RAW_DATA_BUFFER_SIZE, COM_PORT

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
    
        # Initialize an empty array to hold synchronized data
        synchronized_data = np.zeros((self.__channelsNumber, CONVERTED_RAW_DATA_BUFFER_SIZE))
    
        # Track the current buffer index
        buffer_index = 0
    
        # Collect data from all raw data buffers and map them to the correct channels
        for com_port in COM_PORT:
            assigned_channels = CHANNEL_ASSIGNMENT[com_port]
            num_channels = len(assigned_channels)
    
            # Extract the buffers for the current COM_PORT
            buffers_for_port = self.__rawDataBuffers[buffer_index:buffer_index + num_channels]
            buffer_index += num_channels
    
            # Combine data from the buffers and map them to the correct channels
            for i, channel in enumerate(assigned_channels):
                raw_data = np.frombuffer(buffers_for_port[i].get_obj())  # Convert shared memory to NumPy array
    
                # Ensure channel_data matches the buffer size
                if len(raw_data) < CONVERTED_RAW_DATA_BUFFER_SIZE:
                    # Pad with zeros if channel_data is smaller
                    padded_data = np.zeros(CONVERTED_RAW_DATA_BUFFER_SIZE)
                    padded_data[:len(raw_data)] = raw_data
                    synchronized_data[channel - 1, :] = padded_data
                else:
                    # Truncate if channel_data is larger
                    synchronized_data[channel - 1, :] = raw_data[:CONVERTED_RAW_DATA_BUFFER_SIZE]
    
        # Ensure the shape is (CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE)
        if synchronized_data.shape != (self.__channelsNumber, CONVERTED_RAW_DATA_BUFFER_SIZE):
            raise ValueError(f"Unexpected synchronized data shape: {synchronized_data.shape}")
    
        # Add synchronized data to the synchronized data buffer
        if self.__synchronizedDataBuffer:
            self.__synchronizedDataBuffer.addBatchData(synchronized_data)
    
        # Optionally, add synchronized data to the record buffer
        if self.__recordDataBuffer:
            self.__recordDataBuffer.addBatchData(synchronized_data)