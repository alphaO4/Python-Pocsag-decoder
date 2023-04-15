import numpy as np
import pocsag

def decode(iq_samples, sample_rate, frequency):
    # Tune the SDR to the specified frequency
    sdr = pyrtlsdr.RtlSdr()
    sdr.sample_rate = sample_rate
    sdr.center_freq = frequency
    sdr.gain = 50  # Set the gain to a reasonable value
    sdr.reset_buffer()  # Clear any old samples in the buffer

    # Read in the specified number of samples from the SDR
    samples_per_read = 1024
    iq_data = np.zeros(samples_per_read, dtype=np.complex64)
    while len(iq_samples) < samples_per_read:
        iq_data = sdr.read_samples(samples_per_read)
        iq_samples = np.concatenate((iq_samples, iq_data))