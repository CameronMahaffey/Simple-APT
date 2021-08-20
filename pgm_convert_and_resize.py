# pgm_convert_and_resize.py is a script for converting image types supported by PIL into their .pgm ascii
# counterparts, as well as resizing the image to have a width of 909 and keeping the aspect ratio.
# Its main purpose will be to feed NOAA-APT style images into an encoder program.
from PIL import Image
import numpy as np


def converter(image):
    # Open image, convert to greyscale, check width and resize if necessary
    im = Image.open(f'input/{image}')
    im = im.convert("L")
    image_width, image_height = im.size
    # image_array = np.array(im)
    print(f"Size: {im.size}")      # Mode: {im.mode}")
    # im.show()
    if image_width != 909:
        print("Resizing to width of 909 keeping aspect ratio...")
        new_width = 909
        ratio = (new_width / float(image_width))
        new_height = int((float(image_height) * float(ratio)))
        im = im.resize((new_width, new_height))
        print(f"New Size: {im.size}")

    # Save image data in a numpy array and make it 1D.
    image_array1 = np.array(im).ravel()
    # print(f"Picture Array: {image_array1}")

    print(f"Saving as PGM...")
    # Create file w .pgm ext to store data in, first 4 lines are: pgm type, comment, image size, maxVal
    new_pgm_file = open("input/_created_by_temp_converter.pgm", "w+")
    new_pgm_file.write("P2\n# created by pgm_convert_and_resize.py \n%d %d\n255\n" % im.size)

    # Storing greyscale data in file with \n delimiter
    for number in image_array1:
        new_pgm_file.write(str(number) + '\n')
    new_pgm_file.close()
    # im = im.save(r"pics/IMG_0277-greyscale.jpg")

    # replacement strings
    windows_line_ending = b'\r\n'
    unix_line_ending = b'\n'

    # small code snippet that changes a Windows encoded text file into a Unix encoded one, or nothing if not.
    with open('input/_created_by_temp_converter.pgm', 'rb') as new_pgm_file:
        content = new_pgm_file.read()

    content = content.replace(windows_line_ending, unix_line_ending)

    with open('input/_created_by_temp_converter.pgm', 'wb') as new_pgm_file:
        new_pgm_file.write(content)
    new_pgm_file.close()
    print(f"Finished")
