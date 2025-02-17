import serial
import numpy as np
import time
import threading
import h5py
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, BITS_PER_SAMPLE, HEADER_LEN, TERM_LEN, SAMPLES_PER_PACKAGE, VREF, GAIN, CONVERTED_RAW_DATA_BUFFER_SIZE

class Daq(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__bitsPerSample = BITS_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__samplesPerPackage = SAMPLES_PER_PACKAGE
        self.__payloadLen = -(-self.__channelsNumber * self.__bitsPerSample * self.__samplesPerPackage // 8) # Weird -(-) is used to ceil the division
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

        self.__recording = False
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
        multiplier = (2 * (VREF / GAIN)) / (2 ** self.__bitsPerSample)  # Adjust for the configured bit resolution
    
        header = byteArray[0]  # first byte is the data type
        data = byteArray[1:-1]  # the data is from the second byte to the second last byte
        term = byteArray[-1]  # last byte is the terminator
    
        header_int = header  # header is already an integer
    
        # Convert byte array to bit array
        bit_array = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    
        # Extract samples based on the configured bits per sample
        num_samples = len(bit_array) // self.__bitsPerSample
        data_int = np.array([int(''.join(map(str, bit_array[i*self.__bitsPerSample:(i+1)*self.__bitsPerSample])), 2) for i in range(num_samples)])
    
        # Convert to signed integer based on the configured bits per sample
        data_int = np.where(data_int >= 2**(self.__bitsPerSample - 1), data_int - 2**self.__bitsPerSample, data_int)
    
        # Convert to voltage
        data_voltage = data_int * multiplier
    
        # Reshape the data to maintain the structure of channels and samples
        data_voltage = data_voltage.reshape(self.__channelsNumber, num_samples // self.__channelsNumber)
    
        return header_int, data_voltage, term

    def sendDataToBuffer(self):
        packages = self.readData()
        if packages is None:
            return
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            self.__rawDataBuffer.addMultipleData(data)
            if self.__recording:
                self.sendDataToRecordBuffer(data, [99,199])

    def sendDataToRecordBuffer(self, data, term):
        buffer_size = CONVERTED_RAW_DATA_BUFFER_SIZE
        record_data = np.zeros((self.__channelsNumber, buffer_size))
        record_data[:, :data.shape[1]] = data
        record_data[:, data.shape[1]:data.shape[1]+2] = term  # Add terminators
        self.__recordBuffer.addMultipleData(record_data)

    def startRecording(self):
        self.__recording = True
        print("Recording started")

    def stopRecording(self):
        self.__recording = False
        print("Recording stopped")

    def update(self):
        self.sendDataToBuffer()

    def assignBuffer(self, target):
        self.__rawDataBuffer = target

    def assignRecordBuffer(self, target):
        self.__recordBuffer = target

    def close(self):
        self.stopRecording()
        if self.__ser:
            self.__ser.close()