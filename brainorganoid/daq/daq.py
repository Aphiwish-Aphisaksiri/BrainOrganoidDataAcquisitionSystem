import serial
import numpy as np
import time
import threading
import h5py
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import (CHANNELS_NUMBER, BITS_PER_SAMPLE, HEADER_LEN, TERM_LEN, SAMPLES_PER_PACKAGE, 
                                       VREF, GAIN, HEADER_VALUE, TERMINATOR_VALUE, COM_PORT, BAUDRATE, UNIT_MULTIPLIER, 
                                       CHANNELS_PER_PORT, DOWN_SAMPLING_FACTOR)

class Daq(abstractthread):
    def __init__(self, daqIndex):
        super().__init__()
        self.__channelsNumber = CHANNELS_PER_PORT
        self.__bitsPerSample = BITS_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__samplesPerPackage = SAMPLES_PER_PACKAGE
        self.__payloadLen = -(-self.__channelsNumber * self.__bitsPerSample * self.__samplesPerPackage // 8) # Weird -(-) is used to ceil the division
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.__port = COM_PORT[daqIndex]
        self.__baudrate = BAUDRATE
        self.__reconnect_interval = 5  # seconds
        self.__ser = None
        self.__rawData = bytearray()
        self.__startTime = time.time()
        self.__samplesCount = 0
        self.__samplesCountPerSecond = 0
        self.__unitMultiplier = UNIT_MULTIPLIER
        self.__daqIndex = daqIndex
        self.__downSamplingFactor = DOWN_SAMPLING_FACTOR

        self.__connect_thread = threading.Thread(target=self.connect)
        self.__connect_thread.daemon = True
        self.__connect_thread.start()

        self.__recordBuffer = None

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
                    if self.__rawData[0] != HEADER_VALUE:
                        self.__rawData = self.__rawData[1:]
                        continue
                    package = self.__rawData[:self.__packageLen]
                    self.__rawData = self.__rawData[self.__packageLen:]

                    header = package[0]
                    term = package[-1]

                    if header == HEADER_VALUE and term == TERMINATOR_VALUE and len(package) == self.__packageLen:
                        packages.append(package)
                        self.__samplesCount += self.__samplesPerPackage
                    else:
                        print(f"Invalid package: header={header}, term={term}, length={len(package)}")

                currentTime = time.time()
                if currentTime - self.__startTime >= 1:
                    print(f"{COM_PORT[self.__daqIndex]}-Samples received in the last second: {self.__samplesCount}")
                    self.__samplesCountPerSecond = self.__samplesCount
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
        multiplier = ((2 * (VREF / GAIN)) / (2 ** self.__bitsPerSample))*self.__unitMultiplier  # Adjust for the configured bit resolution
        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator
    
        header_int = header  # header is already an integer
    
        # Convert byte array to bit array with big-endian format
        bit_array = np.unpackbits(np.frombuffer(data, dtype='>u1'))
    
        # Extract samples based on the configured bits per sample
        num_samples = len(bit_array) // self.__bitsPerSample
        data_int = np.array([int(''.join(map(str, bit_array[i*self.__bitsPerSample:(i+1)*self.__bitsPerSample])), 2) for i in range(num_samples)])
    
        # Convert to signed integer based on the configured bits per sample
        data_int = np.where(data_int >= 2**(self.__bitsPerSample - 1), data_int - 2**self.__bitsPerSample, data_int)
    
        # Convert to voltage
        data_voltage = data_int * multiplier
    
        # Reshape the data to maintain the structure of channels and samples
        data_voltage = data_voltage.reshape(num_samples // self.__channelsNumber, self.__channelsNumber)

        data_voltage = data_voltage.T
    
        return header_int, data_voltage, term
    
    def setUnitMultiplier(self, unitMultiplier=1_000):
        self.__unitMultiplier = unitMultiplier
        if self.__unitMultiplier == 1_000:
            return "mV"
        elif self.__unitMultiplier == 1_000_000:
            return "uV"
        else:
            return "Invalid unit multiplier"

    def sendDataToBuffer(self):
        packages = self.readData()
        if packages is None:
            return
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            downSampledData = data[:, ::self.__downSamplingFactor]
            self.__rawDataBuffer.addMultipleData(downSampledData)
            # self.sendDataToRecordBuffer(data)

    def sendDataToRecordBuffer(self, data):
        self.__recordBuffer.addMultipleData(data)
        # print(data)

    def update(self):
        self.sendDataToBuffer()

    def getSamplesCount(self):
        return self.__samplesCountPerSecond

    def assignBuffer(self, target):
        self.__rawDataBuffer = target

    def assignRecordBuffer(self, target):
        self.__recordBuffer = target

    def close(self):
        if self.__ser:
            self.__ser.close()