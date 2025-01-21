'''
TODO:
[X] implement plot 8 channels Volt vs Time
[X] implement filter range input (default 0.5-2000 Hz)
[X] implement input for gain
'''
import matplotlib.pyplot as plt
import time
import numpy as np
import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread

NUM_SAMPLE_TO_SHOW = 1000

class UiRawPlot(abstractthread):
    def __init__(self):
        super().__init__()
        self.setThreadFrequency(30)
        self.__channelsNumber = 8

        self.__x = list(range(0, NUM_SAMPLE_TO_SHOW)) # 80000 samples = 10 seconds
        self.__buffer = np.zeros((self.__channelsNumber, NUM_SAMPLE_TO_SHOW))

        self.count = 0
        self.starttime = time.time()

    def render(self):
        self.__uiWindowHandler = dpg.add_window(label="Signal Viewer", width=800, height=600)
        self.__uiSubplotHandler = dpg.add_subplots(rows=self.__channelsNumber, columns=1, width=-1, height=-1, no_title=True, parent=self.__uiWindowHandler)
        self.__uiLineSeriesHandlerList = []    
        for i in range(self.__channelsNumber):
            with dpg.plot(no_title=True, parent=self.__uiSubplotHandler):
                dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                with dpg.plot_axis(dpg.mvYAxis, label=f"CH{i+1}", no_tick_labels=True, tag=f"CH{i+1}"):
                    self.__uiLineSeriesHandlerList.append(dpg.add_line_series(self.__x, self.__buffer[i], label=f"Channel {i+1}"))

    
    def assignBuffer(self, target):
        self.__rawDataBuffer = target

    def update(self):
        self.count += 1
        self.__buffer = self.__rawDataBuffer.getData()
        for i in range(self.__channelsNumber):
            lineHandler = self.__uiLineSeriesHandlerList[i]
            dpg.set_value(lineHandler, [self.__x, self.__buffer[i]])
            y_min, y_max = np.min(self.__buffer[i]), np.max(self.__buffer[i])
            dpg.set_axis_limits(f"CH{i+1}", y_min, y_max)

        if time.time() - self.starttime >= 1:
            self.starttime = time.time()
            #print(self.count)
            self.count = 0

    def fitGraph(self):
        pass
        #dpg.set_plot_xlimits_auto()
        #dpg.set_plot_ylimits_auto()