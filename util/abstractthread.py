import threading
import time
import numpy as np

DEFAULT_FREQUENCY = 100  # Hz
THREAD_PERIOD = 0.01

class abstractthread():
    def __init__(self):
        self.__threadStopEvent = threading.Event()
        self.__threadPeriod = THREAD_PERIOD
        self.__threadHandler = None

    def update(self):
        raise NotImplementedError

    def __run(self):
        next_call = time.time()
        while not self.__threadStopEvent.is_set():
            self.update()
            next_call += self.__threadPeriod
            sleep_time = next_call - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def startThread(self):
        if self.__threadHandler is None or not self.__threadHandler.is_alive():
            self.__threadStopEvent.clear()
            self.__threadHandler = threading.Thread(target=self.__run)
            self.__threadHandler.start()

    def stopThread(self):
        self.__threadStopEvent.set()
        if self.__threadHandler is not None:
            self.__threadHandler.join()

    def setThreadPeriod(self, period=THREAD_PERIOD):
        if period > 0:
            self.__threadPeriod = period
            # print(f"Period set to {period}")
            return True
        else:
            return False

    def setThreadFrequency(self, frequency=DEFAULT_FREQUENCY):
        if frequency > 0:
            self.setThreadPeriod(1 / frequency)
            return True
        else:
            return False

    def getThreadPeriod(self):
        return self.__threadPeriod

    def getThreadFrequency(self):
        return 1 / self.__threadPeriod