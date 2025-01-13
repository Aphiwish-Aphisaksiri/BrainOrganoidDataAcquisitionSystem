import unittest
from util.abstractthread import abstractthread
import time

class TestThread(abstractthread):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def update(self):
        self.counter += 1

class TestAbstractThread(unittest.TestCase):
    def test_thread_start_stop(self):
        test_thread = TestThread()
        test_thread.setThreadPeriod(0.1)  # Set period to 0.1 seconds
        test_thread.startThread()
        time.sleep(0.5)  # Let the thread run for 0.5 seconds
        test_thread.stopThread()
        self.assertGreaterEqual(test_thread.counter, 4)  # At least 4 updates should have occurred
        print("AbstractThread - Start/Stop test passed")

    def test_thread_frequency(self):
        test_thread = TestThread()
        test_thread.setThreadFrequency(10)  # Set frequency to 10 Hz
        test_thread.startThread()
        time.sleep(0.5)  # Let the thread run for 0.5 seconds
        test_thread.stopThread()
        self.assertGreaterEqual(test_thread.counter, 5)  # At least 5 updates should have occurred
        print("AbstractThread - Frequency test passed")

if __name__ == '__main__':
    unittest.main()