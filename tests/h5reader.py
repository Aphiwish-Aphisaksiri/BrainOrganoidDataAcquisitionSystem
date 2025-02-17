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
        # Access the dataset
        dataset = h5file['raw_data']
        
        # Get the number of samples and channels
        num_samples = dataset.shape[0]
        num_channels = dataset.shape[1]
        
        # Create a figure with subplots for each channel
        fig, axes = plt.subplots(num_channels, 1, figsize=(12, 6 * num_channels), sharex=True)
        
        # Plot each channel
        for channel in range(num_channels):
            ax = axes[channel] if num_channels > 1 else axes
            ax.set_title(f'Channel {channel + 1}')
            ax.set_xlabel('Sample Index')
            ax.set_ylabel('Voltage (V)')
            
            # Plot the data for the current channel
            ax.plot(dataset[:, channel], label=f'Channel {channel + 1}')
            
            ax.legend()
            ax.grid()
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    filename = r'datarecord\record_20250217_161243.h5'
    plot_hdf5_data(filename)