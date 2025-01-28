import numpy as np
import struct
from util.abstractthread import abstractthread
from util.buffer import Buffer
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

        self.setThreadFrequency(16)

    def assignInletBuffer(self, unconvertedBuffer):
        self.__unconvertedRawDataBuffer = unconvertedBuffer

    def assignOutletBuffer(self, convertedBuffer):
        self.__rawDataBuffer = convertedBuffer

    def convertByteArrayToData(self, byteArray):
        multiplier = (2 * (VREF / GAIN)) / (2 ** 24)

        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator

        if header != 0xAA or term != 0xFF:
            print(f"Invalid package: header={header}, term={term}")
            return None, None, None

        header_int = header  # header is already an integer

        # Unpack the data using struct
        data_int24 = np.array([struct.unpack('>i', b'\x00' + data[i:i+3])[0] for i in range(0, len(data), 3)])

        # Convert to signed 24-bit integer
        data_int24 = np.where(data_int24 >= 2**23, data_int24 - 2**24, data_int24)

        # Convert to voltage
        data_voltage = data_int24 * multiplier

        # Reshape the data to maintain the structure of 8 channels
        data_voltage = data_voltage.reshape(self.__channelsNumber, -1)

        return header_int, data_voltage, term

    def update(self):
        unconvertedData = self.__unconvertedRawDataBuffer.getData()
        packages = []
        rawDataArray = unconvertedData.flatten()
        while len(rawDataArray) >= self.__packageLen:
            package = rawDataArray[:self.__packageLen]
            rawDataArray = rawDataArray[self.__packageLen:]
            packages.append(package)

        for package in packages:
            header, data_voltage, term = self.convertByteArrayToData(package)
            if data_voltage is not None:
                self.__rawDataBuffer.addMultipleData(data_voltage)