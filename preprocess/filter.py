from scipy.signal import butter, lfilter, iirnotch
import numpy as np
from util.abstractthread import abstractthread
from util.config import HIGH_PASS_FILTER, LOW_PASS_FILTER, GAIN, NOTCH_FILTER, CHANNELS_NUMBER, SAMPLING_RATE

class Filter(abstractthread):
    def __init__(self):
        super().__init__()
        self.setThreadFrequency(30)
        self.__highPassFilter = HIGH_PASS_FILTER
        self.__lowPassFilter = LOW_PASS_FILTER
        self.__gain = GAIN
        self.__notchFilter = NOTCH_FILTER

        # Design filters
        self.__highPassB, self.__highPassA = self.__design_highpass_filter()
        self.__lowPassB, self.__lowPassA = self.__design_lowpass_filter()
        self.__notchB, self.__notchA = self.__design_notch_filter()

    def assignInletBuffer(self, target):
        self.__rawDataBuffer = target

    def assignOutletBuffer(self, target):
        self.__filteredDataBuffer = target

    def update(self):
        if self.__rawDataBuffer.isDataUpdated():
            # Get data from inlet buffer
            rawData = self.__rawDataBuffer.getData()
            # Filter data
            filteredData = self.__filter(rawData)
            # Assign filtered data to outlet buffer
            self.__filteredDataBuffer.addBatchData(filteredData)

    def __filter(self, rawData):
        filteredData = np.zeros_like(rawData)
        for i in range(CHANNELS_NUMBER):
            channel_data = rawData[i, :]
            # Apply high-pass filter
            channel_data = lfilter(self.__highPassB, self.__highPassA, channel_data)
            # Apply low-pass filter
            channel_data = lfilter(self.__lowPassB, self.__lowPassA, channel_data)
            # Apply notch filter
            channel_data = lfilter(self.__notchB, self.__notchA, channel_data)
            # Apply gain
            channel_data *= self.__gain
            filteredData[i, :] = channel_data
        return filteredData

    def __design_highpass_filter(self):
        nyquist = 0.5 * SAMPLING_RATE  # Use the sampling rate from config
        normal_cutoff = self.__highPassFilter / nyquist
        b, a = butter(1, normal_cutoff, btype='high', analog=False)
        return b, a

    def __design_lowpass_filter(self):
        nyquist = 0.5 * SAMPLING_RATE  # Use the sampling rate from config
        normal_cutoff = self.__lowPassFilter / nyquist
        b, a = butter(1, normal_cutoff, btype='low', analog=False)
        return b, a

    def __design_notch_filter(self):
        nyquist = 0.5 * SAMPLING_RATE  # Use the sampling rate from config
        freq = self.__notchFilter / nyquist
        b, a = iirnotch(freq, Q=30)  # Q factor of 30
        return b, a
    
    def setHighPassFilter(self, value):
        self.__highPassFilter = value
        self.__highPassB, self.__highPassA = self.__design_highpass_filter()
        return self.__highPassFilter

    def setLowPassFilter(self, value):
        self.__lowPassFilter = value
        self.__lowPassB, self.__lowPassA = self.__design_lowpass_filter()
        return self.__lowPassFilter

    def setNotchFilter(self, value):
        self.__notchFilter = value
        self.__notchB, self.__notchA = self.__design_notch_filter()
        return self.__notchFilter

    def setGain(self, value):
        self.__gain = value
        return self.__gain