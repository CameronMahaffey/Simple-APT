# Simple-APT
A simple python script that encodes/decodes pictures using automatic picture transmission (APT).

About the scripts:
pgm-convert-and-resize.py takes common image file extensions (.jpg, .png, more coming soon) and resizes them to meet NOAA standard width of 909 pixels, while keeping the image's aspect ratio. After resizing, the image is saved into a file with the .pgm extension and formatted to meet the standard for PNM P2 (perhaps naively, but it works great for my purposes).

apt-encoder.py coming soon, to take the .pgm images and convert them into .raw files, then into .wav files. Adding sync lines and telemetry. In the mean-time, i've been using this github as it has a nice encoder coded in C++ that I've been using to study:
https://github.com/gkbrk/apt-encoder

apt-decoder.py takes an input .wav file that holds the apt encoded data, decodes it using a Hilbert transform and displays the encoded picture. The next few goals for this script is to make it more user-friendly, run faster and straighten the pictures using the syncs. Adding false color, image enhancements and cropping are also possibilities.
