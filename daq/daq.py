import serial
import numpy as np
import time
from util.abstractthread import abstractthread

class Daq(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = 8
        self.__bytesPerSample = 3 # 24 bits
        self.__headerLen = 1
        self.__termLen = 1
        self.__payloadLen = self.__channelsNumber * self.__bytesPerSample
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.__ser = serial.Serial('COM10', 1843200)
        self.__rawData = bytearray()
    
    def convertByteArrayToData(self, byteArray):
        header = byteArray[0] # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]    # last byte is the terminator

        header_int = int.from_bytes(header, byteorder='big')
        data_int24 = np.frombuffer(data, dtype=np.int8).reshape(-1, 3)
        data_int24 = data_int24[:, 0] + (data_int24[:, 1] << 8) + (data_int24[:, 2] << 16)
        term_int = int.from_bytes(term, byteorder='big')
        
        return header_int, data_int24, term_int

    def readData(self):
        self.__rawData += self.__ser.read(self.__ser.in_waiting)
        packages = []
        while len(self.__rawData) >= self.__packageLen:
            package = self.__rawData[:self.__packageLen]
            self.__rawData = self.__rawData[self.__packageLen:]
            
            header = package[0]
            term = package[-1]
            
            if header == 0xAA and term == 0xFF:
                packages.append(package)
            else:
                print(f"Invalid package: header={header}, term={term}")
        
        return packages
    
    def sendDataToBuffer(self):
        packages = self.readData()
        for package in packages:
            _, data, _ = self.convertByteArrayToData(package)
            data = data.reshape(self.__channelsNumber, -1)
            self.__rawDataBuffer.addMultipleData(data)

    def update(self):
        self.count += 1
        self.sendDataToBuffer()
        if time.time() - self.starttime >= 1:
            self.starttime = time.time()
            print(self.count)
            self.count = 0
        
    def assignBuffer(self, target):
        self.__rawDataBuffer = target