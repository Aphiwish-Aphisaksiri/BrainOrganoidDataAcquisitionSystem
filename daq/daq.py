import serial
import time
import numpy as np
from util.abstractthread import abstractthread
from util.buffer import Buffer
from util.config import CHANNELS_NUMBER, BYTES_PER_SAMPLE, HEADER_LEN, TERM_LEN, UNCONVERTED_RAW_DATA_BUFFER_SIZE

class Daq(abstractthread):
    def __init__(self):
        super().__init__()
        self.__channelsNumber = CHANNELS_NUMBER
        self.__bytesPerSample = BYTES_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
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

    def readData(self):
        try:
            if self.__ser.in_waiting > 0:
                self.__rawData += self.__ser.read(self.__ser.in_waiting)

            # Convert rawData to a numpy array and pad with zeros to length UNCONVERTED_RAW_DATA_BUFFER_SIZE
            rawDataArray = np.frombuffer(self.__rawData, dtype=np.uint8)
            if len(rawDataArray) < UNCONVERTED_RAW_DATA_BUFFER_SIZE:
                rawDataArray = np.pad(rawDataArray, (0, UNCONVERTED_RAW_DATA_BUFFER_SIZE - len(rawDataArray)), 'constant')

            # Reshape to match the buffer shape
            rawDataArray = rawDataArray.reshape((self.__channelsNumber, -1))

            currentTime = time.time()
            if currentTime - self.__startTime >= 1:
                print(f"Packages received in the last second: {self.__packageCount}")
                self.__packageCount = 0
                self.__startTime = currentTime

            return rawDataArray
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.__ser.close()
            self.__ser = None
            self.connect()
            return np.zeros((self.__channelsNumber, UNCONVERTED_RAW_DATA_BUFFER_SIZE), dtype=np.uint8)

    def sendDataToBuffer(self):
        rawDataArray = self.readData()
        self.__unconvertedRawDataBuffer.addBatchData(rawDataArray)

    def update(self):
        self.sendDataToBuffer()

    def assignBuffer(self, target):
        self.__unconvertedRawDataBuffer = target