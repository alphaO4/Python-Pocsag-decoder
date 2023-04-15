import numpy as np
import time
from rtlsdr import RtlSdr

# config
sample_rate = 2.4e6
frequency = 00000000
baud_rate = 1200
baud_period = 1 / baud_rate
samples_per_symbol = int(sample_rate / baud_rate)
sync_word = '0x1AFCBDDF'  # POCSAG sync word


def receive():
    # Tune the SDR to the specified frequency
    sdr = RtlSdr()
    sdr.sample_rate = sample_rate
    sdr.center_freq = frequency
    sdr.gain = 50  # Set the gain to a reasonable value
    #sdr.reset_buffer()  # Clear any old samples in the buffer

    # Read in the specified number of samples from the SDR
    samples_per_read = 1024
    iq_data = np.zeros(samples_per_read, dtype=np.complex64)
    iq_samples = np.array([], dtype=np.complex64)
    while True:
        iq_data = sdr.read_samples(samples_per_read)
        iq_samples = np.concatenate((iq_samples, iq_data))
        time.sleep(0.1)
        if len(iq_samples) >= samples_per_symbol:
            break

    return iq_samples


def decode_pocsag(bits):
    message = ''
    sync_found = False
    
    for i in range(len(bits)-31):
        if not sync_found and hex(int(bits[i:i+32], 2)) == sync_word:
            sync_found = True
            i += 31
        elif sync_found:
            char_bits = bits[i:i+8]
            char_code = int(''.join(map(str, char_bits[::-1])), 2)  # reverse bit order and convert to integer
            if char_code == 0:  # end of message
                break
            if char_code >= 32 and char_code <= 127:  # printable ASCII characters
                message += chr(char_code)
            i += 7
    
    return message


def demodulate(samples):
    # Multiply the signal by its conjugate to obtain power
    power = np.abs(samples) ** 2

    # Integrate over each symbol period to obtain symbol value
    symbols = np.zeros(len(samples) // samples_per_symbol, dtype=np.int8)
    for i in range(len(symbols)):
        symbol_start = i * samples_per_symbol
        symbol_end = symbol_start + samples_per_symbol
        symbols[i] = np.mean(power[symbol_start:symbol_end]) > np.mean(power) * 0.5

    # Remove any leading zeros
    leading_zeros = 0
    for i in range(len(symbols)):
        if symbols[i] == 1:
            break
        leading_zeros += 1
    symbols = symbols[leading_zeros:]

    # Remove any trailing zeros
    trailing_zeros = 0
    for i in range(len(symbols)-1, -1, -1):
        if symbols[i] == 1:
            break
        trailing_zeros += 1
    symbols = symbols[:-trailing_zeros] if trailing_zeros > 0 else symbols

    return symbols


# Main loop
while True:
    # Receive IQ samples from SDR
    iq_samples = receive()

    # Demodulate signal
    symbols = demodulate(iq_samples)

    # Convert symbols to bits
    bits = ''.join(map(str, symbols))

    # Decode POCSAG message
    message = decode_pocsag(bits)
    
    if len(message) > 0:
        print("Recived Message:", message)

