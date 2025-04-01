import matplotlib.pyplot as plt
import time
import numpy as np
import dearpygui.dearpygui as dpg
from brainorganoid.util.abstractthread import abstractthread
from brainorganoid.util.config import (CHANNELS_NUMBER, NUM_SAMPLE_TO_SHOW, SAMPLING_RATE, USE_MOCK_DATA, 
                                       MOCK_TYPE, AUTO_FIT_MODE, UNIT_MULTIPLIER, CHANNELS_PER_PORT, COM_PORT)

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

        self.__daqThreadInstances = daqThread

        self.__autoFitMode = AUTO_FIT_MODE
        self.__unitMultiplier = UNIT_MULTIPLIER
        if self.__unitMultiplier == 1_000_000:
            self.__unit = "uV"
        elif self.__unitMultiplier == 1_000:
            self.__unit = "mV"
        else:
            raise ValueError("Invalid unit multiplier")

        self.__cursorStart = 0
        self.__cursorEnd = NUM_SAMPLE_TO_SHOW

    def render(self):
        self.__uiWindowHandler = dpg.add_window(label="Raw Signal Viewer", width=800, height=600)
        with dpg.group(horizontal=True, parent=self.__uiWindowHandler):
            dpg.add_text("Real time plot:")
            dpg.add_button(label="Stop", callback=self.toggleRealTimePlot, tag="btn_ToggleRealTimePlot", width=75)
            dpg.add_text("  |  ")
            dpg.add_text("Auto fit mode:")
            dpg.add_button(label="Each Channel", callback=self.toggleAutoFitMode, tag="btn_ToggleAutoFitMode", width=100)
            dpg.add_text("  |  ")
            dpg.add_input_text(label="Sample received per second", default_value="0", enabled=False, tag="txt_SampleReceived", width=160)
            dpg.add_text("  |  ")
            dpg.add_text("Unit:")
            dpg.add_button(label=self.__unit, callback=self.toggleUnitMultiplier, tag="btn_toggle_unit", width=50)
            with dpg.group(horizontal=True, parent=self.__uiWindowHandler):
                dpg.add_text("Cursor:")
                dpg.add_input_int(default_value=self.__cursorStart, tag="input_int_start_cursor", width=100)
                dpg.add_text("to")
                dpg.add_input_int(default_value=self.__cursorEnd, tag="input_int_end_cursor", width=100)
            with dpg.group(horizontal=True, parent=self.__uiWindowHandler):
                dpg.add_input_text(tag="cursor_setting_feedback",
                                default_value="Cursor setting feedback",
                                width=350,
                                height=120,
                                readonly=True,
                                multiline=True)
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
            self.__buffer = self.__rawDataBuffer.getCircularData(reset_flag=False)
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
            samples_count = ""
            for i in range(len(COM_PORT)):
                samples_count += f"{COM_PORT[i]}: {self.__daqThreadInstances[i].getSamplesCount()}, "
            dpg.set_value("txt_SampleReceived", samples_count)

            self.setCursor()

    def toggleAutoFitMode(self):
        if self.__autoFitMode == "eachChannel":
            self.__autoFitMode = "allChannel"
            dpg.configure_item("btn_ToggleAutoFitMode", label="All Channel")
        else:
            self.__autoFitMode = "eachChannel"
            dpg.configure_item("btn_ToggleAutoFitMode", label="Each Channel")
        self.fitGraph()

    def toggleUnitMultiplier(self):
        self.__unitMultiplier = 1_000 if self.__unitMultiplier == 1_000_000 else 1_000_000
        daqFeedback = []
        for i, port in enumerate(COM_PORT):
            daqFeedback.append(self.__daqThreadInstances[i].setUnitMultiplier(self.__unitMultiplier))
        for i, port in enumerate(COM_PORT):
            if daqFeedback[i] == daqFeedback[0]:
                self.__unit = daqFeedback[i]
        dpg.configure_item("btn_toggle_unit", label=self.__unit)

    def fitGraph(self):
        pass
        #dpg.set_plot_xlimits_auto()
        #dpg.set_plot_ylimits_auto()

    def toggleRealTimePlot(self):
        self.__realTimePlot = not self.__realTimePlot
        dpg.configure_item("btn_ToggleRealTimePlot", label="Stop" if self.__realTimePlot else "Continue")

    def setCursor(self):
        self.__cursorStart = dpg.get_value("input_int_start_cursor")
        self.__cursorEnd = dpg.get_value("input_int_end_cursor")
            
        # Validate cursor range
        if self.__cursorStart < 0 or self.__cursorEnd > self.__buffer.shape[1] or self.__cursorStart >= self.__cursorEnd:
            dpg.set_value("cursor_setting_feedback", "Invalid cursor range. Please adjust the values.")
            return
    
        # Extract the data in the specified range
        data_in_range = self.__buffer[:, self.__cursorStart:self.__cursorEnd]
    
        # Calculate max and min for each channel
        feedback = "Channel Max/Min Values:\n"
        for i in range(self.__channelsNumber):
            channel_max = np.max(data_in_range[i])
            channel_min = np.min(data_in_range[i])
            feedback += f"CH{i+1}: Max = {channel_max:.2f}, Min = {channel_min:.2f}, Dif = {channel_max-channel_min:.4f}\n"
    
        # Update the feedback text
        dpg.set_value("cursor_setting_feedback", feedback)