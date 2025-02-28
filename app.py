from daq.daq import Daq
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
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, SAMPLES_PER_PACKAGE

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__filteredDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__recordBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

    def initializeThreads(self):
        # self.__daq = Daq()
        # self.__daq.assignBuffer(self.__rawDataBuffer)
        # self.__daq.assignRecordBuffer(self.__recordBuffer)

        self.__filter = Filter()
        self.__filter.assignInletBuffer(self.__rawDataBuffer)
        self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

        self.__uiFilter = UiDataProc(self.__filter)
        self.__uiFilter.assignFilter(self.__filter)

        self.__mockRawData = MockRawData()
        self.__mockRawData.assignBuffer(self.__rawDataBuffer)
        self.__mockRawData.assignRecordBuffer(self.__recordBuffer)

        self.__uiRawPlot = UiRawPlot()
        self.__uiRawPlot.assignBuffer(self.__rawDataBuffer)

        self.__uiFilteredPlot = UiFilteredPlot()
        self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

        ## Choose Recording format
        # .h5 format
        # self.__record = Record()
        # self.__record.assignBuffer(self.__recordBuffer)

        # .mat format
        self.__record = RecordMat()
        self.__record.assignBuffer(self.__recordBuffer)
        
        self.__uiRecord = UiRecord(self.__record)
        self.__uiRecord.assignRecord(self.__record)

    def renderApp(self):
        #self.__daq.startThread()
        self.__uiRecord.render()
        self.__filter.startThread()
        self.__uiFilter.render()
        self.__uiFilter.startThread()
        self.__mockRawData.startThread()
        self.__uiRawPlot.render()
        self.__uiRawPlot.startThread()
        self.__uiFilteredPlot.render()
        self.__uiFilteredPlot.startThread()
        self.__record.startThread()

    def stopApp(self):
        self.__uiFilteredPlot.stopThread()
        self.__uiRawPlot.stopThread()
        self.__mockRawData.stopThread()
        self.__uiFilter.stopThread()
        self.__filter.stopThread()
        self.__uiRecord.stopThread()
        #self.__daq.stopThread()
        self.__record.stopThread()
        #self.__daq.close()
        self.__record.close()