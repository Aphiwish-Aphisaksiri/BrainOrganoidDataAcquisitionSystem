import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Load the HDF5 file
file_path = r'filtereddatarecord\record_20250219_140035_3800.000000.h5'
with h5py.File(file_path, 'r') as file:
    # Extract the datasets
    raw_data = file['raw_data'][:]
    filtered_data = file['filtered_data'][:]

# Sampling rate
fs = 8000  # Adjust this value based on your configuration

# Perform FFT on raw data
n_raw = raw_data.shape[0]
yf_raw = fft(raw_data, axis=0)
xf_raw = fftfreq(n_raw, 1 / fs)[:n_raw // 2]

# Perform FFT on filtered data
n_filtered = filtered_data.shape[0]
yf_filtered = fft(filtered_data, axis=0)
xf_filtered = fftfreq(n_filtered, 1 / fs)[:n_filtered // 2]

# Create subplots for comparison
fig, axes = plt.subplots(2, 1, figsize=(12, 12))

# Plot the FFT result for raw data
for i in range(raw_data.shape[1]):
    axes[0].plot(xf_raw, 2.0 / n_raw * np.abs(yf_raw[:n_raw // 2, i]), label=f'Channel {i + 1}')
axes[0].set_title('FFT of Raw Data')
axes[0].set_xlabel('Frequency (Hz)')
axes[0].set_ylabel('Amplitude')
axes[0].legend()
axes[0].grid(True)

# Plot the FFT result for filtered data
for i in range(filtered_data.shape[1]):
    axes[1].plot(xf_filtered, 2.0 / n_filtered * np.abs(yf_filtered[:n_filtered // 2, i]), label=f'Channel {i + 1}')
axes[1].set_title('FFT of Filtered Data')
axes[1].set_xlabel('Frequency (Hz)')
axes[1].set_ylabel('Amplitude')
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.show()