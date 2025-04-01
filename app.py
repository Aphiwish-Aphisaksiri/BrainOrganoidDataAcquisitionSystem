import logging
from brainorganoid.daq.daq import Daq
from brainorganoid.daq.mockdaq import MockDaq
from brainorganoid.daq.datasynchronize import DataSynchronize
from brainorganoid.preprocess.filter import Filter
from brainorganoid.ui.ui_rawplot import UiRawPlot
from brainorganoid.record.record import Record
from brainorganoid.record.recordmat import RecordMat
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.buffer import Buffer
from brainorganoid.util.circularbuffer import CircularBuffer
from brainorganoid.ui.mockRawData import MockRawData
from brainorganoid.ui.ui_dataProc import UiDataProc
from brainorganoid.ui.ui_filteredplot import UiFilteredPlot
from brainorganoid.ui.ui_record import UiRecord
from brainorganoid.ui.ui_settings import UiSettings
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, USE_MOCK_DATA, RECORD_FORMAT, MOCK_TYPE, COM_PORT, CHANNEL_ASSIGNMENT

class App():
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Initializing application...")
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBufferInstances = []
        for port in COM_PORT:
            rawDataBuffer = CircularBuffer(numChannel=len(CHANNEL_ASSIGNMENT[port]), numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
            self.__rawDataBufferInstances.append(rawDataBuffer)
        self.__synchronizedDataBuffer = CircularBuffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        # self.__filteredDataBuffer = CircularBuffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__recordBuffer = CircularBuffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

        self.configChecker()

    def initializeThreads(self):
        try:
            if USE_MOCK_DATA:
                self.__daq = MockDaq(MOCK_TYPE)
                # self.__daq = MockRawData()
                self.__daq.assignBuffer(self.__synchronizedDataBuffer)
                self.__daq.assignRecordBuffer(self.__recordBuffer)
            else:
                self.__daqInstances = []
                for daqIndex in range(len(COM_PORT)):
                    daq = Daq(daqIndex)
                    daq.assignBuffer(self.__rawDataBufferInstances[daqIndex])
                    self.__daqInstances.append(daq)

            self.__dataSynchronize = DataSynchronize()
            self.__dataSynchronize.assignRawDataBufferInstances(self.__rawDataBufferInstances)
            self.__dataSynchronize.assignSynchronizedDataBuffer(self.__synchronizedDataBuffer)

            # self.__filter = Filter()
            # self.__filter.assignInletBuffer(self.__synchronizedDataBuffer)
            # self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

            # self.__uiFilter = UiDataProc(self.__filter)
            # self.__uiFilter.assignFilter(self.__filter)

            self.__uiRawPlot = UiRawPlot(self.__daqInstances[0] if not USE_MOCK_DATA else self.__daq)
            self.__uiRawPlot.assignBuffer(self.__synchronizedDataBuffer)

            # self.__uiFilteredPlot = UiFilteredPlot()
            # self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

            self.__record = self.initializeRecord()
            self.__uiRecord = UiRecord(self.__record)
            self.__uiRecord.assignRecord(self.__record)

            self.__uiSettings = UiSettings(self)
        except Exception as e:
            logging.error(f"Error initializing threads: {e}")
            raise

    def initializeRecord(self):
        if RECORD_FORMAT == "mat":
            record = RecordMat()
        elif RECORD_FORMAT == "h5":
            record = Record()
        else:
            logging.error("Invalid RECORD_FORMAT in config.py")
            exit()
        record.assignBuffer(self.__recordBuffer)
        return record

    def renderApp(self):
        try:
            for daqIndex in range(len(COM_PORT)):
                self.__daqInstances[daqIndex].startThread()
            self.__dataSynchronize.startThread()
            self.__uiRecord.render()
            # self.__filter.startThread()
            # self.__uiFilter.render()
            # self.__uiFilter.startThread()
            self.__uiRawPlot.render()
            self.__uiRawPlot.startThread()
            # self.__uiFilteredPlot.render()
            # self.__uiFilteredPlot.startThread()
            self.__record.startThread()
            self.__uiSettings.render()
        except Exception as e:
            logging.error(f"Error rendering application: {e}")
            self.stopApp()
            raise

    def stopApp(self):
        try:
            # self.__uiFilteredPlot.stopThread()
            self.__uiRawPlot.stopThread()
            # self.__uiFilter.stopThread()
            # self.__filter.stopThread()
            self.__uiRecord.stopThread()
            self.__record.stopThread()
            self.__record.close()
            self.__dataSynchronize.stopThread()
            for daqIndex in range(len(COM_PORT)):
                self.__daqInstances[daqIndex].stopThread()
                self.__daqInstances[daqIndex].close()
            self.__uiSettings.stopThread()
        except Exception as e:
            logging.error(f"Error stopping application: {e}")

    def configChecker(self):
        try:
            if RECORD_FORMAT not in ["mat", "h5"]:
                raise ValueError("Invalid RECORD_FORMAT in config.py")
            if MOCK_TYPE not in ["SineWave", "TriangleWave", "ChannelNumber"]:
                raise ValueError("Invalid MOCK_TYPE in config.py")
            if len(COM_PORT) != len(CHANNEL_ASSIGNMENT):
                raise ValueError("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
            for port in COM_PORT:
                if port not in CHANNEL_ASSIGNMENT:
                    raise ValueError("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
                if len(CHANNEL_ASSIGNMENT[port]) * len(CHANNEL_ASSIGNMENT) != CHANNELS_NUMBER:
                    raise ValueError("CHANNEL_ASSIGNMENT in config.py does not match CHANNELS_NUMBER")
        except ValueError as e:
            logging.error(e)
            exit()