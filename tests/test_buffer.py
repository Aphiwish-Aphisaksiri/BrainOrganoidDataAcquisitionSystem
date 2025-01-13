from util.buffer import Buffer
import numpy as np
import unittest
import time

class TestBuffer(unittest.TestCase):
    def test_add_data(self):
        buffer = Buffer(2, 3)
        buffer.addData([1, 2])
        self.assertTrue(buffer.isDataUpdated())
        self.assertEqual(buffer.getData().tolist(), [[0, 0, 1], [0, 0, 2]])
        print("Buffer - Add data test passed")

    def test_add_batch_data(self):
        buffer = Buffer(2, 3)
        buffer.addBatchData(np.array([[1, 3, 5], [2, 4, 6]]))
        self.assertTrue(buffer.isDataUpdated())
        self.assertEqual(buffer.getData().tolist(), [[1, 3, 5], [2, 4, 6]])
        print("Buffer - Add batch data test passed")
    
    def test_get_data(self):
        buffer = Buffer(2, 3)
        buffer.addData([1, 2])
        self.assertTrue(buffer.isDataUpdated())
        self.assertEqual(buffer.getData().tolist(), [[0, 0, 1], [0, 0, 2]])
        self.assertFalse(buffer.isDataUpdated())
        print("Buffer - Get data test passed")

    def test_is_data_updated(self):
        buffer = Buffer(2, 3)
        buffer.addData([1, 2])
        self.assertTrue(buffer.isDataUpdated())
        print("Buffer - Is data updated test passed")

    def test_set_flag_data_updated(self):
        buffer = Buffer(2, 3)
        buffer.setFlagDataUpdated()
        self.assertTrue(buffer.isDataUpdated())
        print("Buffer - Set flag data updated test passed")

if __name__ == '__main__':
    unittest.main()