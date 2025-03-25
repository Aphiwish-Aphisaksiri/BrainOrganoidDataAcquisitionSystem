from multiprocessing import Array, Lock
import numpy as np

class ArrayBuffer:
    def __init__(self, numChannel, numSample, dtype='d'):
        """
        Initialize the ArrayBuffer with multiprocessing.Array for each channel.
        
        :param numChannel: Number of channels.
        :param numSample: Number of samples per channel.
        :param dtype: Type of the Array (e.g., 'd' for double, 'i' for integer).
        """
        self.__numChannel = numChannel
        self.__numSample = numSample
        self.__dtype = dtype

        # Create a multiprocessing.Array for each channel
        self.__data = [Array(dtype, numSample, lock=False) for _ in range(numChannel)]
        self.__lock = Lock()  # Lock for thread-safe operations
        self.__isUpdated = False

    def __to_numpy(self):
        """
        Convert the multiprocessing.Array data to a NumPy array.
        """
        return np.array([np.frombuffer(channel, dtype=self.__dtype) for channel in self.__data])

    def addData(self, data):
        """
        Add a single data point to the buffer (one value per channel).
        :param data: A list or array of values, one for each channel.
        """
        if len(data) != self.__numChannel:
            raise ValueError(f"Input data must have {self.__numChannel} channels, but got {len(data)}")

        with self.__lock:
            for i, channel in enumerate(self.__data):
                # Shift the data to the left and add the new value at the end
                channel[:-1] = channel[1:]
                channel[-1] = data[i]
            self.__isUpdated = True

    def addBatchData(self, data):
        """
        Add a batch of data to the buffer.
        :param data: A 2D array of shape (numChannel, numSample).
        """
        if data.shape != (self.__numChannel, self.__numSample):
            raise ValueError(f"Input data must have shape ({self.__numChannel}, {self.__numSample}), but got {data.shape}")

        with self.__lock:
            for i, channel in enumerate(self.__data):
                channel[:] = data[i]
            self.__isUpdated = True

    def addMultipleData(self, data):
        """
        Add multiple data points to the buffer.
        :param data: A 2D array of shape (numChannel, numPoints), where numPoints <= numSample.
        """
        numPoints = data.shape[1]
        if data.shape[0] != self.__numChannel:
            raise ValueError(f"Input data must have {self.__numChannel} channels, but got {data.shape[0]}")
        if numPoints > self.__numSample:
            raise ValueError(f"Input data has more points ({numPoints}) than buffer can hold ({self.__numSample})")

        with self.__lock:
            for i, channel in enumerate(self.__data):
                # Shift the existing data to the left and add the new data at the end
                channel[:-numPoints] = channel[numPoints:]
                channel[-numPoints:] = data[i]
            self.__isUpdated = True

    def addMultipleDataToChannel(self, data, channel_index):
        """
        Add multiple data points to a specific channel in the buffer.
        :param data: A 1D array of data points to be added to the channel.
        :param channel_index: The index of the channel where the data should be added.
        """
        numPoints = len(data)
        if channel_index < 0 or channel_index >= self.__numChannel:
            raise ValueError(f"Channel index must be between 0 and {self.__numChannel - 1}, but got {channel_index}")
        if numPoints > self.__numSample:
            raise ValueError(f"Input data has more points ({numPoints}) than buffer can hold ({self.__numSample})")
    
        with self.__lock:
            # Access the specific channel
            channel = self.__data[channel_index]
            # Shift the existing data to the left and add the new data at the end
            channel[:-numPoints] = channel[numPoints:]
            channel[-numPoints:] = data
            self.__isUpdated = True

    def getData(self, reset_flag=True):
        """
        Get the current data in the buffer as a NumPy array.
        :param reset_flag: Whether to reset the updated flag after retrieving the data.
        :return: A 2D NumPy array of shape (numChannel, numSample).
        """
        with self.__lock:
            data = self.__to_numpy()
            if reset_flag:
                self.__isUpdated = False
            return data

    def clearData(self):
        """
        Clear the buffer by resetting all values to zero.
        """
        with self.__lock:
            for channel in self.__data:
                channel[:] = [0] * self.__numSample
            self.__isUpdated = True

    def isDataUpdated(self):
        """
        Check if the buffer has been updated since the last read.
        :return: True if the buffer has been updated, False otherwise.
        """
        with self.__lock:
            return self.__isUpdated

    def setFlagDataUpdated(self):
        """
        Manually set the flag indicating that the buffer has been updated.
        """
        with self.__lock:
            self.__isUpdated = True

    def resetFlagDataUpdated(self):
        """
        Reset the flag indicating that the buffer has been updated.
        """
        with self.__lock:
            self.__isUpdated = False