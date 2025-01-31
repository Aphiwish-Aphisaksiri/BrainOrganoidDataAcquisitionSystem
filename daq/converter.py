import numpy as np
import time
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, BYTES_PER_SAMPLE, HEADER_LEN, TERM_LEN, VREF, GAIN, UNCONVERTED_RAW_DATA_BUFFER_SIZE

class Converter(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__bytesPerSample = BYTES_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__payloadLen = self.__channelsNumber * self.__bytesPerSample
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.setThreadFrequency(32)

        # FOR DEBUGGING
        self.__startTime = time.time()
        self.__packageCount = 0

    def assignInletBuffer(self, unconvertedBuffer):
        self.__unconvertedRawDataBuffer = unconvertedBuffer

    def assignOutletBuffer(self, convertedBuffer):
        self.__rawDataBuffer = convertedBuffer

    def convertByteArrayToData(self, byteArray):
        multiplier = (2 * (VREF / GAIN)) / (2 ** 24)

        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator

        if header != 170 or term != 255:
            print(f"Invalid package: header={header}, term={term}")
            return None, None, None

        header_int = header  # header is already an integer

        # Unpack the data using bitwise operations
        data_int24 = np.array([(data[i] << 16) | (data[i+1] << 8) | data[i+2] for i in range(0, len(data), 3)])

        # Convert to signed 24-bit integer
        data_int24 = np.where(data_int24 >= 2**23, data_int24 - 2**24, data_int24)

        # Convert to voltage
        data_voltage = data_int24 * multiplier

        # Reshape the data to maintain the structure of 8 channels
        data_voltage = data_voltage.reshape(self.__channelsNumber, -1)

        return header_int, data_voltage, term

    def update(self):
        if self.__unconvertedRawDataBuffer.isDataUpdated():
            unconvertedData = self.__unconvertedRawDataBuffer.getData()
            # print(unconvertedData)
            if unconvertedData.shape == (1, UNCONVERTED_RAW_DATA_BUFFER_SIZE):
                rawDataArray = unconvertedData.flatten()
                # print(rawDataArray)

                # print(rawDataArray)
                while len(rawDataArray) >= self.__packageLen:
                    # Check for header
                    if rawDataArray[0] == 170:
                        package = rawDataArray[:self.__packageLen]
                        #print(package)
                        rawDataArray = rawDataArray[self.__packageLen:]
                        header, data_voltage, term = self.convertByteArrayToData(package)
                        #print(data_voltage)
                        if header is not None and data_voltage is not None and term is not None:
                            self.__rawDataBuffer.addData(data_voltage.flatten())
                        self.__packageCount = self.__packageCount + 1
                    else:
                        rawDataArray = rawDataArray[1:]
                currentTime = time.time()
                if currentTime - self.__startTime >= 1:
                    print(f"Packages received in the last second: {self.__packageCount}")
                    self.__packageCount = 0
                    self.__startTime = currentTime
            else:
                print(f"Invalid unconvertedData shape: {unconvertedData.shape}")