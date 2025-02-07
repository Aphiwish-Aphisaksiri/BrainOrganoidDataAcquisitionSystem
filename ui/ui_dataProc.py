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
                dpg.add_input_float(default_value=HIGH_PASS_FILTER,
                                    tag="input_highpassFilter",
                                    width=100,
                                    step=0,
                                    callback=self.setHighPassFilter)
                dpg.add_text(" - ")
                dpg.add_input_float(default_value=LOW_PASS_FILTER,
                                   tag="input_lowpassFilter",
                                    width=100,
                                    step=0,
                                    callback=self.setLowPassFilter)
                dpg.add_text("Hz")
            dpg.add_text("Notch Filter")
            with dpg.group(horizontal=True):
                dpg.add_input_float(default_value=NOTCH_FILTER,
                                    tag="input_notchFilter",
                                    width=100,
                                    step=0,
                                    callback=self.setNotchFilter)
                dpg.add_text("Hz")

            dpg.add_spacer(height=5)
            dpg.add_text("Gain")
            dpg.add_input_float(min_value=1, 
                               max_value=2000.0, 
                               default_value=GAIN,
                               tag="input_gain",
                               width=250,
                               step=1.0,
                               callback=self.setGain)
            
            dpg.add_input_text(tag="setting_feedback",
                               width=250,
                               height=50,
                               readonly=True,
                               multiline=True,
                               default_value="Standing by")
            
    def assignFilter(self, target):
        self.__filterThread = target

    def update(self):
        pass

    def setHighPassFilter(self):
        try:
            highPassFilter = float(dpg.get_value("input_highpassFilter"))
            if highPassFilter <= 0 or highPassFilter >= LOW_PASS_FILTER:
                raise ValueError("High-pass filter value must be positive and less than the low-pass filter value.")
            highPassFilter = self.__filterThread.setHighPassFilter(highPassFilter)
            dpg.set_value("input_highpassFilter", highPassFilter)
            dpg.set_value("setting_feedback", "High-pass filter set successfully.")
        except ValueError as e:
            dpg.set_value("setting_feedback", f"Error: {e}")
        except Exception as e:
            dpg.set_value("setting_feedback", f"Unexpected error: {e}")

    def setLowPassFilter(self):
        try:
            lowPassFilter = float(dpg.get_value("input_lowpassFilter"))
            if lowPassFilter <= HIGH_PASS_FILTER:
                raise ValueError("Low-pass filter value must be greater than the high-pass filter value.")
            lowPassFilter = self.__filterThread.setLowPassFilter(lowPassFilter)
            dpg.set_value("input_lowpassFilter", lowPassFilter)
            dpg.set_value("setting_feedback", "Low-pass filter set successfully.")
        except ValueError as e:
            dpg.set_value("setting_feedback", f"Error: {e}")
        except Exception as e:
            dpg.set_value("setting_feedback", f"Unexpected error: {e}")

    def setNotchFilter(self):
        try:
            notchFilter = float(dpg.get_value("input_notchFilter"))
            if notchFilter <= 0:
                raise ValueError("Notch filter value must be positive.")
            notchFilter = self.__filterThread.setNotchFilter(notchFilter)
            dpg.set_value("input_notchFilter", notchFilter)
            dpg.set_value("setting_feedback", "Notch filter set successfully.")
        except ValueError as e:
            dpg.set_value("setting_feedback", f"Error: {e}")
        except Exception as e:
            dpg.set_value("setting_feedback", f"Unexpected error: {e}")
    
    def setGain(self):
        try:
            gain = float(dpg.get_value("input_gain"))
            if gain <= 0:
                raise ValueError("Gain value must be positive.")
            gain = self.__filterThread.setGain(gain)
            dpg.set_value("input_gain", gain)
            dpg.set_value("setting_feedback", "Gain set successfully.")
        except ValueError as e:
            dpg.set_value("setting_feedback", f"Error: {e}")
        except Exception as e:
            dpg.set_value("setting_feedback", f"Unexpected error: {e}")