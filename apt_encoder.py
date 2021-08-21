import numpy as np
import scipy.io.wavfile as wav
import pgm_convert_and_resize
import sys

# Set wave parameters and initialize some global empty lists.
carrier_hz = 2400      # NOAA specified AM carrier frequency
apt_width = 909        # NOAA specified image width
baud_rate = 4160       # NOAA APT baud rate (2 rows per second)
stored_apt_pic = []    # List to store image pixels
audio_sample = []      # List to store modulated sample data

# Syncs for both image channels, as per the NOAA given standard
sync_a = "000011001100110011001100110011000000000"
sync_b = "000011100111001110011100111001110011100"


# Return the pixel's position in the current row
def get_pixel_position(row, col):
    return col * apt_width + row


# Start of the program, load image arg and send to converter to make sure it is pgm p2, 909 pixels wide
input_file_name = sys.argv[1]
output_file_name = sys.argv[2]
the_pgm_image, image_height = pgm_convert_and_resize.converter(input_file_name)
# the_pgm_image = np.int16(the_pgm_image)
# print(f"the pgm image = {the_pgm_image}")
# print(f"image_height = {image_height}")
# print("APT encoding started..")

# Main loop, sending both pictures and sync/telemetry 1 row at a time, till the height of the picture as been reached.
for rows in range(image_height):
    image_frame_line = rows % 128   # telemetry reset every 128 rows

    # Sync A
    for index in sync_a:
        if index == '0':
            stored_apt_pic.append(255)
        else:
            stored_apt_pic.append(0)

    # Space A
    for index in range(47):
        if rows % 120 == 0:
            stored_apt_pic.append(255)
        else:
            stored_apt_pic.append(0)

    # Image A
    for index in range(apt_width):
        stored_apt_pic.append(the_pgm_image[get_pixel_position(index, rows)])

    # Telemetry A
    for index in range(45):
        wedge = image_frame_line // 8
        v = 0
        if wedge < 8:
            wedge += 1
            v = int(255.0 * (wedge % 8 / 8.0))
        stored_apt_pic.append(v)

    # Sync B
    for index in sync_b:
        if index == '0':
            stored_apt_pic.append(255)
        else:
            stored_apt_pic.append(0)

    # Space B
    for index in range(47):
        if rows % 120 == 0:
            stored_apt_pic.append(0)
        else:
            stored_apt_pic.append(255)

    # Image B
    for index in range(apt_width):
        stored_apt_pic.append(the_pgm_image[get_pixel_position(index, rows)])

    # Telemetry B
    for index in range(45):
        wedge = image_frame_line // 8
        v = 0
        if wedge < 8:
            wedge += 1
            v = int(255.0 * (wedge % 8 / 8.0))
        stored_apt_pic.append(v)

stored_apt_pic = np.float64(stored_apt_pic)
# print(f'stored_apt_pic: {stored_apt_pic}')

# Create the sine carrier sampling array with a length equal to the image array (total pixels)
sine_carrier = np.sin(carrier_hz * 2.0 * np.pi * np.arange(len(stored_apt_pic)) / baud_rate)

# Modulate audio sample, store in 16bit np array, multiply pixels by factor between 32-64
audio_sample = np.int16(sine_carrier * stored_apt_pic * 48)

# Save the encoded data into a .wav file
wav.write(output_file_name, baud_rate, audio_sample)
print(f"Finished, .wav file saved in {output_file_name}")
