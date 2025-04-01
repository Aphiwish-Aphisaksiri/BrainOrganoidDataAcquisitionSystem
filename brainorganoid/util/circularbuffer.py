import numpy as np
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class CircularBuffer():
    def __init__(self, numChannel=CHANNELS_NUMBER, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE):
        """
        Initialize the circular buffer.
        :param numChannel: Number of channels (rows).
        :param numSample: Number of samples (columns).
        """
        self.__data = np.zeros((numChannel, numSample), dtype=np.float64)
        self.__writeIndex = 0  # Pointer to the next write position
        self.__isFull = False  # Flag to indicate if the buffer is full
        self.__isUpdated = False  # Flag to indicate if the buffer has been updated

    def addData(self, data):
        """
        Add a single data point to the buffer.
        :param data: A 1D array of shape (numChannel,).
        """
        if data.shape[0] != self.__data.shape[0]:
            raise ValueError(f"Input data must have shape ({self.__data.shape[0]},), but got {data.shape}")

        # Write the data at the current write index
        self.__data[:, self.__writeIndex] = data

        # Update the write index
        self.__writeIndex = (self.__writeIndex + 1) % self.__data.shape[1]

        # Mark the buffer as full if the write index wraps around
        if self.__writeIndex == 0:
            self.__isFull = True
        
        # Set the updated flag
        self.__isUpdated = True

    def addMultipleData(self, data):
        """
        Add multiple data points to the buffer.
        :param data: A 2D array of shape (numChannel, numPoints).
        """
        numPoints = data.shape[1]
        if data.shape[0] != self.__data.shape[0]:
            raise ValueError(f"Input data must have shape ({self.__data.shape[0]}, numPoints), but got {data.shape}")

        for i in range(numPoints):
            self.addData(data[:, i])
        
        # Set the updated flag
        self.__isUpdated = True

    def addBatchData(self, data):
        """
        Add a batch of data points to the buffer.
        :param data: A 2D array of shape (numChannel, numSample).
        """
        if data.shape[0] != self.__data.shape[0]:
            raise ValueError(f"Input data must have shape ({self.__data.shape[0]}, numSample), but got {data.shape}")

        numSamples = data.shape[1]
        self.__data = data
        
        # Set the updated flag
        self.__isUpdated = True

        # Set the full flag
        self.__isFull = True

    def getData(self, reset_flag=True):
        """
        Retrieve the data from the buffer in the correct order.
        :return: A 2D array of shape (numChannel, numSample).
        """
        # Reset the updated flag
        if reset_flag:
            self.__isUpdated = False

        if not self.__isFull:
            # If the buffer is not full, return only the valid portion
            return self.__data
        else:
            # If the buffer is full, return the data in the correct order
            return np.hstack((self.__data[:, self.__writeIndex:], self.__data[:, :self.__writeIndex]))

    def getCircularData(self, reset_flag=True):
        # Reset the updated flag
        if reset_flag:
            self.__isUpdated = False

        return self.__data
    
    def getWriteIndex(self):
        """
        Get the current write index.
        :return: The current write index.
        """
        return self.__writeIndex
        
    def isDataUpdated(self):
        """
        Check if the buffer has been updated.
        :return: True if the buffer has been updated, False otherwise.
        """
        return self.__isUpdated

    def isBufferFull(self):
        """
        Check if the buffer is full.
        :return: True if the buffer is full, False otherwise.
        """
        return self.__isFull

    def clearData(self):
        """
        Clear the buffer and reset its state.
        """
        self.__data.fill(0)
        self.__writeIndex = 0
        self.__isFull = False

    def resetIsFull(self):
        """
        Clear Is Full flag
        """
        if self.__isFull:
            self.__isFull = False