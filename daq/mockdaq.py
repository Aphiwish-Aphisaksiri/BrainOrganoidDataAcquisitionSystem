import numpy as np
import time
import threading
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, BITS_PER_SAMPLE, HEADER_LEN, TERM_LEN, SAMPLES_PER_PACKAGE, VREF, GAIN, CONVERTED_RAW_DATA_BUFFER_SIZE, HEADER_VALUE, TERMINATOR_VALUE

class MockDaq(abstractthread):
    def __init__(self, mockType):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__bitsPerSample = BITS_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__samplesPerPackage = SAMPLES_PER_PACKAGE
        self.__payloadLen = -(-self.__channelsNumber * self.__bitsPerSample * self.__samplesPerPackage // 8) # Weird -(-) is used to ceil the division
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen

        self.__rawData = bytearray()
        self.__startTime = time.time()
        self.__samplesCount = 0

        self.__recordBuffer = None

        self.__mockType = mockType

        # Triangle wave parameters
        self.__triangle_wave = self.generate_triangle_wave(0, 100, 1000)
        self.__triangle_wave_index = 0

    def generate_triangle_wave(self, min_val, max_val, num_samples):
        return np.linspace(min_val, max_val, num_samples // 2).tolist() + np.linspace(max_val, min_val, num_samples // 2).tolist()

    def readData(self):
        packages = []
        for _ in range(self.__samplesPerPackage):
            if self.__mockType == "TriangleWave":
                if self.__triangle_wave_index >= len(self.__triangle_wave):
                    self.__triangle_wave_index = 0
                sample = self.__triangle_wave[self.__triangle_wave_index]
                self.__triangle_wave_index += 1

            package = bytearray([HEADER_VALUE])
            for _ in range(self.__channelsNumber):
                if self.__mockType == "TriangleWave":
                    sample_bytes = int(sample).to_bytes(self.__bitsPerSample // 8, byteorder='big', signed=True)
                    package.extend(sample_bytes)
                elif self.__mockType == "ChannelNumber":
                    sample_bytes = int(_+1).to_bytes(self.__bitsPerSample // 8, byteorder='big', signed=True)
                    package.extend(sample_bytes)
                    # package.extend(sample_bytes)

            # Testing 2 Stacking
            for _ in range(self.__channelsNumber):
                if self.__mockType == "TriangleWave":
                    sample_bytes = int(sample).to_bytes(self.__bitsPerSample // 8, byteorder='big', signed=True)
                    package.extend(sample_bytes)
                elif self.__mockType == "ChannelNumber":
                    sample_bytes = int(_+1).to_bytes(self.__bitsPerSample // 8, byteorder='big', signed=True)
                    package.extend(sample_bytes)

            package.append(TERMINATOR_VALUE)
            packages.append(package)
            print(package)

        currentTime = time.time()
        if currentTime - self.__startTime >= 1:
            print(f"Samples generated in the last second: {self.__samplesCount}")
            self.__samplesCount = 0
            self.__startTime = currentTime

        return packages

    def convertByteArrayToData(self, byteArray):
        multiplier = (2 * (VREF / GAIN)) / (2 ** self.__bitsPerSample)  # Adjust for the configured bit resolution
        multiplier = 1
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
    
    def getSamplesCount(self):
        return self.__samplesCount

    def sendDataToBuffer(self):
        packages = self.readData()
        if packages is None:
            return
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            self.__rawDataBuffer.addMultipleData(data)
            self.sendDataToRecordBuffer(data)

    def sendDataToRecordBuffer(self, data):
        self.__recordBuffer.addMultipleData(data)
        # print(data)

    def update(self):
        self.sendDataToBuffer()

    def assignBuffer(self, target):
        self.__rawDataBuffer = target

    def assignRecordBuffer(self, target):
        self.__recordBuffer = target

    def close(self):
        pass