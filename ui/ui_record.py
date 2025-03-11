import dearpygui.dearpygui as dpg
from util.abstractthread import abstractthread
from util.config import CHANNELS_NUMBER, SAMPLES_PER_PACKAGE, RECORD_CHANNELS, ON_ELECTRODE_CHANNEL_COUNT, SAMPLING_RATE

class UiRecord(abstractthread):
    def __init__(self, recordThread):
        super().__init__()
        self.__recordThread = recordThread
        self.setThreadFrequency(30)
        self.__recording = False
        self.__recordingChannels = []
        self.getChannelRecordInit()

    def render(self):
        with dpg.window(label="Record UI", tag="tag_window_record", width=400, height=300):
            dpg.add_text("|Recording Channels|")
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False):
                    for i in range(1, ON_ELECTRODE_CHANNEL_COUNT+1):
                        if RECORD_CHANNELS == "even":
                            if i % 2 == 0:
                                checkboxValue = True
                            else:
                                checkboxValue = False
                        elif RECORD_CHANNELS == "odd":
                            if i % 2 == 1:
                                checkboxValue = True
                            else:
                                checkboxValue = False
                        elif RECORD_CHANNELS == "all":
                            checkboxValue = True

                        dpg.add_checkbox(label=f"Channel {i}", tag=f"checkbox_ch{i}", default_value=checkboxValue, callback=self.setChannelRecord)

                dpg.add_text("|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n")
                with dpg.group(horizontal=False):
                    dpg.add_text("Channel Arrangement")
                    dpg.add_input_text(tag="input_text_channel_arrangement",
                                width=105,
                                height=73,
                                readonly=True,
                                multiline=True,
                                default_value="3   2   1\n\n4  GND  8  REF\n\n5   6   7")
            
            dpg.add_text("____________________________________________________")
            dpg.add_text("|Configurations|")
            dpg.add_text(f"Number of Channels: {CHANNELS_NUMBER} Channel(s)")
            dpg.add_text(f"Stacking samples: {SAMPLES_PER_PACKAGE} Sample(s)")
            dpg.add_text(f"Sampling rate: {SAMPLING_RATE} Hz")
            dpg.add_text("____________________________________________________")
            dpg.add_text("|Recording Control|")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.startRecording, tag="btn_StartRecording", width=126)
                dpg.add_button(label="Stop", callback=self.stopRecording, tag="btn_StopRecording", width=126)
            dpg.add_input_text(tag="daq_setting_feedback",
                               width=260,
                               height=50,
                               readonly=True,
                               multiline=True,
                               default_value="Standing by")
            
            
            
    def assignRecord(self, target):
        self.__recordThread = target

    def update(self):
        pass

    def getChannelRecordInit(self):
        self.__recordingChannels = self.__recordThread.getChannelRecordInit()

    def setChannelRecord(self, sender, app_data):
        channel = int(sender[-1])
        if app_data:
            self.__recordingChannels.append(channel)
        else:
            self.__recordingChannels.remove(channel)

        while self.__recordingChannels.count(channel) > 1:
            self.__recordingChannels.remove(channel)
            dpg.set_value("daq_setting_feedback", f"Channel {channel} is already selected")
        
        self.__recordingChannels.sort()

        if len(self.__recordingChannels) > CHANNELS_NUMBER:
            dpg.set_value("daq_setting_feedback", f"Recording channels exceed the \nnumber of channels")
        elif len(self.__recordingChannels) == 0:
            dpg.set_value("daq_setting_feedback", "No recording channel selected")
        else:
            dpg.set_value("daq_setting_feedback", f"Recording channels: {self.__recordThread.setChannelRecord(self.__recordingChannels)}")


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

    