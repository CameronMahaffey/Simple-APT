import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

# Set wave parameters and initialize some global empty lists.
carrier_hz = 2400      # NOAA specified AM carrier frequency
apt_width = 909        # NOAA specified image width
baud_rate = 4160       # NOAA APT baud rate (2 rows per second)
stored_apt_pic = []    # List to store image pixels
audio_sample = []      # List to store modulated sample data

# Syncs for both image channels, as per the NOAA given standard
sync_a = "000011001100110011001100110011000000000"
sync_b = "000011100111001110011100111001110011100"

# Set up plot for display/testing purposes
plt.figure(figsize=(12, 4))
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.title("Signal")


# Return the pixel's position in the current row
def get_pixel_position(row, col):
    return col * apt_width + row


# Ensure that the file is a P2 .PGM, encoded in LF format (i.e. '\n' newline)
def image_load_and_check(file_name):
    image_file = open(file_name, 'r')
    get_line = image_file.readline()

    try:
        assert get_line[0] == 'P'
        assert get_line[1] == '2'
        assert get_line[2] == '\n'
    except AssertionError:
        print('Error. Must be a P2 PGM file. Make sure the file is properly encoded in \'LF\' format')
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
    image_file.readline()
    image_file = np.array(image_file.read().split('\n'))
    return image_file


# Start of the program, load image and make sure it is properly formatted for encoding
the_pgm_image = image_load_and_check('input/IMG_0277.pgm')  # replace w/ sys.argv[1] when done
image_height = the_pgm_image.size // apt_width

# Main loop, sending both pictures and sync/telemetry 1 row at a time, till the height of the picture as been reached.
for rows in range(image_height):
    image_frame_line = rows % 128

    # Sync A
    for index in sync_a:
        if index == '0':
            stored_apt_pic.append(0)
        else:
            stored_apt_pic.append(255)

    # Space A
    for index in range(47):
        stored_apt_pic.append(0)

    # Image A
    for index in range(apt_width):
        if rows < image_height:
            stored_apt_pic.append(the_pgm_image[get_pixel_position(index, rows)])
        else:
            stored_apt_pic.append(0)

    # Telemetry A
    for index in range(45):
        wedge = image_frame_line / 8
        v = 0
        if wedge < 8:
            wedge += 1
            v = int(255.0 * (wedge % 8 / 8.0))
        stored_apt_pic.append(v)

    # Sync B
    for index in sync_b:
        if index == '0':
            stored_apt_pic.append(0)
        else:
            stored_apt_pic.append(255)

    # Space B
    for index in range(47):
        stored_apt_pic.append(255)

    # Image B
    for index in range(apt_width):
        if rows < image_height:
            stored_apt_pic.append(the_pgm_image[get_pixel_position(index, rows)])
        else:
            stored_apt_pic.append(0)

    # Telemetry B
    for index in range(45):
        wedge = image_frame_line / 8
        v = 0
        if wedge < 8:
            wedge += 1
            v = int(255.0 * (wedge % 8 / 8.0))
        stored_apt_pic.append(v)

stored_apt_pic = np.float64(stored_apt_pic)

# Create the sine carrier sampling array with a length equal to the image array (total pixels)
sine_carrier = np.sin(carrier_hz * 2.0 * np.pi * np.arange(len(stored_apt_pic)) / baud_rate)

# Modulate audio sample, store in 16bit np array, multiply pixels by factor between 32-64
audio_sample = np.int16(sine_carrier * stored_apt_pic * 42)

# Plot 2 cycles of modulated data
plt.plot(audio_sample[:4160])
plt.show()

# Save the encoded data into a .wav file
wav.write('wav/IMG_0277.wav', baud_rate, audio_sample)

# # Check out the finished picture as a .pgm
# new_pgm_file = open("pics/example-pgm.pgm", "w+")
# new_pgm_file.write("P2\n# apt pre-modulated image \n%d %d\n255\n" % (2080, 1606))
#
# for pixel in stored_apt_pic:
#     new_pgm_file.write(str(pixel) + '\n')
# new_pgm_file.close()
