import h5py
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch
import os
import argparse

# Define filter design functions
def design_lowpass_filter(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def design_highpass_filter(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def design_comb_filter(freq, fs, quality=30):
    nyquist = 0.5 * fs
    notch_freq = freq / nyquist
    b, a = iirnotch(notch_freq, quality)
    return b, a

# Apply filters to the data
def apply_filters(data, fs, lowpass, highpass):
    # Low-pass filter
    b_lowpass, a_lowpass = design_lowpass_filter(lowpass, fs)
    filtered_data = filtfilt(b_lowpass, a_lowpass, data, axis=0)
    
    # High-pass filter
    # b_highpass, a_highpass = design_highpass_filter(highpass, fs)
    # filtered_data = filtfilt(b_highpass, a_highpass, filtered_data, axis=0)
    
    # # Comb filter at 50 Hz
    # b_comb, a_comb = design_comb_filter(50, fs)
    # filtered_data = filtfilt(b_comb, a_comb, filtered_data, axis=0)
    
    return filtered_data

# Main function to read data, apply filters, and save the filtered data
def main():
    parser = argparse.ArgumentParser(description='Apply filters to HDF5 data.')
    parser.add_argument('input_filename', type=str, help='Input HDF5 file name')
    parser.add_argument('lowpass', type=float, help='Low-pass filter frequency (Hz)')
    parser.add_argument('highpass', type=float, help='High-pass filter frequency (Hz)')
    args = parser.parse_args()

    input_filename = args.input_filename
    lowpass = args.lowpass
    highpass = args.highpass
    fs = 8000  # Sampling rate from config
    
    # Open the input HDF5 file and read the dataset
    with h5py.File(input_filename, 'r') as h5file:
        dataset = h5file['raw_data']
        data = dataset[:]
    
    # Apply filters to the data
    filtered_data = apply_filters(data, fs, lowpass, highpass)
    
    # Generate output filename
    base_filename = os.path.basename(input_filename)
    name, ext = os.path.splitext(base_filename)
    output_filename = f'filtereddatarecord/{name}_{lowpass:06.2f}{highpass:04.0f}{ext}'
    
    # Ensure the filtereddatarecord directory exists
    os.makedirs('filtereddatarecord', exist_ok=True)
    
    # Save the raw and filtered data to the output HDF5 file
    with h5py.File(output_filename, 'w') as h5file:
        h5file.create_dataset('raw_data', data=data)
        h5file.create_dataset('filtered_data', data=filtered_data)
    
    print(f"Filtered data saved to {output_filename}")

if __name__ == "__main__":
    main()