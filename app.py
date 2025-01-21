from daq.daq import Daq
from preprocess.filter import Filter
from ui.ui_rawplot import UiRawPlot
from record.record import Record
from util.abstractthread import abstractthread
from util.buffer import Buffer
from ui.mockRawData import MockRawData
from ui.ui_dataProc import UiDataProc

class App():
    def __init__(self):
        # Variables
        self.__channelsNumber = 8
        self.__rawDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=800)

    def initializeThreads(self):
        self.__daq = Daq()
        self.__daq.assignBuffer(self.__rawDataBuffer)

        self.__filter = Filter()
        self.__filter.assignBuffer(self.__rawDataBuffer)

        self.__UiFilter = UiDataProc(self.__filter)
        self.__UiFilter.assignFilter(self.__filter)

        self.__mockRawData = MockRawData()
        self.__mockRawData.assignBuffer(self.__rawDataBuffer)

        self.__uiRawPlot = UiRawPlot()
        self.__uiRawPlot.assignBuffer(self.__rawDataBuffer)


    def renderApp(self):
        #self.__daq.startThread()

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
        self.__daq.stopThread()