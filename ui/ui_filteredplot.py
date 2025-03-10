import matplotlib.pyplot as plt
import time
import numpy as np
import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

NUM_SAMPLE_TO_SHOW = 10000

class UiFilteredPlot(abstractthread):
    def __init__(self):
        super().__init__()
        self.setThreadFrequency(30)
        self.__channelsNumber = CHANNELS_NUMBER

        self.__x = list(range(0, NUM_SAMPLE_TO_SHOW)) # 80000 samples = 10 seconds
        self.__buffer = np.zeros((self.__channelsNumber, NUM_SAMPLE_TO_SHOW))

        self.count = 0
        self.starttime = time.time()

        self.__realTimePlot = True

    def render(self):
        self.__uiFilteredWindowHandler = dpg.add_window(label="Filtered Signal Viewer", width=800, height=600)
        with dpg.group(horizontal=True, parent=self.__uiFilteredWindowHandler):
            dpg.add_text("Real time plot:")
            dpg.add_button(label="Stop", callback=self.toggleRealTimePlot, tag="btn_ToggleRealTimePlot_filtered", width=75)
        self.__uiFilteredSubplotHandler = dpg.add_subplots(rows=self.__channelsNumber, columns=1, width=-1, height=-1, no_title=True, parent=self.__uiFilteredWindowHandler)
        self.__uiLineSeriesHandlerList = []    
        for i in range(self.__channelsNumber):
            with dpg.plot(no_title=True, parent=self.__uiFilteredSubplotHandler):
                dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                with dpg.plot_axis(dpg.mvYAxis, label=f"CH{i+1}", no_tick_labels=True, tag=f"filteredCH{i+1}"):
                    self.__uiLineSeriesHandlerList.append(dpg.add_line_series(self.__x, self.__buffer[i], label=f"Channel {i+1}"))

    def assignBuffer(self, target):
        self.__filteredDataBuffer = target

    def update(self):
        if self.__realTimePlot:
            self.count += 1
            self.__buffer = self.__filteredDataBuffer.getData(reset_flag=False)
            for i in range(self.__channelsNumber):
                lineHandler = self.__uiLineSeriesHandlerList[i]
                dpg.set_value(lineHandler, [self.__x, self.__buffer[i]])
                y_min, y_max = np.min(self.__buffer[i]), np.max(self.__buffer[i])
                dpg.set_axis_limits(f"filteredCH{i+1}", y_min*1.1, y_max*1.1)

            if time.time() - self.starttime >= 1:
                self.starttime = time.time()
                #print(self.count)
                self.count = 0

    def fitGraph(self):
        pass
        #dpg.set_plot_xlimits_auto()
        #dpg.set_plot_ylimits_auto()

    def toggleRealTimePlot(self):
        self.__realTimePlot = not self.__realTimePlot
        dpg.configure_item("btn_ToggleRealTimePlot_filtered", label="Stop" if self.__realTimePlot else "Continue")