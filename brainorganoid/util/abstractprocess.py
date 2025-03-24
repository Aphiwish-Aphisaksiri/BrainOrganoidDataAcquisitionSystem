from multiprocessing import Process, Event
import time

DEFAULT_PROCESS_PERIOD = 0.01  # Seconds

class AbstractProcess:
    def __init__(self):
        self._processPeriod = DEFAULT_PROCESS_PERIOD
        self._stopEvent = Event()
        self._process = Process(target=self._run)

    def update(self):
        """Override this method with the task logic."""
        raise NotImplementedError

    def _run(self):
        """Internal method to run the process loop."""
        while not self._stopEvent.is_set():
            self.update()
            time.sleep(self._processPeriod)

    def startProcess(self):
        """Start the process."""
        if not self._process.is_alive():
            self._process.start()

    def stopProcess(self):
        """Stop the process."""
        self._stopEvent.set()
        if self._process.is_alive():
            self._process.join()

    def setProcessPeriod(self, period):
        """Set the process execution period."""
        if period > 0:
            self._processPeriod = period
            return True
        return False

    def getProcessPeriod(self):
        """Get the process execution period."""
        return self._processPeriod