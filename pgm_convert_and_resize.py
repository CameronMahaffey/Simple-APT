# pgm_convert_and_resize.py is a script for converting image types supported by PIL into their .pgm ascii
# counterparts, as well as resizing the image to have a width of 909 and keeping the aspect ratio.
# Its main purpose will be to feed NOAA-APT style images into an encoder program.
from PIL import Image
import numpy as np


# Ensure that the file is a P2 .PGM, encoded in LF format (i.e. '\n' newline)
def image_check(image_file):
    # print(image_file)
    get_line = image_file.readline()

    try:
        assert get_line[0] == 'P'
        assert get_line[1] == '2'
        assert get_line[2] == '\n'
    except AssertionError:
        print('Error. Must be a \'P2\' PGM file. Make sure the file is properly encoded in \'LF\' format')
        quit()

    get_line = image_file.readline()  # skip comments
    while get_line[0] == '#':
        get_line = image_file.readline()

    try:
        assert get_line[0] == '9'
        assert get_line[1] == '0'
        assert get_line[2] == '9'
    except AssertionError:
        print('Error. Image must have a width of 909 pixels.')
        quit()
    image_height = int(get_line[3:])
    image_file.readline()
    image_file = np.array(image_file.read().split('\n'))
    print(image_file)
    return image_file, image_height


def converter(image_file_path):
    image_width = 0
    image_height = 0
    im = None
    # Open image, convert to greyscale, check width and resize if necessary
    if image_file_path.lower().endswith(('.png', '.jpg')):
        print("Not a PGM, converting...")
        im = Image.open(f'{image_file_path}')
        im = im.convert("L")
        image_width, image_height = im.size
    elif image_file_path.lower().endswith('.pgm'):
        print("PGM file, no conversion needed.")
        return image_check(open(f'{image_file_path}'))
    else:
        print("Error. Image must be a .pgm, .png, or .jpg extension")
        quit()
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
    image_width, image_height = im.size
    # Save image data in a numpy array and make it 1D.
    image_array1 = np.array(im).ravel()
    # print(f"Picture Array: {image_array1} size: {image_array1.size}")

    print(f"Converting to PGM...")
    new_pgm_file = []

    # Storing greyscale data in array with \n delimiter
    for number in image_array1:
        new_pgm_file.append(number)
    print("Finished conversion")

    return new_pgm_file, image_height
