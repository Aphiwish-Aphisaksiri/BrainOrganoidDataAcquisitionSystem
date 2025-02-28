import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
import os

def plot_mat_data(filename):
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    # Load the .mat file
    mat_data = loadmat(filename)
    
    # Extract the raw data
    raw_data = mat_data['raw_data']
    
    # Get the number of samples and channels
    num_samples = raw_data.shape[0]
    num_channels = raw_data.shape[1]
    
    # Create a figure with subplots for each channel
    fig, axes = plt.subplots(num_channels, 1, figsize=(12, 6 * num_channels), sharex=True)
    
    # Plot each channel
    for channel in range(num_channels):
        ax = axes[channel] if num_channels > 1 else axes
        ax.set_title(f'Raw Data - Channel {channel + 1}')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Voltage (V)')
        ax.plot(raw_data[:, channel], label=f'Channel {channel + 1}')
        ax.legend()
        ax.grid()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    filename = r'datarecord\record_20250228_154801.mat'
    plot_mat_data(filename)