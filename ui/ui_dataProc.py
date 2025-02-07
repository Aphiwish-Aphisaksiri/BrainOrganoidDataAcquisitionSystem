import matplotlib.pyplot as plt
import time
import numpy as np
import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, HIGH_PASS_FILTER, LOW_PASS_FILTER, NOTCH_FILTER, GAIN

class UiDataProc(abstractthread):
    def __init__(self, filterThread):
        super().__init__()
        self.__filterThread = filterThread
        self.setThreadFrequency(30)
        self.__channelsNumber = CHANNELS_NUMBER

        #TODO: Implement get filter range and gain from filterThread


    def render(self):
        with dpg.window(label="Data processing UI", width=400, height=300):
            dpg.add_text("Filter Range")
            with dpg.group(horizontal=True):
                dpg.add_input_text(default_value=HIGH_PASS_FILTER,
                                    width=100,
                                    callback=self.setHighPassFilter)
                dpg.add_text(" - ")
                dpg.add_input_text(default_value=LOW_PASS_FILTER,
                                    width=100,
                                    callback=self.setLowPassFilter)
                dpg.add_text("Hz")
            dpg.add_text("Notch Filter")
            dpg.add_input_text(default_value=NOTCH_FILTER,
                                width=100,
                                callback=self.setNotchFilter)

            dpg.add_spacer(height=5)
            dpg.add_text("Gain")
            dpg.add_input_float(min_value=0.5, 
                               max_value=2000.0, 
                               default_value=GAIN,
                               width=250,
                               step=1.0,
                               callback=self.setGain)
            
    def assignFilter(self, target):
        self.__filterThread = target

    def update(self):
        pass

    def setHighPassFilter(self):
        #TODO: Implement setHighPassFilter
        pass

    def setLowPassFilter(self):
        #TODO: Implement setLowPassFilter
        pass

    def setNotchFilter(self):
        pass

    def setGain(self):
        #TODO: Implement setGain
        pass