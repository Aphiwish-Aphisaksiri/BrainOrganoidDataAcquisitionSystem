import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, iirnotch, filtfilt
from scipy.fft import fft, fftfreq

# Define filter design functions
def design_bandpass_filter(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def design_notch_filter(freq, fs, quality=30):
    nyquist = 0.5 * fs
    notch_freq = freq / nyquist
    b, a = iirnotch(notch_freq, quality)
    return b, a

# Apply filters to the data
def apply_filters(data, fs):
    # Band-pass filter
    b_bandpass, a_bandpass = design_bandpass_filter(0.1, 60, fs)
    filtered_data = filtfilt(b_bandpass, a_bandpass, data, axis=0)
    
    # Notch filter at 50 Hz
    b_notch, a_notch = design_notch_filter(50, fs)
    filtered_data = filtfilt(b_notch, a_notch, filtered_data, axis=0)
    
    return filtered_data

# Plot the time-domain data
def plot_time_domain(data, fs):
    t = np.arange(data.shape[0]) / fs
    
    plt.figure(figsize=(12, 6))
    for i in range(data.shape[1]):
        plt.plot(t, data[:, i], label=f'Channel {i + 1}')
    
    plt.title('Time Domain')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid()
    plt.show()

# Perform FFT and plot the results
def plot_frequency_domain(data, fs):
    n = data.shape[0]
    yf = fft(data, axis=0)
    xf = fftfreq(n, 1 / fs)[:n // 2]
    
    plt.figure(figsize=(12, 6))
    for i in range(data.shape[1]):
        plt.plot(xf, 2.0 / n * np.abs(yf[:n // 2, i]), label=f'Channel {i + 1}')
    
    plt.title('Frequency Domain')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.xlim(0, 100)
    plt.legend()
    plt.grid()
    plt.show()

# Main function to read data, apply filters, and plot
def main():
    filename = r'datarecord\record_20250217_152154.h5'
    fs = 8000  # Sampling rate from config
    
    # Open the HDF5 file and read the dataset
    with h5py.File(filename, 'r') as h5file:
        dataset = h5file['raw_data']
        data = dataset[:]
    
    # Apply filters to the data
    filtered_data = apply_filters(data, fs)
    
    # Plot the time domain of the filtered data
    plot_time_domain(filtered_data, fs)
    
    # Plot the frequency domain of the filtered data
    plot_frequency_domain(filtered_data, fs)

if __name__ == "__main__":
    main()