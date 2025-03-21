from daq.daq import Daq
from daq.mockdaq import MockDaq
from daq.datasynchronize import DataSynchronize
from preprocess.filter import Filter
from ui.ui_rawplot import UiRawPlot
from record.record import Record
from record.recordmat import RecordMat
from util.abstractthread import abstractthread
from util.buffer import Buffer
from ui.mockRawData import MockRawData
from ui.ui_dataProc import UiDataProc
from ui.ui_filteredplot import UiFilteredPlot
from ui.ui_record import UiRecord
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, USE_MOCK_DATA, RECORD_FORMAT, MOCK_TYPE, COM_PORT, CHANNEL_ASSIGNMENT

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBufferInstances = []
        for port in COM_PORT:
            rawDataBuffer = Buffer(numChannel=len(CHANNEL_ASSIGNMENT[port]), numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
            self.__rawDataBufferInstances.append(rawDataBuffer)
        self.__synchronizedDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__filteredDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__recordBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

        self.configChecker()

    def initializeThreads(self):
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

        self.__filter = Filter()
        self.__filter.assignInletBuffer(self.__synchronizedDataBuffer)
        self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

        self.__uiFilter = UiDataProc(self.__filter)
        self.__uiFilter.assignFilter(self.__filter)

        self.__uiRawPlot = UiRawPlot(self.__daqInstances[0])
        self.__uiRawPlot.assignBuffer(self.__synchronizedDataBuffer)

        self.__uiFilteredPlot = UiFilteredPlot()
        self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

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

    def renderApp(self):
        for daqIndex in range(len(COM_PORT)):
            self.__daqInstances[daqIndex].startThread()
        self.__dataSynchronize.startThread()
        self.__uiRecord.render()
        self.__filter.startThread()
        self.__uiFilter.render()
        self.__uiFilter.startThread()
        self.__uiRawPlot.render()
        self.__uiRawPlot.startThread()
        self.__uiFilteredPlot.render()
        self.__uiFilteredPlot.startThread()
        self.__record.startThread()

    def stopApp(self):
        self.__uiFilteredPlot.stopThread()
        self.__uiRawPlot.stopThread()
        self.__uiFilter.stopThread()
        self.__filter.stopThread()
        self.__uiRecord.stopThread()
        self.__record.stopThread()
        self.__record.close()
        self.__dataSynchronize.stopThread()
        for daqIndex in range(len(COM_PORT)):
            self.__daqInstances[daqIndex].stopThread()
            self.__daqInstances[daqIndex].close()

    def configChecker(self):
        if RECORD_FORMAT not in ["mat", "h5"]:
            print("Invalid RECORD_FORMAT in config.py")
            exit()
        if MOCK_TYPE not in ["SineWave", "TriangleWave", "ChannelNumber"]:
            print("Invalid MOCK_TYPE in config.py")
            exit()
        if len(COM_PORT) != len(CHANNEL_ASSIGNMENT):
            print("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
            exit()
        for port in COM_PORT:
            if port not in CHANNEL_ASSIGNMENT:
                print("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
                exit()
            if len(CHANNEL_ASSIGNMENT[port])*len(CHANNEL_ASSIGNMENT) != CHANNELS_NUMBER:
                print("CHANNEL_ASSIGNMENT in config.py does not match CHANNELS_NUMBER")
                exit()