import h5py
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_hdf5_data(filename):
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    # Open the HDF5 file
    with h5py.File(filename, 'r') as h5file:
        # Access the datasets
        raw_data = h5file['raw_data']
        filtered_data = h5file['filtered_data']
        
        # Get the number of samples and channels
        num_samples = raw_data.shape[0]
        num_channels = raw_data.shape[1]
        
        # Create a figure with subplots for each channel
        fig, axes = plt.subplots(num_channels, 2, figsize=(24, 6 * num_channels), sharex=True)
        
        # Plot each channel
        for channel in range(num_channels):
            # Plot raw data
            ax_raw = axes[channel, 0] if num_channels > 1 else axes[0]
            ax_raw.set_title(f'Raw Data - Channel {channel + 1}')
            ax_raw.set_xlabel('Sample Index')
            ax_raw.set_ylabel('Voltage (V)')
            ax_raw.plot(raw_data[:, channel], label=f'Channel {channel + 1}')
            ax_raw.legend()
            ax_raw.grid()
            
            # Plot filtered data
            ax_filtered = axes[channel, 1] if num_channels > 1 else axes[1]
            ax_filtered.set_title(f'Filtered Data - Channel {channel + 1}')
            ax_filtered.set_xlabel('Sample Index')
            ax_filtered.set_ylabel('Voltage (V)')
            ax_filtered.plot(filtered_data[:, channel], label=f'Channel {channel + 1}')
            ax_filtered.legend()
            ax_filtered.grid()
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    filename = r'filtereddatarecord\record_20250217_161243_000.253800.h5'
    plot_hdf5_data(filename)