import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz
import os
import sys

# Add the root directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.config import SAMPLING_RATE

def plot_frequency_response(filename):
    with open(filename, 'r') as f:
        filter_coefficients = json.load(f)

    for filter_type, coeffs in filter_coefficients.items():
        b = np.array(coeffs['b'])
        a = np.array(coeffs['a'])
        w, h = freqz(b, a, worN=8000)
        plt.plot(0.5 * SAMPLING_RATE * w / np.pi, np.abs(h), label=f'{filter_type} filter')

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.title('Frequency Response')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    filename = r'tests\filter_coefficients.json'
    plot_frequency_response(filename)