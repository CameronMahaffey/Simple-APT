from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter import colorchooser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import ImageTk, Image, ImageOps, ImageFilter, ImageColor
from pygame import mixer
from pathlib import Path
from random import randint
import subprocess
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import sys


# Define a custom navigation toolbar for the plots
class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self,canvas_,parent_):
        self.toolitems = (
            ('Home', 'Reset View', 'home', 'home'),
            ('Back', 'Back', 'back', 'back'),
            ('Forward', 'Forward', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan', 'move', 'pan'),
            ('Zoom', 'Zoom', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Save', 'Save Figure', 'filesave', 'save_figure')
        )
        NavigationToolbar2Tk.__init__(self, canvas_, parent_)


# Function to add false color to a greyscale image
def false_color(image_to_change):
    global rgby_list
    colors = rgby_list
    if image_to_change.mode not in ['L', 'RGB']:
        raise TypeError('Unsupported source image mode: {}'.format(image_to_change.mode))
    image_to_change.load()
    print(image_to_change.mode)

    # Create look-up-tables (luts) to map luminosity ranges to components
    # of the colors given in the color palette.
    num_colors = len(colors)
    palette = [colors[int(i / 256. * num_colors)] for i in range(256)]
    luts = (tuple(c[0] for c in palette) +
            tuple(c[1] for c in palette) +
            tuple(c[2] for c in palette))


    grey_scale = image_to_change

    # Convert grayscale to an equivalent RGB mode image.
    if Image.getmodebands(image_to_change.mode) < 4:  # Non-alpha image?
        merge_args = ('RGB', (grey_scale, grey_scale, grey_scale))  # RGB version of grayscale.

    else:  # Include copy of src image's alpha layer.
        a = Image.new('L', image_to_change.size)
        a.putdata(image_to_change.getdata(3))
        luts += tuple(range(256))  # Add a 1:1 mapping for alpha values.
        merge_args = ('RGBA', (grey_scale, grey_scale, grey_scale, a))  # RGBA version of grayscale.

    # Merge all the grayscale bands back together and apply the luts to it.
    return Image.merge(*merge_args).point(luts)


# Function that will be invoked when the color wheel button is clicked
def choose_color():
    global dec_image
    if check_var.get() == 0:
        print("Check 'False Color'")
    else:
        color_red = colorchooser.askcolor(title ="Choose RED")
        color_green = colorchooser.askcolor(title="Choose GREEN")
        color_blue = colorchooser.askcolor(title="Choose BLUE")
        color_red = color_red[1].lstrip('#')
        color_red = [color_red[0:2], color_red[2:4], color_red[4:6]]
        color_red = [int(i, 16) for i in color_red]
        color_green = color_green[1].lstrip('#')
        color_green = [color_green[0:2], color_green[2:4], color_green[4:6]]
        color_green = [int(i, 16) for i in color_green]
        color_blue = color_blue[1].lstrip('#')
        color_blue = [color_blue[0:2], color_blue[2:4], color_blue[4:6]]
        color_blue = [int(i, 16) for i in color_blue]
        change_colors((color_red, color_green, color_blue,))

        image_to_color = (ImageTk.getimage(new_dec_image[0])).convert('L')
        colored_image = false_color(image_to_color)
        colored_image = ImageTk.PhotoImage(colored_image)

        new_dec_image[2] = colored_image

        # reload processed image in the frame
        dec_image.grid_forget()
        dec_image = Label(dec_image_frame, image=new_dec_image[2], padx=10, pady=10, relief=SUNKEN)
        dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


def pre_color_cycle():
    global start_color_cycle_btn
    start_color_cycle_btn.config(state=DISABLED)
    print("Starting color cycle!")
    color_cycle()


def stop_color_cycle():
    global timer_id
    global start_color_cycle_btn
    start_color_cycle_btn.config(state=ACTIVE)
    root.after_cancel(timer_id)


# Cycle through all colors
def color_cycle():
    global rgby_list
    global dec_image
    global timer_id
    global count_up
    timer_id = root.after(50, color_cycle)

    change_amt = 30

    # lazy coded algorithm for full color spectrum
    for i in range(2):
        red = rgby_list[i][0]
        green = rgby_list[i][1]
        blue = rgby_list[i][2]

        if count_up:
            if red == 0 and green == 0 and blue <= 255:
                blue += change_amt
                if blue >= 255:
                    blue = 255
                    green += change_amt
            elif red == 0 and green <= 255 and blue == 255:
                green += change_amt
                if green >= 255:
                    green = 255
                    blue -= change_amt
            elif red == 0 and green == 255 and blue <= 255:
                blue -= change_amt
                if blue <= 0:
                    blue = 0
                    red += change_amt
            elif red <= 255 and green == 255 and blue == 0:
                red += change_amt
                if red >= 255:
                    red = 255
                    green -= change_amt
            elif red == 255 and green <= 255 and blue == 0:
                green -= change_amt
                if green <= 0:
                    green = 0
                    blue += change_amt
            elif red == 255 and green == 0 and blue <= 255:
                blue += change_amt
                if blue >= 255:
                    blue = 255
                    green += change_amt
            elif red == 255 and green <= 255 and blue == 255:
                green += change_amt
                if green >= 255:
                    green = 255
                    blue -= change_amt
                    count_up = False
        else:
            if red == 255 and green == 255 and blue <= 255:
                blue -= change_amt
                if blue <= 0:
                    blue = 0
                    green -= change_amt
            elif red == 255 and green <= 255 and blue == 0:
                green -= change_amt
                if green <= 0:
                    green = 0
                    blue += change_amt
            elif red == 255 and green == 0 and blue <= 255:
                blue += change_amt
                if blue >= 255:
                    blue = 255
                    red -= change_amt
            elif red <= 255 and green == 0 and blue == 255:
                red -= change_amt
                if red <= 0:
                    red = 0
                    green += change_amt
            elif red == 0 and green <= 255 and blue == 255:
                green += change_amt
                if green >= 255:
                    green = 255
                    blue -= change_amt
            elif red == 0 and green == 255 and blue <= 255:
                blue -= change_amt
                if blue <= 0:
                    blue = 0
                    green -= change_amt
            elif red == 0 and green <= 255 and blue == 0:
                green -= change_amt
                if green <= 0:
                    green = 0
                    blue += change_amt
                    count_up = True

        rgby_list[i] = [red, green, blue]

    # run false color function
    image_to_cycle = ImageTk.getimage(new_dec_image[0])
    image_to_cycle = image_to_cycle.convert('L')
    colored_image = false_color(image_to_cycle)
    new_dec_image[2] = ImageTk.PhotoImage(colored_image)

    # Update dec image
    dec_image.grid_forget()
    dec_image = Label(dec_image_frame, image=new_dec_image[2], padx=10, pady=10, relief=SUNKEN)
    dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)



# Function to switch between original and colored decoder image
def switch_between():
    global dec_image

    dec_image.grid_forget()
    rb2.set("Original")
    if check_var.get():
        dec_image = Label(dec_image_frame, image=new_dec_image[2], padx=10, pady=10, relief=SUNKEN)
    else:
        dec_image = Label(dec_image_frame, image=new_dec_image[0], padx=10, pady=10, relief=SUNKEN)

    dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


# Get the current index of the image
def get_current_image_index():
    global current_image_index
    return current_image_index


# Set the current index of the image
def set_current_image_index(index):
    global current_image_index
    current_image_index = index


# Resize to fit the screen better, keep aspect ratio
def resize_to_fit(image):
    image_width, image_height = image.size
    if image_height >= 500:
        new_height = 400
        ratio = (new_height / float(image_height))
        new_width = int((float(image_width) * float(ratio)))
        image = image.resize((new_width, new_height))
    while image_width >= 900:
        image_width, image_height = image.size
        image = image.resize((image_width * 3 // 4, image_height * 3 // 4))
    return image


# Update the plots with samples from the given wav file
def update_graph(which_plot):
    global enc_canvas
    global dec_canvas
    global wav_file
    global am_sample_data

    if which_plot == 1:
        baud, wav_file = wav.read(enc_entry_output_text.get())  # get the wav file from output of enc
        sample_data = wav_file[:4160]   # get some samples

        enc_subplot.clear()
        enc_subplot.set_title('Output WAV')
        enc_subplot.set_xlabel('Samples')
        enc_subplot.set_ylabel('Amplitude')
        enc_subplot.set_xticks(np.arange(0, 5200, 1040))
        enc_subplot.set_yticks(np.arange(min(sample_data) - 1000, max(sample_data) + 1000, 4000))

        enc_subplot.plot(sample_data, color=background_color, label="wav")
        enc_canvas.draw()
        enc_subplot.legend()
        print("Encoder Plot Updated")
    else:
        baud, wav_file = wav.read(dec_entry_input_text.get())  # get the wav file from input of dec
        sample_data = wav_file[:4160]  # get some samples
        am_sample_data = np.abs(signal.hilbert(wav_file))
        am_samples = am_sample_data[:4160]  # get some samples

        dec_subplot.clear()
        dec_subplot.set_title('Input WAV')
        dec_subplot.set_xlabel('Samples')
        dec_subplot.set_ylabel('Amplitude')
        dec_subplot.set_xticks(np.arange(0, 5200, 1040))
        dec_subplot.set_yticks(np.arange(min(sample_data) - 1000, max(sample_data) + 1000, 4000))

        dec_subplot.plot(sample_data, color=background_color, label="wav")
        dec_subplot.plot(am_samples, color="red", label="data")
        dec_canvas.draw()
        dec_subplot.legend()
        print("Decoder Plot Updated")


# Callback function for button press event inside figure
def mouse_clicked(event):
    # print(f"Mouse clicked")
    global dec_canvas
    global cid_pressed
    stop_plot()
    dec_canvas.mpl_disconnect(cid_pressed)
    cid_pressed = dec_canvas.mpl_connect('button_release_event', mouse_released)


# Callback function for button press event inside figure
def mouse_released(event):
    global dec_canvas
    global cid_pressed
    # print(f"Mouse released")

    dec_canvas.mpl_disconnect(cid_pressed)
    pre_run_plot(False)


# Function called that starts timer
def pre_run_plot(is_running):
    global dec_canvas
    global cid_pressed
    global running
    running = is_running
    if running:
        return
    running = True
    print("Running Plot.")
    cid_pressed = dec_canvas.mpl_connect('button_press_event', mouse_clicked)
    run_plot()


# Timer function that calls itself when updating graph
def run_plot():
    global dec_canvas
    global timer_on
    global plot_counter

    try:
        sample_data = wav_file[plot_counter:plot_counter + 4160]  # get some samples
        am_samples = am_sample_data[plot_counter:plot_counter + 4160]  # get some am samples

        plot_counter += graph_speed.get()

        dec_subplot.clear()
        dec_subplot.set_title('Input WAV')
        dec_subplot.set_xlabel('Samples')
        dec_subplot.set_ylabel('Amplitude')
        dec_subplot.set_xticks(np.arange(0, 5200, 1040))

        dec_subplot.plot(sample_data, color=background_color, label="wav")
        dec_subplot.plot(am_samples, color="red", label="data")
        dec_canvas.draw()
        dec_subplot.legend()
        # print("im updating every sec")
        timer_on = root.after(10, run_plot)
    except:
        print("Reached end of file.")
        stop_plot()
        plot_counter = 0


# Function to stop timer function, and thus stop updating graph
def stop_plot():
    global running
    global timer_on
    global dec_canvas
    global cid_pressed

    running = False
    root.after_cancel(timer_on)
    dec_canvas.mpl_disconnect(cid_pressed)
    print("Stopped Plot.")


# Create forward button command for browsing pictures
def forward(image_index):
    global button_forward
    global button_backward

    rb1.set("Nothing")
    print(f"Going one right to index {image_index}")
    set_current_image_index(image_index - 1)

    # Reset grid and re-place w/ new image
    update_enc_image(image_index - 1)
    button_forward = Button(encoder_tab, text=">>", command=lambda: forward(image_index + 1))
    button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index - 1))

    if image_index == len(encoder_image_list):
        button_forward = Button(encoder_tab, text=">>", state=DISABLED)

    button_backward.grid(row=1, column=0, padx=20, sticky=NW)
    button_forward.grid(row=1, column=0, padx=20, sticky=NE)


    enc_entry_input_text.set(enc_image_filepath_list[image_index - 1])

    update_status(f"Image {image_index} of {str(len(encoder_image_list))}")


# Create backward button command for browsing pictures
def backward(image_index):
    global button_forward
    global button_backward

    rb1.set("Nothing")
    print(f"Going one left to index {image_index}")
    set_current_image_index(image_index - 1)
    update_enc_image(image_index - 1)
    button_forward = Button(encoder_tab, text=">>", command=lambda: forward(image_index + 1))
    button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index - 1))

    if image_index <= 1:
        button_backward = Button(encoder_tab, text="<<", state=DISABLED)

    button_backward.grid(row=1, column=0, padx=20, sticky=NW)
    button_forward.grid(row=1, column=0, padx=20, sticky=NE)

    enc_entry_input_text.set(enc_image_filepath_list[image_index - 1])

    update_status(f"Image {str(image_index)} of {str(len(encoder_image_list))}")


# Define what happens when browse buttons are clicked
def browse_dir(tab, io):
    if tab == 1:  # encoder tab selected
        use_tab = encoder_tab
        if io == 1:
            use_entry = enc_entry_input_text
        else:
            use_entry = enc_entry_output_text
    else:
        use_tab = decoder_tab
        if io == 1:
            use_entry = dec_entry_input_text
        else:
            use_entry = dec_entry_output_text
    # Create file dialog box
    if io == 1:  # an input
        use_tab.filename = filedialog.askopenfilename(initialdir="/users/camer/PycharmProjects/Simple-APT",
                                                      title="Select a file",
                                                      filetypes=(("all files", "*.*"),
                                                                 ("png files", "*.png"),
                                                                 ("jpg files", "*.jpg"),
                                                                 ("jpeg files", "*.jpeg"),
                                                                 ("pgm files", "*.pgm"),
                                                                 ("wav files", "*.wav")
                                                                 ))
    else:
        use_tab.filename = filedialog.askopenfilename(initialdir="/users/camer/PycharmProjects/Simple-APT")
        # change to askdirectory
    use_entry.set(use_tab.filename)
    dir_path = use_tab.filename
    if use_tab.filename != '':  # user doesn't click exit or cancel
        if io == 1:
            if (tab == 1):  # only applies to input of encoder
                rb1.set("Nothing")    # reset the radio buttons
                check_if_loaded(dir_path)
            if (tab == 0):  # only applies to the input of decoder
                update_graph(tab)


# Create a new image list from dir contents when new image is selected from encoder input browse
def new_image_list(directory_path):
    global current_image_index  # didn't work with the function for some reason here
    flipped_filename = ''  # empty string to store file name
    for char in reversed(directory_path):
        # print(char)
        if char == '/' or char == '\\':  # sometimes filepaths are both ways
            break
        flipped_filename += char  # returns the file-name but flipped
        directory_path = directory_path.rstrip(char)  # remove 1 letter off the end until first '/' is found
    print(f'Selected image dir path: {directory_path}')  # now we have folder file path and the clicked image
    # print(f'flipped name: {flipped_filename}')
    clicked_image = flipped_filename[::-1]  # flips the file name, this was the clicked image
    print(f'Selected image: {clicked_image}\n')
    del encoder_image_list[:]  # clear image list to upload new batch   (to load new images into list and into frame)
    del enhanced_image_list[:]
    del enc_image_filename_list[:]  # clear image filename list    (for indexing purposes)
    del enc_image_filepath_list[:]  # clear the image filepath list (for entry box)
    current_image_index = 0  # reset the clicked image index
    print(f"All images in {directory_path}:")
    for file in Path(directory_path).glob('*.*'):  # search all contents in directory path
        image_file_path = str(file)
        if image_file_path.lower().endswith(('.jpg', '.png', '.pgm')):  # if a photo,
            print(image_file_path)
            enc_image_filepath_list.append(image_file_path)  # add the path to the filepath list
            enc_image_filename_list.append(image_file_path[len(directory_path):])  # add it to filename list
            if image_file_path.lower().endswith('.pgm'):
                pgm_array = open(image_file_path, 'r')  # open the .pgm file to create a preview image
                for i in range(4):  # remove first four lines of pgm
                    pgm_array.readline()
                pgm_array = pgm_array.read().split('\n')
                if pgm_array[len(pgm_array)-1] == '':  # if last character has a space dont include in list
                    pgm_array.pop()
                pgm_array = np.uint8(pgm_array)      # create a numpy array from .pgm contents
                try:
                    pgm_array = np.reshape(pgm_array, (pgm_array.size // 909, 909))  # make the array 2D
                    image = ImageTk.PhotoImage(resize_to_fit(Image.fromarray(pgm_array)))
                except:
                    print("Not able to preview .pgm that isn't 909 in width :(")
                    image = ImageTk.PhotoImage(resize_to_fit(Image.open("misc/pgm_placeholder.png")))
                # print(pgm_array)
            else:
                image = ImageTk.PhotoImage(resize_to_fit(Image.open(image_file_path)))  # add all images in order
            encoder_image_list.append(image)  # to the image_list
            enhanced_image_list.append(image) # make a copy for enhancement previewing
    print(f'\nAll images in selected dir: {enc_image_filename_list}')
    # print(f'All image filepaths: {enc_image_filepath_list}')
    for image_name in enc_image_filename_list:
        if image_name == clicked_image:
            current_image_index = enc_image_filename_list.index(image_name)
            print(f'Clicked image index: {current_image_index + 1}')
    update_enc_image(current_image_index)  # update the encoder image

    # Update the status bar
    update_status(f"Image {str(current_image_index + 1)} of {str(len(encoder_image_list))}")
    print(f"length of image list: {len(encoder_image_list)}\n")


# Check to see if the new contents to be loaded are actually the old contents, save time
def check_if_loaded(file_path):
    print(file_path)
    print(enc_image_filepath_list)
    file_path = file_path.replace('/', '\\')
    if file_path in enc_image_filepath_list:
        position_in_list = enc_image_filepath_list.index(file_path)
        print(f"Selected image and directory already loaded into memory.")
        update_status("Selected image and directory already loaded into memory.")
        set_current_image_index(position_in_list)
        update_enc_image(position_in_list)
    else:
        new_image_list(file_path)


# Function that is called when return is pressed in one of the entry input boxes
def entry_return_pressed(tab):
    # print("Enter Pressed.")
    if tab == 1:
        input_text = enc_entry_input_text.get()
        if input_text != '':
            check_if_loaded(input_text)
    else:
        input_text = dec_entry_input_text.get()
        if input_text != '':
            update_graph(0)


# Function called when the image in the encoder tab needs to be updated
def update_enc_image(index):
    global enc_image
    update_buttons(index)  #update buttons every time the enc_image is changed
    enc_image.grid_forget()

    if rb1.get() == "Nothing":
        used_image = encoder_image_list[index]
    else:
        used_image = enhanced_image_list[index]

    enc_image = Label(enc_image_frame, image=used_image, padx=10, pady=10, relief=SUNKEN)
    enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


# Function to update the browsing forward and backward buttons
def update_buttons(image_index):
    global button_forward
    global button_backward

    # Update the buttons depending on index of selected image
    if image_index == 0:
        button_backward = Button(encoder_tab,text="<<", command=backward, state=DISABLED)
        button_forward = Button(encoder_tab, text=">>", command=lambda: forward(2))
    elif image_index == (len(encoder_image_list) - 1):
        button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index))
        button_forward = Button(encoder_tab, text=">>", command=forward, state=DISABLED)
    else:
        button_forward = Button(encoder_tab, text=">>", command=lambda: forward(image_index + 2))
        button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index))

    button_backward.grid(row=1, column=0, padx=20, sticky=NW)
    button_forward.grid(row=1, column=0, padx=20, sticky=NE)


# Function to update the status bars at the bottom
def update_status(status_message):
    update_status = Label(encoder_tab, text=status_message,
                          bd=1, relief=SUNKEN, anchor=E, bg='light grey')
    update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


# Display the decoded image when decode button is pressed
def new_decoder_image(image_filepath):
    global dec_image
    del new_dec_image[:]
    the_new_image_LA = Image.open(image_filepath)  # open the image
    the_new_image = ImageTk.PhotoImage(resize_to_fit(the_new_image_LA))  # convert before append
    new_dec_image.append(the_new_image)  # add the new image
    new_dec_image.append(the_new_image)  # add copy for enhance preview
    the_new_image = the_new_image_LA.convert('L')  # now new image is 'L', for false color func
    the_new_image = false_color(the_new_image)  # get the colored version
    the_new_image = ImageTk.PhotoImage(resize_to_fit(the_new_image))  # convert before append
    new_dec_image.append(the_new_image)  # add the new colored image
    new_dec_image.append(the_new_image)  # add copy for enhance preview
    print(f"{new_dec_image[0]}, {new_dec_image[2]}, {len(new_dec_image)}")
    dec_image.grid_forget()
    dec_image = Label(dec_image_frame, image=new_dec_image[0], padx=10, pady=10, relief=SUNKEN)
    dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


# Reset Dec image function
def reset_dec_image():
    global rgby_list
    file_path = dec_entry_output_text.get()
    if file_path == '':
        print("Error. Insert file path in the browse box.")
    else:
        rgby_list = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]
        new_decoder_image(file_path)
        rb2.set("Original")
        check_var.set(0)

# Simple redirector function to make all stdout data go to the GUI
def sysout_redirector(input_str):
    read_only_textbox.insert(END, input_str)


# Define the functionality of the encode and decode buttons (runs scripts as subprocesses)
def popups(tab):
    if tab == 1:
        msg = messagebox.askyesno("Encode will overwrite file.", "Are you sure?")
        call_process = 'python apt_encoder.py'
        used_tab = encoder_tab
        output_entry_used = enc_entry_output_text
        input_file_path = 'temp.jpg'
    else:
        msg = messagebox.askyesno("Decode will overwrite file.", "Are you sure?")
        call_process = 'python apt_decoder.py'
        used_tab = decoder_tab
        output_entry_used = dec_entry_output_text
        input_file_path =  dec_entry_input_text.get()  # get filepath from decoder input box
    if msg == 1:
        # quit pygame mixer to get permission to .wav
        if mixer.get_init() is not None:
            mixer.quit()
        # save the temporary image into folder
        image_index = get_current_image_index()
        if rb1 == "Nothing":
            used_list = encoder_image_list
        else:
            used_list = enhanced_image_list
        save_this_image = used_list[image_index]  # get image to save
        save_this_image = ImageTk.getimage(save_this_image)  # convert into a PIL image for saving
        save_this_image = save_this_image.convert("RGB")
        save_this_image.save('temp.jpg', "JPEG")
        output_file_path = output_entry_used.get()
        # if empty, ask for a folder dialog to save and place it into output_entry_used.set()
        if output_file_path == '':
            ask_folder = filedialog.askdirectory() + '/'
            if ask_folder == '/':
                update_status("Action Cancelled.")
                print("Action Cancelled.")
                return
            print(f"Folder selected for save: {ask_folder}")
            image_index = get_current_image_index()
            if len(enc_image_filename_list) != 0:
                output_file_path = ask_folder + enc_image_filename_list[image_index]
            else:
                output_file_path = ask_folder + "placeholder_name.jpg"
            if tab == 1:
                output_file_path = output_file_path[:-4] + '.wav'
            output_entry_used.set(output_file_path)
        print(f"Calling process: {call_process} {input_file_path} {output_file_path}")
        call_to_process = subprocess.Popen(f"{call_process} {input_file_path} {output_file_path}",
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
        sysout_redirector(call_to_process.stdout.read())  # pipe stdout to program output tab

        delete_temp_file = Path("temp.jpg")
        delete_temp_file.unlink()

        mixer.init()  #re initialize mixer

        if output_file_path != '' and input_file_path != '':
            if tab == 0:
                new_decoder_image(output_file_path)
            else:
                update_graph(tab)

            # update the status of popup return status
            update_status(f"Success. File saved to {output_file_path}")
        else:
            update_status(f"Error. Check Filepath")
    else:
        update_status("Action Cancelled.")
        print("Action Cancelled.")


# Make simple playback/stop/pause functions with pygame module
def play_wav():
    global paused
    global pause_button
    paused = False
    pause_button.config(text="Pause")
    file_path = dec_entry_input_text.get()
    mixer.music.stop()  # just in case something is still playing
    mixer.music.load(file_path)
    mixer.music.play(loops=0)
    print("Playing wav.")


# Stop function
def stop_wav():
    global paused
    mixer.music.stop()  # just in case something is still playing
    paused = True
    print("Playback stopped.")


# Pause function
def pause_wav(is_paused):
    global paused
    global pause_button
    paused = is_paused
    if paused:
        pause_button.config(text="Pause")
        mixer.music.unpause()
        paused = False
        print("Playback unpaused.")
    else:
        pause_button.config(text="Resume")
        mixer.music.pause()
        paused = True
        print("Playback paused.")


# Function to send output of encoder to input of decoder
def send_to_decoder():
    dec_entry_input_text.set(enc_entry_output_text.get())
    if dec_entry_input_text.get() != '':  # not empty
        update_graph(0)   # update the decoder graph

        # update the status
        update_status("Sent to Decoder.")
        print("Sent to Decoder.")


# Function to rotate the images in the encoder tab
def rotate_image():
    image_index = get_current_image_index()
    print(f'Rotate image {image_index + 1}')
    image_to_rotate = encoder_image_list[image_index]  # get image from encoder image list
    image_to_rotate = ImageTk.getimage(image_to_rotate)  # convert to PIL image
    rotated_image = ImageTk.PhotoImage(resize_to_fit(image_to_rotate.rotate(90, expand=TRUE)))
    encoder_image_list[image_index] = rotated_image
    image_to_rotate = enhanced_image_list[image_index]  # get image from enhanced image list
    image_to_rotate = ImageTk.getimage(image_to_rotate)  # convert to PIL image
    rotated_image = ImageTk.PhotoImage(resize_to_fit(image_to_rotate.rotate(90, expand=TRUE)))
    enhanced_image_list[image_index] = rotated_image
    update_enc_image(image_index)


# Function to flip the images in the encoder tab
def flip_image():
    image_index = get_current_image_index()
    print(f'Flip image {image_index + 1}')
    image_to_flip = encoder_image_list[image_index]
    image_to_flip = ImageTk.getimage(image_to_flip)
    image_to_flip = ImageOps.flip(image_to_flip)
    flipped_image = ImageTk.PhotoImage(resize_to_fit(image_to_flip))
    encoder_image_list[image_index] = flipped_image
    image_to_flip = enhanced_image_list[image_index]
    image_to_flip = ImageTk.getimage(image_to_flip)
    image_to_flip = ImageOps.flip(image_to_flip)
    flipped_image = ImageTk.PhotoImage(resize_to_fit(image_to_flip))
    enhanced_image_list[image_index] = flipped_image
    update_enc_image(image_index)


# Function to flip the images in the encoder tab
def mirror_image():
    image_index = get_current_image_index()
    print(f'mirror image {image_index + 1}')
    image_to_mirror = encoder_image_list[image_index]
    image_to_mirror = ImageTk.getimage(image_to_mirror)
    image_to_mirror = ImageOps.mirror(image_to_mirror)
    mirrored_image = ImageTk.PhotoImage(resize_to_fit(image_to_mirror))
    encoder_image_list[image_index] = mirrored_image
    image_to_mirror = enhanced_image_list[image_index]
    image_to_mirror = ImageTk.getimage(image_to_mirror)
    image_to_mirror = ImageOps.mirror(image_to_mirror)
    mirrored_image = ImageTk.PhotoImage(resize_to_fit(image_to_mirror))
    enhanced_image_list[image_index] = mirrored_image
    update_enc_image(image_index)


# Function to save images to a selected directory with a name
def save_image(tab):
    save_to_filepath = filedialog.asksaveasfilename()
    if save_to_filepath == '':
        print("Save cancelled.")
    if not save_to_filepath.endswith(('.jpg', '.png')):
        save_to_filepath += '.jpg'
    print(f"Saving image to {save_to_filepath}...")
    if tab == 1:  # Encoder Save pressed
        image_index = get_current_image_index()
        if rb1.get() == "Nothing":
            image_to_use = encoder_image_list[image_index]
        else:
            image_to_use = enhanced_image_list[image_index]
    else:  # Decoder save pressed
        if check_var.get() == 0:  # Greyscale image [0] or [1]
            if rb2.get() == "Original":
                image_to_use = new_dec_image[0]
            else:
                image_to_use = new_dec_image[1]
        else:
            if rb2.get() == "Original":
                image_to_use = new_dec_image[2]
            else:
                image_to_use = new_dec_image[3]
    save_this_image = ImageTk.getimage(image_to_use)
    save_this_image = save_this_image.convert('RGB')
    save_this_image.save(save_to_filepath, "JPEG")
    print(f"Image saved to {save_to_filepath}")
    update_status(f"Image saved to {save_to_filepath}")


# Function to handle the effects on images from selection between radio buttons
def enhancement_handler():
    selected_rb = rb1.get()
    print(f"Selected button: {selected_rb}")
    update_status(f"Selected button:  {selected_rb}")
    image_index = get_current_image_index()
    print(f"Image index enhance handler: {image_index + 1}")
    copy_of_image = encoder_image_list[image_index]
    image_to_enhance = ImageTk.getimage(copy_of_image)  # convert into a PIL image
    image_to_enhance = image_to_enhance.convert('RGB')
    # print(f'image mode: {image_to_enhance.mode}')
    if selected_rb == "Nothing":
        enhanced_image = encoder_image_list[image_index]
    elif selected_rb == "Auto-Contrast":
        enhanced_image = ImageOps.autocontrast(image_to_enhance)
    elif selected_rb == "Edge Enhance":
        enhanced_image = image_to_enhance.filter(ImageFilter.EDGE_ENHANCE)
    elif selected_rb == "Gauss Blur":
        enhanced_image = image_to_enhance.filter(ImageFilter.GaussianBlur(radius=3))
    elif selected_rb == "Equalize":
        enhanced_image = ImageOps.equalize(image_to_enhance)
    elif selected_rb == "Colorize":
        image_to_enhance = image_to_enhance.convert('L')
        enhanced_image = ImageOps.colorize(image_to_enhance, black="blue", white="red", mid="#0FFF60")
    elif selected_rb == "Solarize":
        enhanced_image = ImageOps.solarize(image_to_enhance)
    elif selected_rb == "Invert":
        enhanced_image = ImageOps.invert(image_to_enhance)
    if selected_rb != "Nothing":  # convert back into a PhotoImage object
        enhanced_image = ImageTk.PhotoImage(enhanced_image)

    # store enhanced image in enhanced_image_list
    enhanced_image_list[image_index] = enhanced_image

    # reload enhanced image in the frame
    update_enc_image(image_index)


# Function to handle the effects on images from selection between radio buttons
def processor_handler():
    global dec_image
    selected_rb = rb2.get()
    print(f"Selected button: {selected_rb}")
    update_status(f"Selected button:  {selected_rb}")
    if check_var.get() == 0:
        copy_of_image = new_dec_image[0]
    else:
         copy_of_image = new_dec_image[2]
    copy2 = copy_of_image
    image_to_enhance = ImageTk.getimage(copy_of_image)  # convert into a PIL image

    # print(f'image mode: {image_to_enhance.mode}')
    if selected_rb == "Original":
        enhanced_image = copy2
    elif selected_rb == "Colorize":
        image_to_enhance = image_to_enhance.convert('L')  # convert into greyscale
        enhanced_image = ImageOps.colorize(image_to_enhance, black="purple", white="yellow")
    elif selected_rb == "Edge Enhance":
        enhanced_image = image_to_enhance.filter(ImageFilter.EDGE_ENHANCE)
    elif selected_rb == "Gauss Blur":
        enhanced_image = image_to_enhance.filter(ImageFilter.GaussianBlur(radius=3))
    elif selected_rb == "EQ":
        image_to_enhance = image_to_enhance.convert('RGB')  # convert into greyscale
        enhanced_image = ImageOps.equalize(image_to_enhance)
    elif selected_rb == "Posterize":
        image_to_enhance = image_to_enhance.convert('RGB')  # convert into greyscale
        enhanced_image = ImageOps.posterize(image_to_enhance, 2)
    else:
        return
    if selected_rb != "Original":  # convert back into a PhotoImage object
        enhanced_image = ImageTk.PhotoImage(enhanced_image)


    # reload processed image in the frame
    dec_image.grid_forget()
    if check_var.get() == 0:
        new_dec_image[1] = enhanced_image
        dec_image = Label(dec_image_frame, image=new_dec_image[1], padx=10, pady=10, relief=SUNKEN)
    else:
        new_dec_image[3] = enhanced_image
        dec_image = Label(dec_image_frame, image=new_dec_image[3], padx=10, pady=10, relief=SUNKEN)
    dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


# Function for accepting enhancements button
def accept_enhancements():
    image_index = get_current_image_index()
    encoder_image_list[image_index] = enhanced_image_list[image_index]
    print("Enhancement accepted.")
    rb1.set("Nothing")


# Function for accepting processing button
def accept_processing():
    if rb2.get() == 'Original':
        print("Nothing to Process.")
    else:
        if check_var.get() == 0:
            new_dec_image[0] = new_dec_image[1]
        else:
            new_dec_image[2] = new_dec_image[3]
        print("Processing accepted.")
        rb2.set("Original")


# Function I might use to make clicking tabs more interesing
def tab_clicked(event):
    print("tab switched")
    # print(f"tab clicked, event:{event}")
    # screen_width = encoder_tab.winfo_width()
    # screen_height = encoder_tab.winfo_screenheight()
    # print(f" W x H: {screen_width} x {screen_height}")
    # # resize the screen depending on tab clicked, determined by x pos. of click
    # if 0 <= event.x <= 48:
    #     # root.geometry()
    # elif 49 <= event.x <= 96:
    #     # root.geometry()
    # elif 97 <= event.x <= 192:
    #     # root.geometry()


# Initializations of some commonly used vars and lists
encoder_image_list = []
enhanced_image_list = []
new_dec_image = []
enc_image_filename_list = []  # store image file names
enc_image_filepath_list = []  # store image filepaths in selected dir
background_color = '#3F4A57'  # default bg color
other_object_color = '#3695C2'
current_image_index = 0
plot_counter = 0
sys.stdout.write = sysout_redirector
mixer.init()  #initialize pygame mixer
paused = False
running = False
rgby_list = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]  # list to hold default R G B values
count_up = True

# Make the root GUI, give it a title and icon, change the font and background
root = Tk()
root.title("Simple APT")
root.iconbitmap('misc/sound_wave_icon.ico')
root.configure(background=background_color)
root.option_add("*font", "times 10")

# Create all the tabs within root, managed with ttk Notebook
tab_control = ttk.Notebook(root)
encoder_tab = Frame(tab_control, bg=background_color)
decoder_tab = Frame(tab_control, bg=background_color)
read_only_tab = Frame(tab_control, bg=background_color)
testing_tab = Frame(tab_control, bg=background_color)

# Pack tabs to screen
tab_control.add(encoder_tab, text="Encode")
tab_control.add(decoder_tab, text="Decode")
tab_control.add(read_only_tab, text="Program Output")
tab_control.add(testing_tab, text="Testing")
tab_control.pack()
tab_control.bind('<Button-1>', tab_clicked)

# Create and place the frame that will hold the output of program(s)
read_only_frame = LabelFrame(read_only_tab, bg=other_object_color)
read_only_frame.grid(row=0, column=0, padx=10, pady=10, sticky=W + E)

# Add a program output title, scrollbar and textbox to the read_only_frame
read_only_title = Label(read_only_frame, pady=5, font='Arial 10 bold',
                        bg=other_object_color, text='Program Output')
read_only_title.grid(row=0, column=0)
read_only_scrollbar = Scrollbar(read_only_frame, bg=other_object_color,
                                activebackground=other_object_color)
read_only_textbox = Text(read_only_frame, width=135, bg="light grey", yscrollcommand=read_only_scrollbar.set)
read_only_textbox.bind("<Key>", lambda e: "break")  # cheeky way to make the textbox read only
read_only_scrollbar.config(command=read_only_textbox.yview)
read_only_textbox.grid(row=1, column=0)
read_only_scrollbar.grid(row=1, column=1, sticky=N + S)

# Create the title labels for first two tabs
encoder_tab_title = Label(encoder_tab, text="SIMPLE APT ENCODER",
                          font="Abadi 24 italic bold", bg=other_object_color,
                          padx=10, relief=RIDGE).grid(row=0, column=2, sticky=NE)
decoder_tab_title = Label(decoder_tab, text="SIMPLE APT DECODER",
                          font="Abadi 23 italic bold", bg=other_object_color,
                          padx=10, relief=RIDGE).grid(row=0, column=0, sticky=NW)

# Create initial image objects and place in the initial image lists
initial_enc_image = ImageTk.PhotoImage(resize_to_fit(Image.open('misc/initial_image.png')))
initial_dec_image = ImageTk.PhotoImage(resize_to_fit(Image.open('misc/initial_image_grey.png')))
initial_dec_color = Image.open('misc/initial_image_grey.png')
initial_dec_color = initial_dec_color.convert('L')
initial_dec_color = ImageTk.PhotoImage(resize_to_fit(false_color(initial_dec_color)))

encoder_image_list.append(initial_enc_image)
new_dec_image.append(initial_dec_image)
new_dec_image.append(initial_dec_image)
new_dec_image.append(initial_dec_color)
new_dec_image.append(initial_dec_color)
enhanced_image_list.append(initial_enc_image)
enc_image_filename_list.append('initial_image.png')
enc_image_filepath_list.append('misc/initial_image.png')

# Create basic 'input/output' labels for first two tabs
encoder_input_label = Label(encoder_tab, text="input", borderwidth=2, bg=other_object_color,
                            font="times 12 underline", relief=RIDGE, padx=10).grid(row=1, column=0)
encoder_output_label = Label(encoder_tab, text="output", borderwidth=2, bg=other_object_color,
                            font="times 12 underline", relief=RIDGE, padx=10).grid(row=1, column=2)
decoder_input_label = Label(decoder_tab, text="input", borderwidth=2, bg=other_object_color,
                            font="times 12 underline", relief=RIDGE, padx=10).grid(row=1, column=0)
decoder_output_label = Label(decoder_tab, text="output", borderwidth=2, bg=other_object_color,
                            font="times 12 underline", relief=RIDGE, padx=10).grid(row=1, column=2)

# Create the plots
enc_plot = Figure(figsize=(4, 3), dpi=100, tight_layout=TRUE,
                  facecolor=other_object_color, linewidth=1)
dec_plot = Figure(figsize=(4, 3), dpi=100, tight_layout=TRUE,
                  facecolor=other_object_color, linewidth=1)
enc_subplot = enc_plot.add_subplot(111)
enc_subplot.set_facecolor(other_object_color)
enc_subplot.axes.format_coord = lambda x, y: "in figure"
dec_subplot = dec_plot.add_subplot(111)
dec_subplot.set_facecolor(other_object_color)
dec_subplot.axes.format_coord = lambda x, y: "in figure"

# Create the frames for the figures to sit in
enc_plot_frame = Frame(encoder_tab, bg=background_color)
enc_plot_frame.grid(row=0, column=2, padx=10, pady=50, sticky=S)
dec_plot_frame = Frame(decoder_tab, bg=background_color)
dec_plot_frame.grid(row=0, column=0, padx=10, pady=50, sticky=S)

# Create Encoder Figure Plot object with toolbar
enc_canvas = FigureCanvasTkAgg(enc_plot, master=enc_plot_frame)
enc_toolbar = CustomToolbar(enc_canvas, enc_plot_frame)
enc_toolbar.config(bg=background_color)
enc_toolbar._message_label.config(bg=background_color, fg="light grey")
enc_toolbar.update()
enc_toolbar.grid(row=1, column=0, padx=10, sticky=W + E)
enc_canvas.tkcanvas.grid(row=0, column=0)

# Create Decoder Figure Plot object with toolbar
dec_canvas = FigureCanvasTkAgg(dec_plot, master=dec_plot_frame)
dec_toolbar = CustomToolbar(dec_canvas, dec_plot_frame)
dec_toolbar.config(bg=background_color)
dec_toolbar._message_label.config(bg=background_color, fg="light grey")
dec_toolbar.update()
dec_toolbar.grid(row=1, column=0, padx=10, sticky=W + E)
dec_canvas.tkcanvas.grid(row=0, column=0)

# Slider for speed of graph updates
graph_speed = Scale(decoder_tab, from_=12, to=416, orient=HORIZONTAL, resolution=4,
                    showvalue=0, troughcolor=other_object_color, bg=background_color)
graph_speed.grid(row=0, column=0, padx=50, pady=20, sticky=SE)
graph_speed.set(416)

# Labels to hide random whitespace box caused by Navigation Toolbar
Label(dec_plot_frame, text="  ", bg=background_color).grid(row=1, column=0, padx=10, sticky=NS + E)  # hide whitespace
Label(enc_plot_frame, text="  ", bg=background_color).grid(row=1, column=0, padx=10, sticky=NS + E)  # hide whitespace

# Create the encoder and decoder image frames
enc_image_frame = LabelFrame(encoder_tab, bg=other_object_color)
enc_image_frame.grid(row=0, column=0, padx=10, pady=10, sticky=W)
dec_image_frame = LabelFrame(decoder_tab, bg=other_object_color)
dec_image_frame.grid(row=0, column=2, padx=10, pady=10, sticky=E)

# Create and place the initial image object in the respective image frames
enc_image = Label(enc_image_frame, image=encoder_image_list[0], relief=SUNKEN)
enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
dec_image = Label(dec_image_frame, image=new_dec_image[0], relief=SUNKEN)
dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Post-Processing Frame in the Encoder Tab
preprocess_frame = LabelFrame(encoder_tab, bg=other_object_color)
preprocess_frame.grid(row=0, column=1, padx=10, pady=30)
enc_frame_title = Label(preprocess_frame, text="Pre-Process", bg=other_object_color,
                        font="times 12 underline").grid(row=0, column=0, sticky=W + E)

# Pre-Processing Frame in the Decoder Tab
postprocess_frame = LabelFrame(decoder_tab, bg=other_object_color)
postprocess_frame.grid(row=0, column=1, padx=10, pady=10)
dec_frame_title = Label(postprocess_frame, text="Post-Process", bg=other_object_color,
                        font="times 12 underline").grid(row=0, column=0, sticky=W + E)

rb1 = StringVar(None, "Nothing")
# Encoder Enhancement Radio Buttons
enhancement_values = {"Nothing": "Nothing",
                      "Auto-Contrast": "Auto-Contrast",
                      "Edge Enhance": "Edge Enhance",
                      "Gauss. Blur": "Gauss Blur",
                      "Equalize": "Equalize",
                      "Colorize": "Colorize",
                      "Solarize": "Solarize",
                      "Invert": "Invert"}

rb_row_placement = 1
for (text, value) in enhancement_values.items():
    Radiobutton(preprocess_frame, text=text, variable=rb1,
                command=enhancement_handler, value=value,
                bg=other_object_color, activebackground=other_object_color,
                indicator=1).grid(row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1


rb2 = StringVar(None, "Original")
# Decoder Processing Radio Buttons
processing_values = {"Original": "Original",
                     "Gauss Blur": "Gauss Blur",
                     "Edge Enhance": "Edge Enhance",
                     "Colorize": "Colorize",
                     "Posterize": "Posterize",
                     "EQ": "EQ"}

rb_row_placement = 1
for (text, value) in processing_values.items():
    Radiobutton(postprocess_frame, text=text, variable=rb2,
                command=processor_handler, bg=other_object_color, activebackground=other_object_color,
                value=value, indicator=1).grid(row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1

# Check button for False color
check_var = IntVar(None, 0)
Checkbutton(decoder_tab, text="False Color", variable=check_var, bg=background_color,
            fg="light grey", activebackground=background_color, selectcolor=other_object_color,
            command=switch_between).grid(row=0, column=1, pady=90, sticky=N)

# Initial Status Bars
enc_status = Label(encoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=3, sticky=W + E)
dec_status = Label(decoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=3, sticky=W + E)

# Create entry boxes for encode and decode tab
enc_entry_input_text = StringVar(None, "misc/initial_image.png")
enc_entry_input_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                            textvariable=enc_entry_input_text)
enc_entry_input_box.bind("<Return>", (lambda event: entry_return_pressed(1)))  # keybind to sense enter pressed
enc_entry_input_box.grid(row=2, column=0)

enc_entry_output_text = StringVar(None, "wav/initial_wav.wav")
enc_entry_output_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                             textvariable=enc_entry_output_text).grid(row=2, column=2)

dec_entry_input_text = StringVar(None, "wav/initial_wav.wav")
dec_entry_input_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                            textvariable=dec_entry_input_text)
dec_entry_input_box.bind("<Return>", (lambda event: entry_return_pressed(0)))
dec_entry_input_box.grid(row=2, column=0)

dec_entry_output_text = StringVar(None, "output/initial_image_dec.png")
dec_entry_output_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                             textvariable=dec_entry_output_text).grid(row=2, column=2)

# Update graphs with initial wav samples
update_graph(0)
update_graph(1)

# Forward and Backward buttons
button_backward = Button(encoder_tab, text="<<", command=backward,
                         state=DISABLED).grid(row=1, column=0, padx=20, sticky=NW)
button_forward = Button(encoder_tab, text=">>", command=forward,
                        state=DISABLED).grid(row=1, column=0, padx=20, sticky=NE)

# Encode/Decode buttons
Button(encoder_tab, text="Encode", command=lambda: popups(1)).grid(row=1, column=1, rowspan=2, pady=5, sticky=NSEW)
Button(decoder_tab, text="Decode", command=lambda: popups(0)).grid(row=1, column=1, rowspan=2, pady=5, sticky=NSEW)

# Color Picker button
Button(decoder_tab, text = "Select color", command = choose_color).grid(row=0, column=1, pady=90, sticky=EW + S)


# Rotate image button
Button(encoder_tab, text="Rotate", command=rotate_image).grid(row=0, column=1, sticky=SW)

# Mirror image button
Button(encoder_tab, text="Mirror", command=mirror_image).grid(row=0, column=1, sticky=SE)

# Flip image button
Button(encoder_tab, text="Flip", command=flip_image).grid(row=0, column=1, padx=5, pady=30, sticky=SE)

# Encoder/Decoder Save buttons
Button(encoder_tab, text="Save", command=lambda: save_image(1)).grid(row=0, column=1, padx=5, pady=30, sticky=SW)
Button(decoder_tab, text="Save", command=lambda: save_image(0)).grid(row=0, column=1, padx=5, pady=50, sticky=SW)

# Accept enhancements/processing buttons
Button(preprocess_frame, text="Add", command=accept_enhancements).grid(row=8, column=0, sticky=SE)
Button(postprocess_frame, text="Add", command=accept_processing).grid(row=6, column=0, sticky=SE)

# Encoder browse buttons
Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 1)).grid(  # input browse button
    row=2, column=0, padx=10, pady=10, sticky=W)
Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 0)).grid(  # output browse button
    row=2, column=2, padx=10, pady=5, sticky=E)

# Decoder browse buttons
Button(decoder_tab, text="Browse", command=lambda: browse_dir(0, 1)).grid(  # input browse button
    row=2, column=0, padx=80, pady=5, sticky=W)
Button(decoder_tab, text="Browse", command=lambda: browse_dir(0, 0)).grid(  # output browse button
    row=2, column=2, padx=10, pady=5, sticky=E)

# Exit buttons
Button(encoder_tab, text="Quit", command=root.quit).grid(row=0, column=2, padx=10, pady=10, sticky=SE)  # enc exit
Button(decoder_tab, text="Quit", command=root.quit).grid(row=1, column=2, padx=20, pady=5, sticky=E) # dec exit

# Send to Decoder button
Button(encoder_tab, text="Send to Decoder", command=send_to_decoder).grid(row=1, column=2, padx=5, sticky=E)

# Button to play/stop plot, decoder tab
Button(dec_plot_frame, text="Run", command=lambda: pre_run_plot(running)).grid(row=1, column=0, padx=130, pady=5, sticky=NS + E)
Button(dec_plot_frame, text="Stop", command=stop_plot).grid(row=1, column=0, padx=90, pady=5, sticky=NS + E)

# Reset decoder image picture
Button(decoder_tab, text="Reset", command=reset_dec_image).grid(row=0, column=1, padx=5, pady=50, sticky=SE)

# Playback and Pause Buttons
playback_button = Button(decoder_tab, text="Play", command=play_wav)
playback_button.grid(row=0, column=0, padx=10, pady=5, sticky=SW)
pause_button = Button(decoder_tab, text="Pause", command=lambda: pause_wav(paused))
pause_button.grid(row=1, column=0, padx=10, sticky=W)
stop_button = Button(decoder_tab, text="Stop", command=stop_wav)
stop_button.grid(row=2, column=0, padx=10, sticky=W)

# Last buttons, color cycle and stop
start_color_cycle_btn = Button(decoder_tab, text="Cycle!", command=pre_color_cycle)
start_color_cycle_btn.grid(row=0, column=1, padx=5, pady=50, sticky=N)
Button(decoder_tab, text="Stop", command=stop_color_cycle).grid(row=0, column=1, padx=5, pady=50, sticky=NE)

# Main loop for the GUI application
root.mainloop()
