"""
Utility functions
"""

import numpy as np

from scipy import signal
from scipy.fftpack import fft, fftshift


def generate_spectrum(f0, fs, a0, b, n_window, n_fft):
    """Reference amplitude spectrum generation

    The function generates an harmonic amplitude spectrum and then convolves it with the frequency response of the
    window used in the STFT

    Parameters
    ----------
    f0 : int
        Fundamental frequency
    fs : int
        Sampling frequency
    a0 : float
        Fundamental frequency's amplitude
    b : float
        Scaling factor for the amplitude's exponential decrease
    n_window : int
        FFT window size
    n_fft : int
        Length of the Fourier transform

    Returns
    -------
    ndarray, shape (n_fft // 2,)
        Output spectrum

    """
    hann_window = signal.hann(n_window)  # window used in the STFT
    hann_window_fft = fft(hann_window, n_fft) / (len(hann_window) / 2.0)  # window's FFT
    hann_window_response = np.abs(fftshift(hann_window_fft) / abs(hann_window_fft).max())  # window's frequency response

    n_harmonics = fs // (2 * f0)
    harmonic_spec = np.zeros(n_fft)

    # fill the harmonic spectrum array with exponentially decreasing amplitudes
    for n in range(1, n_harmonics):
        harmonic_spec[int(round(n_fft * n * f0 / fs))] = a0 * np.exp(-b * n)

    # symmetrization
    for n in range(1, n_harmonics):
        harmonic_spec[harmonic_spec.size - n] = harmonic_spec[n]

    # convolution of the window's frequency response and the harmonic spectrum
    harmonic_spec_window_conv = signal.convolve(hann_window_response, fftshift(harmonic_spec))
    shift = fftshift(harmonic_spec_window_conv)
    output_spec = shift[:n_fft // 2]

    return output_spec / np.sum(output_spec)


def export_subsequences(subsequences, fs, hop_length, export_path):
    """Export reported subsequences for visualization in AudioSculpt

    Parameters
    ----------
    subsequences : list
        List of reported subsequences
    fs : int
        Sampling frequency
    hop_length : int
        Number of frames between STFT columns
    export_path : string
        Path where to export the reported subsequences

    """
    with open(export_path, 'w') as f:
        for i in range(len(subsequences)):
            start_time = subsequences[i][1][0] * hop_length / fs
            end_time = subsequences[i][2][0] * hop_length / fs
            f.write("{:.6f} {:.6f} subsequence{:d}\n".format(start_time, start_time, i + 1))
            f.write("{:.6f} {:.6f} subsequence{:d}\n".format(end_time, end_time, i + 1))


def import_annotations(file_path):
    """Import annotations from .lab file

    Parameters
    ----------
    file_path : string
        Location of the .lab file

    Returns
    -------
    list
        List of times for which there is a marker in the .lab file

    """
    annotations = []

    with open(file_path, 'r') as f:
        for line in f.readlines():
            time = line.split("\t")[0]
            annotations.append(float(time))

    return annotations
