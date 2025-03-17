import matplotlib.pyplot as plt
import time
import numpy as np
import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, NUM_SAMPLE_TO_SHOW, SAMPLING_RATE, USE_MOCK_DATA, MOCK_TYPE, AUTO_FIT_MODE

class UiRawPlot(abstractthread):
    def __init__(self, daqThread):
        super().__init__()
        self.setThreadFrequency(30)
        self.__channelsNumber = CHANNELS_NUMBER

        self.__x = list(range(0, NUM_SAMPLE_TO_SHOW)) # 80000 samples = 10 seconds
        self.__buffer = np.zeros((self.__channelsNumber, NUM_SAMPLE_TO_SHOW))

        self.count = 0
        self.starttime = time.time()

        self.__realTimePlot = True

        self.__daqThread = daqThread

        self.__autoFitMode = AUTO_FIT_MODE

    def render(self):
        self.__uiWindowHandler = dpg.add_window(label="Raw Signal Viewer", width=800, height=600)
        with dpg.group(horizontal=True, parent=self.__uiWindowHandler):
            dpg.add_text("Real time plot:")
            dpg.add_button(label="Stop", callback=self.toggleRealTimePlot, tag="btn_ToggleRealTimePlot", width=75)
            dpg.add_text("  |  ")
            dpg.add_text("Auto fit mode:")
            dpg.add_button(label="Each Channel", callback=self.toggleAutoFitMode, tag="btn_ToggleAutoFitMode", width=100)
            dpg.add_text("  |  ")
            dpg.add_input_text(label="Sample received per second", default_value="0", enabled=False, tag="txt_SampleReceived", width=80)
            if USE_MOCK_DATA:
                dpg.add_text("  |  ")
                dpg.add_text("Mock Data Type: "+MOCK_TYPE)
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
        if self.__realTimePlot:
            self.count += 1
            self.__buffer = self.__rawDataBuffer.getData(reset_flag=False)
            if self.__autoFitMode == "eachChannel":
                for i in range(self.__channelsNumber):
                    lineHandler = self.__uiLineSeriesHandlerList[i]
                    dpg.set_value(lineHandler, [self.__x, self.__buffer[i]])
                    y_min, y_max = np.min(self.__buffer[i]), np.max(self.__buffer[i])
                    y_range = y_max - y_min
                    if y_min == y_max:
                        y_min -= 0.1
                        y_max += 0.1
                    else:
                        y_min = y_min - 0.1*y_range
                        y_max = y_max + 0.1*y_range
                    dpg.set_axis_limits(f"CH{i+1}", y_min, y_max)
            elif self.__autoFitMode == "allChannel":
                for i in range(self.__channelsNumber):
                    lineHandler = self.__uiLineSeriesHandlerList[i]
                    dpg.set_value(lineHandler, [self.__x, self.__buffer[i]])
                    y_min, y_max = np.min(self.__buffer), np.max(self.__buffer)
                    y_range = y_max - y_min
                    if y_min == y_max:
                        y_min -= 0.1
                        y_max += 0.1
                    else:
                        y_min = y_min - 0.1*y_range
                        y_max = y_max + 0.1*y_range
                    dpg.set_axis_limits(f"CH{i+1}", y_min, y_max)
            else:
                print("Invalid auto fit mode")

            if time.time() - self.starttime >= 1:
                self.starttime = time.time()
                samples_count = self.__daqThread.getSamplesCount()
                dpg.set_value("txt_SampleReceived", str(samples_count)+"/"+str(SAMPLING_RATE))

    def toggleAutoFitMode(self):
        if self.__autoFitMode == "eachChannel":
            self.__autoFitMode = "allChannel"
            dpg.configure_item("btn_ToggleAutoFitMode", label="All Channel")
        else:
            self.__autoFitMode = "eachChannel"
            dpg.configure_item("btn_ToggleAutoFitMode", label="Each Channel")
        self.fitGraph()

    def fitGraph(self):
        pass
        #dpg.set_plot_xlimits_auto()
        #dpg.set_plot_ylimits_auto()

    def toggleRealTimePlot(self):
        self.__realTimePlot = not self.__realTimePlot
        dpg.configure_item("btn_ToggleRealTimePlot", label="Stop" if self.__realTimePlot else "Continue")