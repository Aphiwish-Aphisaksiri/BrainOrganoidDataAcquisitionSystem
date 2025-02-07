from daq.daq import Daq
from preprocess.filter import Filter
from ui.ui_rawplot import UiRawPlot
from record.record import Record
from util.abstractthread import abstractthread
from util.buffer import Buffer
from ui.mockRawData import MockRawData
from ui.ui_dataProc import UiDataProc
from ui.ui_filteredplot import UiFilteredPlot
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__filteredDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

    def initializeThreads(self):
        self.__daq = Daq()
        self.__daq.assignBuffer(self.__rawDataBuffer)

        self.__filter = Filter()
        self.__filter.assignInletBuffer(self.__rawDataBuffer)
        self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

        self.__uiFilter = UiDataProc(self.__filter)
        self.__uiFilter.assignFilter(self.__filter)

        self.__mockRawData = MockRawData()
        self.__mockRawData.assignBuffer(self.__rawDataBuffer)

        self.__uiRawPlot = UiRawPlot()
        self.__uiRawPlot.assignBuffer(self.__rawDataBuffer)

        self.__uiFilteredPlot = UiFilteredPlot()
        self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

    def renderApp(self):
        self.__daq.startThread()
        self.__filter.startThread()
        self.__uiFilter.render()
        self.__uiFilter.startThread()
        #self.__mockRawData.startThread()
        self.__uiRawPlot.render()
        self.__uiRawPlot.startThread()
        self.__uiFilteredPlot.render()
        self.__uiFilteredPlot.startThread()

    def stopApp(self):
        self.__uiFilteredPlot.stopThread()
        self.__uiRawPlot.stopThread()
        self.__mockRawData.stopThread()
        self.__uiFilter.stopThread()
        self.__filter.stopThread()
        self.__daq.stopThread()