# pgm-convert-and-resize.py is a script for converting image types supported by PIL into their .pgm ascii
# counterparts, as well as resizing the image to have a width of 909 and keeping the aspect ratio.
# Its main purpose will be to feed NOAA-APT style images into an encoder program.
from PIL import Image
import numpy as np

# Open image, convert to greyscale, check width and resize if necessary
im = Image.open(r"pics/IMG_0277.JPG").convert("L")

# image_array = np.array(im)
# print(f"Original 2D Picture Array:\n{image_array}")  # data is stored differently depending on im.mode (RGB vs L vs P)
print(f"Size: {im.size}")      # Mode: {im.mode}")
# im.show()
if im.size != 909:
    print("Resizing to width of 909 keeping aspect ratio...")
    image_width = 909
    wpercent = (image_width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((image_width, hsize))
    image_width, image_height = im.size
    print(f"New Size: {im.size}")

# Save image data in a numpy array and make it 1D.
image_array1 = np.array(im).ravel()
# print(f"Picture Array: {image_array1}")

print(f"Saving as PGM...")
# Create file w .pgm ext to store data in, first 4 lines are: pgm type, comment, image size, maxVal (=black, 0=white)
new_pgm_file = open("pics/output-pgm.pgm", "w+")
new_pgm_file.write("P2\n# Created by pgm-convert-and-resize.py \n%d %d\n255\n" % im.size)

# Storing greyscale data in file with \n delimiter
for number in image_array1:
    new_pgm_file.write(str(number) + '\n')
new_pgm_file.close()
# im = im.save(r"pics/IMG_0277-greyscale.jpg")

# replacement strings
WINDOWS_LINE_ENDING = b'\r\n'
UNIX_LINE_ENDING = b'\n'

# small code snippet that changes a Windows encoded text file into a Unix encoded one, or nothing if not.
with open('pics/output-pgm.pgm', 'rb') as new_pgm_file:
    content = new_pgm_file.read()

content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

with open('pics/output-pgm.pgm', 'wb') as new_pgm_file:
    new_pgm_file.write(content)
new_pgm_file.close()
print(f"Finished")
