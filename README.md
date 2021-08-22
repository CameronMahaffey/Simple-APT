# Simple-APT 
A simple python project that encodes/decodes pictures using automatic picture transmission (APT). The ultimate goal was to create a user-friendly program that allows the user to quickly encode/decode pictures, as well as create a visually appealing GUI with added functionality. The scripts are far from perfect, but they do a good job of showing the APT process.

# About the GUI
The GUI was created with the built-in python module "Tkinter". There are three tabs: encoder, decoder and program output. The encoder tab contains browse buttons that allow the user to select input and output files for the encoder script. The input file must be an image extension of .png, .jpg, or .pgm (P2) and the output file must be a .wav file. A preview of the selected input image will be placed in the image frame of the encoder tab. As an added bonus, you can use the browse left and right buttons ("<<" and ">>") to view all images that are in the selected images directory. After deciding on an image to encode into a .wav file, select an output file with the other browse button (or type the filepaths in the respective entry boxes.) Click on the 'encode' button and the .wav file will be saved. The plot on the right hand side will update with a small sample that shows the amplitude modulated waveform. Click on the 'send to decoder' button to conveniently send the filepath to the input entry box of the decoder tab. The decoder tab has the same format as the encoder tab, but in reverse. A .wav filepath placed into the input entry box will update the graph with the same sample as before, but this time it also shows the hilbert transform of the signal. This is a good visualization of how amplitude modulation works for encoding/decoding images to send/receive as a waveform. There are play/stop buttons to listen to the .wav file listed in the input entry box of the decoder tab. The program output tab has a read-only text box where all program output and errors are piped.

# Usage:
Simply type 'python gui.py' to run the program, or you can use the scripts via the command line in the manner seen below.

Type 'python apt\_encoder.py {input_filename}.ext {output_filename}.wav' with the intended input/output in the Simple-APT directory, or add the absolute file paths instead

  ex. python apt\_encoder.py input\png\_example.png wav\png\_example.wav           or              python apt\_encoder C:\....png\_example\_.png C:\....png\_example\_.wav
 
Type 'python apt\_decoder.py {filename}.wav' with the intended .wav file in the wav folder. File is placed here automatically if encoded with apt\_encoder.py

  ex. python apt\_decoder.py wav\png\_example.wav output\png\_example.png          or              python apt\_decoder C:\....png\_example\_.wav C:\....png\_example\_.jpg
  
In the above example, the resulting decoded image will be in the output folder, under the name 'output/{filename}.jpg, or whichever absolute filepath you selected. Careful not to overwrite the input image wih the decoded image you create.

  ex. output/png\_example.jpg 

# Directory Contents:
Simple-APT

  input -- the directory to place the pictures to be encoded, the input directory for apt_encoder.py. A temp .pgm file is stored in here during processing.
  
  output -- the directory that apt_decoder.py will use to place the decoded images
  
  misc -- holds initial images for the GUI runs for the first time
  
  wav -- an intermediate directory to store the .wav files, which are the output files from apt\_encoder.py and the input files for apt\_decoder.py
  
  apt\_decoder -- decode script
  
  apt\_encoder -- encode script
  
  gui.py -- Tkinter GUI that allows for simple encoding/decoding and visualization
  
  pgm\_convert\_and\_resize -- script to resize images and convert into .pgm files
  
  
Add \_\_init\_\_.py in the Simple-APT directory for the IDE to recognize that you want to include the parent directory in the search for modules, since pgm_convert_and_resize.py is imported as a module in apt_encoder.py, or just edit the encoder script to include the pgm_convert_and_resize code.

# About the scripts:

pgm\_convert\_and\_resize.py takes common image file extensions (.jpg, .png, more coming soon) and resizes them to meet NOAA standard width of 909 pixels, while keeping the image's aspect ratio. After resizing, the image is saved into a file with the .pgm extension and formatted to meet the standard for PNM P2.

apt\_encoder.py takes the .pgm images and converts them into .wav files. Sync lines, spaces and telemetry are added to the images. Currently, only pictures imported as .jpg and .png will be resized and converted into .pgm files, so it is advised to use these for now. Using .pgm files is fine, just make sure to resize them to a width of 909 pixels prior to feeding them into the script - it will throw an error. Plans are to add resizing capabilities for .pgm images as well and be script should be able to eventually handle most image formats supported by Pillow.

apt\_decoder.py takes an input .wav file that holds the apt encoded data, decodes it using a Hilbert transform, then saves the decoded picture as a .jpg in the selected output folder. The next few goals for this script are to make it more robust and straighten the pictures using the syncs.


# Used packages/versions:
Python 3.9
pip freeze - 
    cycler==0.10.0
    kiwisolver==1.3.1
    matplotlib==3.4.3
    numpy==1.21.1
    Pillow==8.3.1
    pyparsing==2.4.7
    python-dateutil==2.8.2
    scipy==1.7.1
    six==1.16.0

