# FILE: util/config.py

# Configuration variables

## DAQ configuration
USE_MOCK_DATA = True
MOCK_TYPE = "SineWave"
COM_PORT = 'COM5'
BAUDRATE = 1250000
SAMPLING_RATE = 8000
CHANNELS_NUMBER = 4
SAMPLES_PER_PACKAGE = 2
BITS_PER_SAMPLE = 24  # 19 bits
HEADER_LEN = 1
TERM_LEN = 1
HEADER_VALUE = 0xAA
TERMINATOR_VALUE = 0xFF
VREF = 2.4
GAIN = 12
ON_ELECTRODE_CHANNEL_COUNT = 8

## Plotting configuration
TIME_TO_SHOW = 1.5
CONVERTED_RAW_DATA_BUFFER_SIZE = int(TIME_TO_SHOW*SAMPLING_RATE)
NUM_SAMPLE_TO_SHOW = int(TIME_TO_SHOW*SAMPLING_RATE)

## Filter configuration
HIGH_PASS_FILTER = 0.25
LOW_PASS_FILTER = 1500
FILTER_ORDER = 4
NOTCH_FILTER = 50
GAIN = 1

## Record configuration
RECORD_FORMAT = "mat"
# "mat" for MATLAB .mat file
# "h5" for HDF5 file
RECORD_CHANNELS = "odd"
# "even" for even channels
# "odd" for odd channels
# "all" for all channels