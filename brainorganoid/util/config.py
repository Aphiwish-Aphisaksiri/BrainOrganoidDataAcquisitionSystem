# FILE: util/config.py

# Configuration variables

## DAQ configuration
USE_MOCK_DATA = False
MOCK_TYPE = "SineWave" # "SineWave", "TriangleWave", "ChannelNumber"
COM_PORT = ['COM5', 'COM8']
CHANNEL_ASSIGNMENT = {
    COM_PORT[0]: [1, 2, 3, 4],
    COM_PORT[1]: [5, 6, 7, 8]
}
BAUDRATE = 1250000
SAMPLING_RATE = 8000
CHANNELS_NUMBER = 8
SAMPLES_PER_PACKAGE = 2
DOWN_SAMPLING_FACTOR = 1

## Plotting configuration
TIME_TO_SHOW = 4
AUTO_FIT_MODE = "eachChannel" # "eachChannel", "allChannel"

## Filter configuration
HIGH_PASS_FILTER = 0.25
LOW_PASS_FILTER = 1500

## Record configuration
RECORD_FORMAT = "mat" # "mat", "h5"
RECORD_CHANNELS = "even" # 'even' for even channels, 'odd' for odd channels, 'all' for all channels
RECORD_BUFFER_SIZE = SAMPLING_RATE

# =================================================================================================

## CONSTANTS
# DAQ Constants
CHANNELS_PER_PORT = len(CHANNEL_ASSIGNMENT[COM_PORT[0]])
BITS_PER_SAMPLE = 24
HEADER_LEN = 1
TERM_LEN = 1
HEADER_VALUE = 0xAA
TERMINATOR_VALUE = 0xFF
VREF = 2.4
GAIN = 12
UNIT_MULTIPLIER = 1_000
ON_ELECTRODE_CHANNEL_COUNT = 8

# Plotting Constants
CONVERTED_RAW_DATA_BUFFER_SIZE = int(TIME_TO_SHOW*SAMPLING_RATE/DOWN_SAMPLING_FACTOR)
NUM_SAMPLE_TO_SHOW = CONVERTED_RAW_DATA_BUFFER_SIZE

# Filter Constants
FILTER_ORDER = 4
NOTCH_FILTER = 50
GAIN = 1
SAVE_FILTER_COEFFICIENT = False