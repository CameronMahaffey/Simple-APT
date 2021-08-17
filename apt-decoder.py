# derived from the base code at :
# https://medium.com/swlh/decoding-noaa-satellite-images-using-50-lines-of-code3c5d1d0a08da

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
from PIL import Image


# set sampling frequency and get data from input .wav file
fs, data = wav.read('wav/my-apt.wav')
print(f"sample rate = {fs}")
# print(f"data sample = {data[60 * fs:61 * fs]}")
print(f"data sample = {data[10 * fs:11 * fs]}")
mini = min(data)
maxi = max(data)
# theRange = maxi - mini
print(f"min in set = {mini}")
print(f"max in set = {maxi}")
# print(f"the range  = {theRange}")

# set up the plot
plt.figure(figsize=(12, 4))
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.title("Signal")

# resample the data to make program run faster, change resample to 1 for max quality (affects image dimensions)
resample = 4
data = data[::resample]
fs = fs // resample

# uncomment when using 8-bit
#for x in range(data.shape[0]):
#    percentage = (data[x] - mini) / theRange
#    data[x] = (255 * percentage)


# hilbert transform definition to get the amplitude envelope of the data
def hilbert(data_sample):
    analytical_signal = signal.hilbert(data_sample)
    amplitude_envelope = np.abs(analytical_signal)
    return amplitude_envelope


data_crop = data[60 * fs:61 * fs]  # crop the data to show one period, for plot
data_am = hilbert(data)  # amplitude envelope of data signal
data_am_crop = hilbert(data_crop)  # cropped amplitude envelope of data signal, for plotting purposes

# plot the cropped data and cropped AM data in the same figure and show
plt.plot(data_crop)
plt.plot(data_am_crop)
plt.show()

frame_width = int(0.5 * fs)
w, h = frame_width, data_am.shape[0] // frame_width
image = Image.new('RGB', (w, h))

px, py = 0, 0
for p in range(data_am.shape[0]):
    lum = int(data_am[p] // 32 - 32)
    # print(f"lum = {lum}")
    if lum < 0:
        lum = 0
    if lum > 255:
        lum = 255
    image.putpixel((px, py), (lum, lum, lum))
    px += 1
    if px >= w:
        if (py % 50) == 0:
            print(f"Line saved {py} of {h}")
        px = 0
        py += 1
        if py >= h:
            break

image = image.resize((2 * w, h))
image.save("output/my-apt.jpg")
plt.imshow(image)
plt.show()
