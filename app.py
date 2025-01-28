from daq.daq import Daq
from daq.converter import Converter
from preprocess.filter import Filter
from ui.ui_rawplot import UiRawPlot
from record.record import Record
from util.abstractthread import abstractthread
from util.buffer import Buffer
from ui.mockRawData import MockRawData
from ui.ui_dataProc import UiDataProc
from util.config import CHANNELS_NUMBER, UNCONVERTED_RAW_DATA_BUFFER_SIZE, CONVERTED_RAW_DATA_BUFFER_SIZE

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__unconvertedRawDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=UNCONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__convertedRawDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

    def initializeThreads(self):
        self.__daq = Daq()
        self.__daq.assignBuffer(self.__unconvertedRawDataBuffer)

        self.__converter = Converter()
        self.__converter.assignInletBuffer(self.__unconvertedRawDataBuffer)
        self.__converter.assignOutletBuffer(self.__convertedRawDataBuffer)

        self.__filter = Filter()
        self.__filter.assignInletBuffer(self.__convertedRawDataBuffer)

        self.__UiFilter = UiDataProc(self.__filter)
        self.__UiFilter.assignFilter(self.__filter)

        self.__mockRawData = MockRawData()
        self.__mockRawData.assignBuffer(self.__unconvertedRawDataBuffer)

        self.__uiRawPlot = UiRawPlot()
        self.__uiRawPlot.assignBuffer(self.__convertedRawDataBuffer)

    def renderApp(self):
        self.__daq.startThread()
        self.__converter.startThread()
        self.__filter.startThread()

        self.__UiFilter.render()
        self.__UiFilter.startThread()

        #self.__mockRawData.startThread()

        self.__uiRawPlot.render()
        self.__uiRawPlot.startThread()

    def stopApp(self):
        self.__uiRawPlot.stopThread()
        self.__mockRawData.stopThread()
        self.__UiFilter.stopThread()
        self.__filter.stopThread()
        self.__converter.stopThread()
        self.__daq.stopThread()