import serial
import numpy as np

class Daq():
    def __init__(self):
        self.__channelsNumber = 8
        self.__bytesPerSample = 3 # 24 bits
        self.__stackCount = 5
        self.__typeByteLen = 1
        self.__lengthLen = 1
        self.__checkSumLen = 1
        self.__termLen = 1
        self.__payloadLen = self.__channelsNumber * self.__bytesPerSample * self.__stackCount

        self.__ser = serial.Serial('COM10', 1843200)
        self.__rawData = bytearray()
    
    def convertByteArrayToData(self, byteArray):
        dataType = byteArray[0] # first byte is the data type
        length = byteArray[1]   # second byte is the length of the data
        data = byteArray[2:-3]  # the data is from the third byte to the third last byte
        checkSum = byteArray[-2]  # second last byte is the checksum
        term = byteArray[-1]    # last byte is the terminator

        dataType_int = int.from_bytes(dataType, byteorder='big')

        length_int = int.from_bytes(length, byteorder='big')

        if length_int != len(self.__payloadLen) + len(self.__checkSumLen) + len(self.__termLen):
            raise ValueError("Byte array length does not match the expected length.")

        data_int24 = np.frombuffer(data, dtype=np.int8).reshape(-1, 3)
        data_int24 = data_int24[:, 0] + (data_int24[:, 1] << 8) + (data_int24[:, 2] << 16)

        checkSum_int = int.from_bytes(checkSum, byteorder='big')
        #TODO: implement checkSum calculation and comparison

        term_int = int.from_bytes(term, byteorder='big')
        
        return dataType_int, length_int, data_int24, checkSum_int, term_int

    def sendDataToBuffer(self):
        pass