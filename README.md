# Simple-APT 
A simple python project that encodes/decodes pictures using automatic picture transmission (APT). My ultimate goal is to make a user-friendly program with GUI that will encode and decode pictures. I think it would also be fun to add the ability of reading the audio signal from an SDR and doing the processing in real time (something along the lines of WxtoImg/SDR software).

# Usage:
Type 'python apt\_encoder.py {filename}.ext' with the intended image placed in the input folder

  ex. python apt\_encoder.py png\_example.png
 
Type 'python apt\_decoder.py {filename}.wav' with the intended .wav file in the wav folder. File is placed here automatically if encoded with apt\_encoder.py

  ex. python apt\_decoder.py png\_example.wav
  
The resulting decoded image will be in the output folder, under the name 'output/{filename}.jpg

  ex. output/png\_example.jpg

# Directory Contents:
Simple-APT

  input -- the directory to place the pictures to be encoded, the input directory for apt_encoder.py. A temp .pgm file is stored in here during processing.
  
  output -- the directory that apt_decoder.py will use to place the decoded images
  
  wav -- the directory where .wav files are stored, the output files from apt\_encoder.py and the input files for apt\_decoder.py (aka the intermediate directory)
  
  apt\_decoder -- decode script
  
  apt\_encoder -- encode script
  
  pgm\_convert\_and\_resize -- script to resize images and convert into .pgm files
  
  
If using PyCharm, it might be necessary to add \_\_init\_\_.py in the Simple-APT directory for the IDE to recognize that you want to include the parent directory in the search for modules, since pgm_convert_and_resize.py is imported as a module in apt_encoder.py

# About the scripts:

pgm\_convert\_and\_resize.py takes common image file extensions (.jpg, .png, more coming soon) and resizes them to meet NOAA standard width of 909 pixels, while keeping the image's aspect ratio. After resizing, the image is saved into a file with the .pgm extension and formatted to meet the standard for PNM P2 (perhaps naively, but it works great for this purpose). A temporary .pgm file, named \_created\_by\_temp\_converter.py, is saved in the input folder when a non .pgm file is ran through apt\_encoder.py

apt\_encoder.py takes the .pgm images and converts them into .wav files. Sync lines, spaces and telemetry are added to the images. Currently, only pictures imported as .jpg and .png will be resized and converted into .pgm files, so it is advised to use these for now. Using .pgm files is fine, just make sure to resize them to a width of 909 pixels prior to feeding them into the script - it will throw an error. Plans are to add resizing capabilities for .pgm images as well and be script should be able to eventually handle all image formats supported by Pillow.

apt\_decoder.py takes an input .wav file that holds the apt encoded data, decodes it using a Hilbert transform, then saves the decoded picture as a .jpg in the output folder. The next few goals for this script is to make it more robust, run faster and straighten the pictures using the syncs. Adding false color, image enhancements and cropping soon.


# Used packages/versions:
Python 3.9

numpy-1.21.1

Pillow-8.3.1

scipy-1.7.1
