from brainorganoid.util.abstractprocess import AbstractProcess
from brainorganoid.util.config import (
    CHANNELS_PER_PORT, BITS_PER_SAMPLE, HEADER_LEN, TERM_LEN, SAMPLES_PER_PACKAGE,
    VREF, GAIN, HEADER_VALUE, TERMINATOR_VALUE, COM_PORT, BAUDRATE, UNIT_MULTIPLIER
)
import serial
import numpy as np
import logging
import time
from multiprocessing import Lock

class DaqProcess(AbstractProcess):
    def __init__(self, daqIndex):
        super().__init__()
        self.__daqIndex = daqIndex
        self.__rawDataBuffer = None  # This will be a multiprocessing.Array
        self.__bufferLock = Lock()  # Lock for thread-safe access to the shared buffer
        self.__channelsNumber = CHANNELS_PER_PORT
        self.__bitsPerSample = BITS_PER_SAMPLE
        self.__headerLen = HEADER_LEN
        self.__termLen = TERM_LEN
        self.__samplesPerPackage = SAMPLES_PER_PACKAGE
        self.__payloadLen = -(-self.__channelsNumber * self.__bitsPerSample * self.__samplesPerPackage // 8)  # Ceil division
        self.__packageLen = self.__headerLen + self.__payloadLen + self.__termLen
        self.__port = COM_PORT[daqIndex]
        self.__baudrate = BAUDRATE
        self.__unitMultiplier = UNIT_MULTIPLIER
        self.__ser = None
        self.__rawData = bytearray()
        self.__startTime = time.time()
        self.__samplesCount = 0
        self.__samplesCountPerSecond = 0
        self.__reconnect_interval = 5  # seconds
        logging.info(f"DaqProcess {daqIndex} initialized.")

    def connect(self):
        """Establish a connection to the serial port."""
        while self.__ser is None:
            if self._stopEvent.is_set():  # Check if the stop signal is set
                logging.info(f"Stopping reconnect attempts for {self.__port}")
                return
            try:
                self.__ser = serial.Serial(
                    self.__port,
                    self.__baudrate,
                    timeout=1,
                    rtscts=True,
                    dsrdtr=True
                )
                self.__ser.reset_input_buffer()  # Clear the input buffer
                logging.info(f"Connected to {self.__port}")
            except serial.SerialException as e:
                logging.error(f"Failed to connect to {self.__port}: {e}")
                time.sleep(self.__reconnect_interval)

    def readData(self):
        """Read data from the serial port."""
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
                        logging.warning(f"Invalid package: Port={COM_PORT[self.__daqIndex]}, header={header}, term={term}, length={len(package)}")

                currentTime = time.time()
                if currentTime - self.__startTime >= 1:
                    self.__samplesReceivedPerSecondBuffer[0] = self.__samplesCount
                    logging.info(f"{self.__port}-Samples received in the last second: {self.__samplesCount}")
                    self.__samplesCountPerSecond = self.__samplesCount
                    self.__samplesCount = 0
                    self.__startTime = currentTime

                return packages
        except serial.SerialException as e:
            logging.error(f"Serial error: {e}")
            if self.__ser:
                self.__ser.close()
                self.__ser = None
            self.connect()
            return []

    def convertByteArrayToData(self, byteArray):
        """Convert raw byte array to structured data."""
        multiplier = ((2 * (VREF / GAIN)) / (2 ** self.__bitsPerSample)) * self.__unitMultiplier
        header = byteArray[0]
        data = byteArray[1:-1]
        term = byteArray[-1]

        # Convert byte array to bit array
        bit_array = np.unpackbits(np.frombuffer(data, dtype='>u1'))

        # Extract samples based on the configured bits per sample
        num_samples = len(bit_array) // self.__bitsPerSample
        data_int = np.array([
            int(''.join(map(str, bit_array[i * self.__bitsPerSample:(i + 1) * self.__bitsPerSample])), 2)
            for i in range(num_samples)
        ])

        # Convert to signed integer
        data_int = np.where(data_int >= 2 ** (self.__bitsPerSample - 1), data_int - 2 ** self.__bitsPerSample, data_int)

        # Convert to voltage
        data_voltage = data_int * multiplier

        # Reshape the data to maintain the structure of channels and samples
        data_voltage = data_voltage.reshape(num_samples // self.__channelsNumber, self.__channelsNumber).T

        return header, data_voltage, term

    def sendDataToBuffer(self):
        """Read, process, and send data to the buffers."""
        packages = self.readData()
        if packages is None:
            return
        for package in packages:
            header, data, term = self.convertByteArrayToData(package)
            with self.__bufferLock:  # Ensure thread-safe access to the shared buffers
                for channel_index, channel_data in enumerate(data):
                    # Access the shared buffer for the current channel
                    buffer = np.frombuffer(self.__rawDataBuffers[channel_index].get_obj())
                    
                    # Shift the existing data to the left to make room for new data
                    num_new_samples = len(channel_data)
                    buffer_size = len(buffer)
                    if num_new_samples > buffer_size:
                        raise ValueError(f"New data size ({num_new_samples}) exceeds buffer size ({buffer_size}).")
                    
                    # Shift the buffer to the left and add new data to the end
                    buffer[:-num_new_samples] = buffer[num_new_samples:]
                    buffer[-num_new_samples:] = channel_data
    
                    # Also send the data to the record buffer
                    record_buffer = np.frombuffer(self.__recordBuffer.get_obj())
                    record_buffer[:-num_new_samples] = record_buffer[num_new_samples:]
                    record_buffer[-num_new_samples:] = channel_data

    def assignRawDataBuffers(self, buffers):
        """Assign a multiprocessing.Array as the buffer."""
        self.__rawDataBuffers = buffers

    def assignRecordBuffer(self, buffer):
        """Assign a multiprocessing.Array to store the recorded data."""
        self.__recordBuffer = buffer

    def assignSamplesReceivedPerSecondBuffer(self, buffer):
        """Assign a multiprocessing.Array to store the samples received per second."""
        self.__samplesReceivedPerSecondBuffer = buffer

    def getSamplesCount(self):
        return self.__samplesCountPerSecond

    def update(self):
        """Override the update method to handle data acquisition."""
        if self._stopEvent.is_set():  # Check if the stop signal is set
            logging.info(f"Stopping data acquisition for {self.__port}")
            return
        if self.__ser is None:
            self.connect()
        self.sendDataToBuffer()

    def close(self):
        """Close the serial connection."""
        if self.__ser:
            self.__ser.close()