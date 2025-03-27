from brainorganoid.daq.daq import Daq
from brainorganoid.daq.mockdaq import MockDaq
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
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, USE_MOCK_DATA, RECORD_FORMAT, MOCK_TYPE, RECORD_BUFFER_SIZE

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffer = CircularBuffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        # self.__filteredDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__recordBuffer = CircularBuffer(numChannel=self.__channelsNumber, numSample=RECORD_BUFFER_SIZE)

    def initializeThreads(self):
        if USE_MOCK_DATA:
            self.__daq = MockDaq(MOCK_TYPE)
            # self.__daq = MockRawData()
            self.__daq.assignBuffer(self.__rawDataBuffer)
            self.__daq.assignRecordBuffer(self.__recordBuffer)
        else:
            self.__daq = Daq()
            self.__daq.assignBuffer(self.__rawDataBuffer)
            self.__daq.assignRecordBuffer(self.__recordBuffer)

        # self.__filter = Filter()
        # self.__filter.assignInletBuffer(self.__rawDataBuffer)
        # self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

        # self.__uiFilter = UiDataProc(self.__filter)
        # self.__uiFilter.assignFilter(self.__filter)

        self.__uiRawPlot = UiRawPlot(self.__daq)
        self.__uiRawPlot.assignBuffer(self.__rawDataBuffer)

        # self.__uiFilteredPlot = UiFilteredPlot()
        # self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

        if RECORD_FORMAT == "mat":
            self.__record = RecordMat()
            self.__record.assignBuffer(self.__recordBuffer)
        elif RECORD_FORMAT == "h5":
            self.__record = Record()
            self.__record.assignBuffer(self.__recordBuffer)
        else:
            print("Invalid RECORD_FORMAT in config.py")
            exit()
        
        self.__uiRecord = UiRecord(self.__record)
        self.__uiRecord.assignRecord(self.__record)

        self.__uiSettings = UiSettings(self)

    def renderApp(self):
        self.__daq.startThread()
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

    def stopApp(self):
        # self.__uiFilteredPlot.stopThread()
        self.__uiRawPlot.stopThread()
        # self.__uiFilter.stopThread()
        # self.__filter.stopThread()
        self.__uiRecord.stopThread()
        self.__record.stopThread()
        self.__record.close()
        self.__daq.close()
        self.__daq.stopThread()
