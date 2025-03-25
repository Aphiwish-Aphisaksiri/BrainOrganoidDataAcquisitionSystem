import numpy as np
import time
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import CHANNELS_NUMBER, CHANNEL_ASSIGNMENT, CONVERTED_RAW_DATA_BUFFER_SIZE, COM_PORT

class DataSynchronize(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffer = []  # List to hold raw data buffers from multiple DAQ instances
        self.__synchronizedDataBuffer = None
        self.__recordDataBuffer = None
        self.__samplesReceivedPerSecond = np.zeros(len(COM_PORT))
        self.__startTime = time.time()

    def assignRawDataBufferInstances(self, buffers):
        """Assign raw data buffers (multiprocessing.Array) for all DAQ instances."""
        self.__rawDataBuffer = buffers

    def assignSynchronizedDataBuffer(self, buffer):
        self.__synchronizedDataBuffer = buffer

    def assignRecordDataBuffer(self, buffer):
        self.__recordDataBuffer = buffer

    def assignSamplesReceivedPerSecondBuffers(self, buffers):
        self.__samplesReceivedPerSecondBuffer = buffers

    def getSamplesReceivedPerSecond(self):
        """Return a formatted string of samples received per second for each COM_PORT."""
        return ", ".join(
            f"{com_port}: {int(self.__samplesReceivedPerSecond[daq_index])}"
            for daq_index, com_port in enumerate(COM_PORT)
        )

    def update(self):
        if not self.__rawDataBuffer:
            print("Raw data buffer is not assigned.")
            return

        currentTime = time.time()
        if currentTime - self.__startTime >= 1:
            self.__startTime = currentTime
            samples_received = self.__samplesReceivedPerSecondBuffer.getData()
            # print(f"Samples received per second: {samples_received}")

        # Synchronize data from raw data buffer
        synchronized_data = self.__rawDataBuffer.getData()
        self.__synchronizedDataBuffer.addBatchData(synchronized_data)

        # Optionally, add synchronized data to the record buffer
        if self.__recordDataBuffer:
            self.__recordDataBuffer.addBatchData(synchronized_data)