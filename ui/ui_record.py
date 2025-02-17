import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class UiRecord(abstractthread):
    def __init__(self, recordThread):
        super().__init__()
        self.__recordThread = recordThread
        self.setThreadFrequency(30)
        self.__recording = False

    def render(self):
        with dpg.window(label="Record UI", width=400, height=300):
            dpg.add_text("Recording")
            dpg.add_button(label="Start", callback=self.startRecording, tag="btn_StartRecording")
            dpg.add_button(label="Stop", callback=self.stopRecording, tag="btn_StopRecording")
            dpg.add_input_text(tag="daq_setting_feedback",
                               width=250,
                               height=50,
                               readonly=True,
                               multiline=True,
                               default_value="Standing by")
            
    def assignRecord(self, target):
        self.__recordThread = target

    def update(self):
        pass

    def startRecording(self):
        if not self.__recording:
            if self.__recordThread.startRecording():
                dpg.set_value("daq_setting_feedback", "Recording...")
                self.__recording = True
            else:
                dpg.set_value("daq_setting_feedback", "Failed to start recording")
        else:
            dpg.set_value("daq_setting_feedback", "Already recording")

    def stopRecording(self):
        if self.__recording:
            if self.__recordThread.stopRecording():
                dpg.set_value("daq_setting_feedback", "Recording stopped")
                self.__recording = False
            else:
                dpg.set_value("daq_setting_feedback", "Failed to stop recording")
        else:
            dpg.set_value("daq_setting_feedback", "Currently not recording")

    