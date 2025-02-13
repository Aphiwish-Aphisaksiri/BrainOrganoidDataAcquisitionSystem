import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE

class UiDaq(abstractthread):
    def __init__(self, daqThread):
        super().__init__()
        self.__daqThread = daqThread
        self.setThreadFrequency(30)
        self.__recording = False

    def render(self):
        with dpg.window(label="Daq UI", width=400, height=300):
            dpg.add_text("Recording")
            dpg.add_button(label="Start", callback=self.startRecording, tag="btn_StartRecording")
            dpg.add_button(label="Stop", callback=self.stopRecording, tag="btn_StopRecording")
            dpg.add_input_text(tag="daq_setting_feedback",
                               width=250,
                               height=50,
                               readonly=True,
                               multiline=True,
                               default_value="Standing by")
            
    def assignDaq(self, target):
        self.__daqThread = target

    def update(self):
        pass

    def startRecording(self):
        self.__daqThread.startRecording()
        dpg.set_value("daq_setting_feedback", "Recording...")

    def stopRecording(self):
        self.__daqThread.stopRecording()
        dpg.set_value("daq_setting_feedback", "Recording stopped")

    