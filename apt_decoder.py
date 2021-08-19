# derived from the base code at :
# https://medium.com/swlh/decoding-noaa-satellite-images-using-50-lines-of-code3c5d1d0a08da
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
from PIL import Image
import sys


# hilbert transform definition to get the amplitude envelope of the data
def hilbert(data_sample):
    analytical_signal = signal.hilbert(data_sample)
    amplitude_envelope = np.abs(analytical_signal)
    return amplitude_envelope


# set sampling frequency and get data from input .wav file
input_file_name = sys.argv[1]
fs, data = wav.read(f'wav/{input_file_name}')
data_am = hilbert(data)  # get the amplitude envelope of data signal

frame_width = int(0.5 * fs)
w, h = frame_width, data_am.shape[0] // frame_width
image = Image.new('RGB', (w, h))

px, py = 0, 0
for p in range(data_am.shape[0]):
    lum = int(data_am[p] // 32 - 32)
    if lum < 0:
        lum = 0
    if lum > 255:
        lum = 255
    image.putpixel((px, py), (lum, lum, lum))
    px += 1
    if px >= w:
        px = 0
        py += 1
        if py >= h:
            break

print(f"Finished. Image saved in output/{input_file_name[:-4]}.jpg")
image = image.resize((w, h))
image.save(f"output/{input_file_name[:-4]}.jpg")
