import serial
import numpy as np
import time
import struct
from util.abstractthread import abstractthread

class Daq(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = 8
        self.__bytesPerSample = 3  # 24 bits
        self.__headerLen = 1
        self.__termLen = 1
        self.__payloadLen = self.__channelsNumber * self.__bytesPerSample
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.__port = 'COM4'
        self.__baudrate = 1460000
        self.__reconnect_interval = 5  # seconds
        self.__ser = None
        self.__rawData = bytearray()
        self.__startTime = time.time()
        self.__packageCount = 0

        self.setThreadFrequency(16)

        # FOR DEBUGGING
        self.__prev_byte_count = 0

        self.connect()

    def connect(self):
        while self.__ser is None:
            try:
                self.__ser = serial.Serial(
                    self.__port,
                    self.__baudrate,
                    timeout=0,
                    rtscts=True,
                    dsrdtr=True,
                    parity="N",
                    stopbits=1,
                    bytesize=8
                )
                self.__ser.reset_input_buffer()  # Clear the input buffer
                print(f"Connected to {self.__port}")
            except serial.SerialException as e:
                print(f"Failed to connect to {self.__port}: {e}")
                time.sleep(self.__reconnect_interval)


    
    def convertByteArrayToData(self, byteArray):
        Vref = 2.4
        Gain = 12
        multiplier = (2 * (Vref / Gain)) / (2 ** 24)
    
        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator
    
        header_int = header  # header is already an integer
    
        # Unpack the data using struct
        data_int24 = np.array([struct.unpack('>i', b'\x00' + data[i:i+3])[0] for i in range(0, len(data), 3)])
    
        # Convert to signed 24-bit integer
        data_int24 = np.where(data_int24 >= 2**23, data_int24 - 2**24, data_int24)
    
        # Convert to voltage
        data_voltage = data_int24 * multiplier
    
        # Reshape the data to maintain the structure of 8 channels
        data_voltage = data_voltage.reshape(self.__channelsNumber, -1)
    
        term_int = term  # term is already an integer
    
        return header_int, data_voltage, term_int

    def readData(self):
        try:
            self.__rawData += self.__ser.read(self.__ser.in_waiting)
            packages = []
            while len(self.__rawData) >= self.__packageLen:
                if self.__rawData[0] != 0xAA:
                    self.__rawData = self.__rawData[1:]
                    continue
                package = self.__rawData[:self.__packageLen]
                self.__rawData = self.__rawData[self.__packageLen:]

                header = package[0]
                term = package[-1]

                if header == 0xAA and term == 0xFF and len(package) == self.__packageLen:
                    packages.append(package)
                    self.__packageCount += 1
                else:
                    print(f"Invalid package: header={header}, term={term}, length={len(package)}")

            currentTime = time.time()
            if currentTime - self.__startTime >= 1:
                print(f"Packages received in the last second: {self.__packageCount}")
                self.__packageCount = 0
                self.__startTime = currentTime

            return packages
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.__ser.close()
            self.__ser = None
            self.connect()
            return []

    def sendDataToBuffer(self):
        packages = self.readData()
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            data = data.reshape(self.__channelsNumber, -1)
            self.__rawDataBuffer.addMultipleData(data)

    def update(self):
        self.sendDataToBuffer()

    def assignBuffer(self, target):
        self.__rawDataBuffer = target