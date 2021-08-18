# Simple-APT
A simple python script that encodes/decodes pictures using automatic picture transmission (APT). My ultimate goal is to make a user-friendly program with GUI that will encode and decode pictures. I think it would also be fun to add the ability of reading the audio signal from an SDR and doing the processing in real time (something along the lines of WxtoImg/SDR software)

About the scripts:
pgm-convert-and-resize.py takes common image file extensions (.jpg, .png, more coming soon) and resizes them to meet NOAA standard width of 909 pixels, while keeping the image's aspect ratio. After resizing, the image is saved into a file with the .pgm extension and formatted to meet the standard for PNM P2 (perhaps naively, but it works great for my purposes).

apt-encoder.py takes the .pgm images and converts them into .wav files. Sync lines, spaces and telemetry are added.

apt-decoder.py takes an input .wav file that holds the apt encoded data, decodes it using a Hilbert transform and displays the encoded picture. The next few goals for this script is to make it more robust, run faster and straighten the pictures using the syncs. Adding false color, image enhancements and cropping are also possibilities. This is the resourse that I used to build this:
https://medium.com/swlh/decoding-noaa-satellite-images-using-50-lines-of-code-3c5d1d0a08da


Used packages/versions:
Python 3.9
numpy-1.21.1
Pillow-8.3.1
scipy-1.7.1
matplotlib-3.4.3
