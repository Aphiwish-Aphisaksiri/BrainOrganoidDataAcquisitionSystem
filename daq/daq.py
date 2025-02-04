import serial
import numpy as np
import time
import threading
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, BYTES_PER_SAMPLE, HEADER_LEN, TERM_LEN, SAMPLES_PER_PACKAGE, VREF, GAIN

class Daq(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__bytesPerSample = BYTES_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__samplesPerPackage = SAMPLES_PER_PACKAGE
        self.__payloadLen = self.__channelsNumber * self.__bytesPerSample * self.__samplesPerPackage
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.__port = 'COM5'
        self.__baudrate = 1250000
        self.__reconnect_interval = 5  # seconds
        self.__ser = None
        self.__rawData = bytearray()
        self.__startTime = time.time()
        self.__samplesCount = 0

        self.__connect_thread = threading.Thread(target=self.connect)
        self.__connect_thread.daemon = True
        self.__connect_thread.start()

    def connect(self):
        while self.__ser is None:
            try:
                self.__ser = serial.Serial(
                    self.__port,
                    self.__baudrate,
                    timeout=1,
                    rtscts=True,
                    dsrdtr=True
                )
                self.__ser.reset_input_buffer()  # Clear the input buffer
                print(f"Connected to {self.__port}")
            except serial.SerialException as e:
                print(f"Failed to connect to {self.__port}: {e}")
                time.sleep(self.__reconnect_interval)

    def readData(self):
        try:
            if self.__ser is not None:
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
                        self.__samplesCount += self.__samplesPerPackage
                    else:
                        print(f"Invalid package: header={header}, term={term}, length={len(package)}")

                currentTime = time.time()
                if currentTime - self.__startTime >= 1:
                    print(f"Samples received in the last second: {self.__samplesCount}")
                    self.__samplesCount = 0
                    self.__startTime = currentTime

                return packages
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.__ser.close()
            self.__ser = None
            self.connect()
            return []

    def convertByteArrayToData(self, byteArray):
        multiplier = (2 * (VREF / GAIN)) / (2 ** 24)

        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator

        header_int = header  # header is already an integer

        # Unpack the data using bitwise operations
        data_int24 = np.array([(data[i] << 16) | (data[i+1] << 8) | data[i+2] for i in range(0, len(data), 3)])

        # Convert to signed 24-bit integer
        data_int24 = np.where(data_int24 >= 2**23, data_int24 - 2**24, data_int24)

        # Convert to voltage
        data_voltage = data_int24 * multiplier

        # Reshape the data to maintain the structure of channels and samples
        data_voltage = data_voltage.reshape(self.__channelsNumber, self.__samplesPerPackage)

        return header_int, data_voltage, term

    def sendDataToBuffer(self):
        packages = self.readData()
        if packages is None:
            return
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            self.__rawDataBuffer.addMultipleData(data)

    def update(self):
        self.sendDataToBuffer()

    def assignBuffer(self, target):
        self.__rawDataBuffer = target