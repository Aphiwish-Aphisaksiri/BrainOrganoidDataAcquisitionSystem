import logging
from multiprocessing import Array
from brainorganoid.daq.daqprocess import DaqProcess
from brainorganoid.daq.datasynchronize import DataSynchronize
from brainorganoid.preprocess.filter import Filter
from brainorganoid.ui.ui_rawplot import UiRawPlot
from brainorganoid.record.record import Record
from brainorganoid.record.recordmat import RecordMat
from brainorganoid.util.buffer import Buffer
from brainorganoid.util.arraybuffer import ArrayBuffer
from brainorganoid.ui.ui_dataProc import UiDataProc
from brainorganoid.ui.ui_filteredplot import UiFilteredPlot
from brainorganoid.ui.ui_record import UiRecord
from brainorganoid.ui.ui_settings import UiSettings
from brainorganoid.util.config import CHANNELS_NUMBER, CONVERTED_RAW_DATA_BUFFER_SIZE, RECORD_FORMAT, COM_PORT, CHANNEL_ASSIGNMENT

class App():
    def __init__(self):
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Initializing application...")

        # Variables
        self.__channelsNumber = CHANNELS_NUMBER
        self.__rawDataBuffers = ArrayBuffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE, dtype='d')
        self.__SamplesReceivedPerSecondBuffers = ArrayBuffer(numChannel=len(COM_PORT), numSample=1, dtype='d')
        self.__synchronizedDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__filteredDataBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)
        self.__recordBuffer = Buffer(numChannel=self.__channelsNumber, numSample=CONVERTED_RAW_DATA_BUFFER_SIZE)

        self.configChecker()

    def initializeProcesses(self):
        try:
            self.__daqProcesses = []
            for daqIndex, port in enumerate(COM_PORT):
                daqProcess = DaqProcess(daqIndex)
                # Get the channel indices assigned to this COM_PORT from CHANNEL_ASSIGNMENT
                assigned_channels = CHANNEL_ASSIGNMENT[port]
                # Map the buffers for the assigned channels
                daqProcess.assignBuffers(self.__rawDataBuffers, assigned_channels)
                daqProcess.assignSamplesReceivedPerSecondBuffer(self.__SamplesReceivedPerSecondBuffers, daqIndex)
                self.__daqProcesses.append(daqProcess)
        except Exception as e:
            logging.error(f"Error initializing processes: {e}")
            raise

    def initializeThreads(self):
        try:
            self.__dataSynchronize = DataSynchronize()
            self.__dataSynchronize.assignRawDataBufferInstances(self.__rawDataBuffers)
            self.__dataSynchronize.assignSynchronizedDataBuffer(self.__synchronizedDataBuffer)
            self.__dataSynchronize.assignRecordDataBuffer(self.__recordBuffer)
            self.__dataSynchronize.assignSamplesReceivedPerSecondBuffers(self.__SamplesReceivedPerSecondBuffers)

            self.__filter = Filter()
            self.__filter.assignInletBuffer(self.__synchronizedDataBuffer)
            self.__filter.assignOutletBuffer(self.__filteredDataBuffer)

            self.__uiFilter = UiDataProc(self.__filter)
            self.__uiFilter.assignFilter(self.__filter)

            self.__uiRawPlot = UiRawPlot(self.__dataSynchronize)
            self.__uiRawPlot.assignBuffer(self.__synchronizedDataBuffer)

            self.__uiFilteredPlot = UiFilteredPlot()
            self.__uiFilteredPlot.assignBuffer(self.__filteredDataBuffer)

            self.__record = self.initializeRecord()
            self.__uiRecord = UiRecord(self.__record)
            self.__uiRecord.assignRecord(self.__record)

            self.__uiSettings = UiSettings(self)
        except Exception as e:
            logging.error(f"Error initializing threads: {e}")
            raise

    def initializeRecord(self):
        if RECORD_FORMAT == "mat":
            record = RecordMat()
        elif RECORD_FORMAT == "h5":
            record = Record()
        else:
            logging.error("Invalid RECORD_FORMAT in config.py")
            exit()
        record.assignBuffer(self.__recordBuffer)
        return record

    def renderApp(self):
        try:
            for daqProcess in self.__daqProcesses:
                daqProcess.startProcess()
            self.__dataSynchronize.startThread()
            self.__uiRecord.render()
            self.__filter.startThread()
            self.__uiFilter.render()
            self.__uiFilter.startThread()
            self.__uiRawPlot.render()
            self.__uiRawPlot.startThread()
            self.__uiFilteredPlot.render()
            self.__uiFilteredPlot.startThread()
            self.__record.startThread()

            self.__uiSettings.render()
        except Exception as e:
            logging.error(f"Error rendering application: {e}")
            self.stopApp()
            raise

    def stopApp(self):
        """Stop all processes and threads gracefully."""
        try:
            logging.info("Stopping application...")
            # Stop all DAQ processes
            for daqProcess in self.__daqProcesses:
                daqProcess.stopProcess()
    
            # Stop all threads
            self.__uiFilteredPlot.stopThread()
            self.__uiRawPlot.stopThread()
            self.__uiFilter.stopThread()
            self.__filter.stopThread()
            self.__uiRecord.stopThread()
            self.__record.stopThread()
            self.__dataSynchronize.stopThread()
    
            # Close resources
            self.__record.close()
            logging.info("Application stopped successfully.")
        except Exception as e:
            logging.error(f"Error stopping application: {e}")

    def configChecker(self):
        try:
            if RECORD_FORMAT not in ["mat", "h5"]:
                raise ValueError("Invalid RECORD_FORMAT in config.py")
            if len(COM_PORT) != len(CHANNEL_ASSIGNMENT):
                raise ValueError("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
            for port in COM_PORT:
                if port not in CHANNEL_ASSIGNMENT:
                    raise ValueError("COM_PORT and CHANNEL_ASSIGNMENT in config.py do not match")
                if sum(len(CHANNEL_ASSIGNMENT[p]) for p in COM_PORT) != CHANNELS_NUMBER:
                    raise ValueError("CHANNEL_ASSIGNMENT in config.py does not match CHANNELS_NUMBER")
        except ValueError as e:
            logging.error(e)
            exit()