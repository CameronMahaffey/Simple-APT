from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image, ImageOps, ImageFilter
import winsound  # use a different module if not on windows
import pathlib
import subprocess
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import sys


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
    global enc_plot
    global enc_canvas
    global dec_plot
    global dec_canvas

    if which_plot == 1:
        enc_subplot.clear()
        enc_subplot.set_title('Output WAV')
        enc_subplot.set_xlabel('Samples')
        enc_subplot.set_ylabel('Amplitude')
        baud, wav_file = wav.read(enc_entry_output_text.get())  # get the wav file from output of enc
        sample_data = wav_file[:4160]   # get some samples

        enc_canvas.tkcanvas.grid_forget()
        enc_subplot.plot(sample_data, color=background_color, label="wav")
        enc_canvas = FigureCanvasTkAgg(enc_plot, master=encoder_tab)
        enc_canvas.get_tk_widget().grid(row=0, column=4, columnspan=4, padx=10, pady=50)
        enc_canvas.tkcanvas.grid(row=0, column=4, columnspan=4, padx=10, pady=50)
        # print("Encoder Plot Updated")
        enc_subplot.legend()
    else:
        dec_subplot.clear()
        dec_subplot.set_title('Input WAV')
        dec_subplot.set_xlabel('Samples')
        dec_subplot.set_ylabel('Amplitude')
        baud, wav_file = wav.read(dec_entry_input_text.get())  # get the wav file from input of dec
        sample_data = wav_file[:4160]   # get some samples
        am_sample_data = np.abs(signal.hilbert(sample_data))

        dec_canvas.tkcanvas.grid_forget()
        dec_subplot.plot(sample_data, color=background_color, label="wav")
        dec_subplot.plot(am_sample_data, color="red", label="data")
        dec_canvas = FigureCanvasTkAgg(dec_plot, master=decoder_tab)
        dec_canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, padx=10, pady=50)
        dec_canvas.tkcanvas.grid(row=0, column=0, columnspan=4, padx=10, pady=50)
        # print("Decoder Plot Updated")
        dec_subplot.legend()


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

    button_backward.grid(row=1, column=0, sticky=E)
    button_forward.grid(row=1, column=2, sticky=W)

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

    button_backward.grid(row=1, column=0, sticky=E)
    button_forward.grid(row=1, column=2, sticky=W)

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
                new_image_list(dir_path)  # create a new image list with the contents in the directory
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
    del enc_image_filename_list[:]  # clear image filename list    (for indexing purposes)
    del enc_image_filepath_list[:]  # clear the image filepath list (for entry box)
    current_image_index = 0  # reset the clicked image index
    print(f"All images in {directory_path}:")
    for file in pathlib.Path(directory_path).glob('*.*'):  # search all contents in directory path
        image_file_path = str(file)
        if image_file_path.lower().endswith(('.jpg', '.png', '.pgm')):  # if a photo,
            print(image_file_path)
            enc_image_filepath_list.append(image_file_path)  # add the path to the filepath list
            enc_image_filename_list.append(image_file_path[len(directory_path):])  # add it to filename list
            if image_file_path.lower().endswith('.pgm'):  # placeholder photo till i can preview .pgms
                pgm_array = open(image_file_path, 'r')  # open the .pgm file to create a preview image
                for i in range(4):  # remove first four lines of pgm
                    pgm_array.readline()
                pgm_array = np.uint8(pgm_array.read().split('\n'))      # create a numpy array from .pgm contents
                pgm_array = np.reshape(pgm_array, (pgm_array.size // 909, 909))  # make the array 2D
                # sprint(pgm_array)
                image = ImageTk.PhotoImage(resize_to_fit(Image.fromarray(pgm_array)))
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

    # Update the browsing forward/back buttons depending on index of selected image
    update_buttons(current_image_index)

    # Update the status bar
    update_status(f"Image {str(current_image_index + 1)} of {str(len(encoder_image_list))}")
    print(f"length of image list: {len(encoder_image_list)}\n")


# Function that is called when return is pressed in one of the entry input boxes
def entry_return_pressed(tab):
    print("Enter Pressed.")
    if tab == 1:
        input_text = enc_entry_input_text.get()
        input_text = input_text.replace('/', '\\')
        if input_text != '':
            if input_text in enc_image_filepath_list:
                position_in_list = enc_image_filepath_list.index(input_text)
                print(f"Selected image and directory already loaded into memory.")
                set_current_image_index(position_in_list)
                update_enc_image(position_in_list)
            else:
                new_image_list(input_text)
    else:
        input_text = dec_entry_input_text.get()
        if input_text != '':
            update_graph(0)


# Function called when the image in the encoder tab needs to be updated
def update_enc_image(index):
    global enc_image
    print(f"Enc image update index {index + 1}")
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

    button_backward.grid(row=1, column=0, sticky=E)
    button_forward.grid(row=1, column=2, sticky=W)


# Function to update the status bars at the bottom
def update_status(status_message):
    update_status = Label(encoder_tab, text=status_message,
                          bd=1, relief=SUNKEN, anchor=E, bg='light grey')
    update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


# Display the decoded image when decode button is pressed
def new_decoder_image(image_filepath):
    global dec_image
    del new_dec_image[:]
    new_dec_image.append(ImageTk.PhotoImage(resize_to_fit(Image.open(image_filepath))))
    dec_image.grid_forget()
    dec_image = Label(dec_image_frame, image=new_dec_image[0], padx=10, pady=10, relief=SUNKEN)
    dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)


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
        print(f"Calling process: {call_process} {input_file_path} {output_file_path}")
        call_to_process = subprocess.Popen(f"{call_process} {input_file_path} {output_file_path}",
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
        sysout_redirector(call_to_process.stdout.read())

        delete_temp_file = pathlib.Path("temp.jpg")
        delete_temp_file.unlink()

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


# Make simple playback/stop function with winsound module
def wav_playback(file_path):
    if file_path is None:
        # Stop playback
        winsound.PlaySound(None, winsound.SND_ASYNC)
        print(f"Playing {file_path}")
    else:
        # Start Playback
        winsound.PlaySound(file_path, winsound.SND_ASYNC)
        print(f"Playback stopped.")


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


# Function for accepting enhancements button
def accept_enhancements():
    image_index = get_current_image_index()
    encoder_image_list[image_index] = enhanced_image_list[image_index]
    print("Enhancement accepted.")
    rb1.set("Nothing")


# Initializations of some commonly used vars and lists
encoder_image_list = []
enhanced_image_list = []
new_dec_image = []
enc_image_filename_list = []
enc_image_filepath_list = []
background_color = '#3F4A57'  # default bg color
other_object_color = '#3695C2'
current_image_index = 0
current_image_index = 0
sys.stdout.write = sysout_redirector


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

# Pack tabs to screen
tab_control.add(encoder_tab, text="Encode")
tab_control.add(decoder_tab, text="Decode")
tab_control.add(read_only_tab, text="Program Output")
tab_control.pack()

# Create the title labels for first two tabs
encoder_tab_title = Label(encoder_tab, text="SIMPLE APT ENCODER",
                          font="Abadi 24 italic bold", bg=other_object_color,
                          padx=10, relief=RIDGE).grid(row=0, column=3, columnspan=5, sticky=NE)
decoder_tab_title = Label(decoder_tab, text="SIMPLE APT DECODER",
                          font="Abadi 23 italic bold", bg=other_object_color,
                          padx=10, relief=RIDGE).grid(row=0, column=0, columnspan=6, sticky=NW)

# Create initial image object and place in the encoder image list
initial_image = ImageTk.PhotoImage(resize_to_fit(Image.open('misc/initial_image.png')))
encoder_image_list.append(initial_image)
enhanced_image_list.append(initial_image)

# Create basic 'input/output' labels for first two tabs
encoder_input_label = Label(encoder_tab, text="input", borderwidth=3,
                            relief=RIDGE, padx=10).grid(row=1, column=1)
encoder_output_label = Label(encoder_tab, text="output", borderwidth=3,
                            relief=RIDGE, padx=10).grid(row=1, column=5)
decoder_input_label = Label(decoder_tab, text="input", borderwidth=3,
                            relief=RIDGE, padx=10).grid(row=1, column=2)
decoder_output_label = Label(decoder_tab, text="output", borderwidth=3,
                            relief=RIDGE, padx=10).grid(row=1, column=7)

# Create the plot
enc_plot = Figure(figsize=(4, 3), dpi=100, tight_layout=TRUE,
                  facecolor=other_object_color, linewidth=1)
dec_plot = Figure(figsize=(4, 3), dpi=100, tight_layout=TRUE,
                  facecolor=other_object_color, linewidth=1)
enc_subplot = enc_plot.add_subplot(111)
enc_subplot.set_facecolor(other_object_color)
dec_subplot = dec_plot.add_subplot(111)
dec_subplot.set_facecolor(other_object_color)
enc_subplot.set_title('Output WAV')
enc_subplot.set_xlabel('Samples')
enc_subplot.set_ylabel('Amplitude')
dec_subplot.set_title('Input WAV')
dec_subplot.set_xlabel('Samples')
dec_subplot.set_ylabel('Amplitude')

# Create Figure Plot objects
enc_canvas = FigureCanvasTkAgg(enc_plot, master=encoder_tab)
enc_canvas.tkcanvas.grid(row=0, column=4, columnspan=4, padx=10, pady=50)

dec_canvas = FigureCanvasTkAgg(dec_plot, master=decoder_tab)
dec_canvas.tkcanvas.grid(row=0, column=0, columnspan=4, padx=10, pady=50)

# Create the encoder and decoder image frames
enc_image_frame = LabelFrame(encoder_tab, bg=other_object_color)
enc_image_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
dec_image_frame = LabelFrame(decoder_tab, bg=other_object_color)
dec_image_frame.grid(row=0, column=6, columnspan=3, padx=10, pady=10)

# Create and place the initial image object in the respective image frames
enc_image = Label(enc_image_frame, image=encoder_image_list[0], relief=SUNKEN)
enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
dec_image = Label(dec_image_frame, image=encoder_image_list[0], relief=SUNKEN)
dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

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

# Enhancement Frame in the Encoder Tab
enhancement_frame = LabelFrame(encoder_tab, bg=other_object_color)
enhancement_frame.grid(row=0, column=3, padx=10, pady=30)
enc_frame_title = Label(enhancement_frame, text="Enhancements", bg=other_object_color,
                        font="times 12 underline").grid(row=0, column=0, sticky=W + E)

# Processing Frame in the Decoder Tab
processing_frame = LabelFrame(decoder_tab, bg=other_object_color)
processing_frame.grid(row=0, column=4, columnspan=2, padx=10, pady=10)
dec_frame_title = Label(processing_frame, text="Processing", bg=other_object_color,
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
    Radiobutton(enhancement_frame, text=text, variable=rb1,
                command=enhancement_handler, value=value,
                bg=other_object_color, activebackground=other_object_color,
                indicator=1).grid(row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1


rb2 = IntVar(None, "1")
# Decoder Processing Radio Buttons
processing_values = {"Original": "1",
                     "False Color": "2",
                     "CLUT": "3",
                     "Flip RB": "4",
                     "Opt. 5": "5",
                     "Opt. 6": "6"}

rb_row_placement = 1
for (text, value) in processing_values.items():
    Radiobutton(processing_frame, text=text, variable=rb2,
                bg=other_object_color, activebackground=other_object_color,
                value=value, indicator=1).grid(row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1

# Initial Status Bars
enc_status = Label(encoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=9, sticky=W + E)
dec_status = Label(decoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=9, sticky=W + E)

# Create entry boxes for encode and decode tab
enc_entry_input_text = StringVar(None, "misc/initial_image.png")
enc_entry_input_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                            textvariable=enc_entry_input_text)
enc_entry_input_box.bind("<Return>", (lambda event: entry_return_pressed(1)))
enc_entry_input_box.grid(row=2, column=1)

enc_entry_output_text = StringVar(None, "wav/initial_wav.wav")
enc_entry_output_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                             textvariable=enc_entry_output_text).grid(row=2, column=5)

dec_entry_input_text = StringVar(None, "wav/initial_wav.wav")
dec_entry_input_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                            textvariable=dec_entry_input_text)
dec_entry_input_box.bind("<Return>", (lambda event: entry_return_pressed(0)))
dec_entry_input_box.grid(row=2, column=2)

dec_entry_output_text = StringVar(None, "output/initial_image_dec.png")
dec_entry_output_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                             textvariable=dec_entry_output_text).grid(row=2, column=7)

# Forward and Backward buttons
button_backward = Button(encoder_tab, text="<<", command=backward,
                         state=DISABLED).grid(row=1, column=0, sticky=E)
button_forward = Button(encoder_tab, text=">>", command=forward,
                        state=DISABLED).grid(row=1, column=2, sticky=W)

# Encode/Decode buttons
encode_button = Button(encoder_tab, text="Encode", command=lambda: popups(1)).grid(
    row=1, column=3, rowspan=2, padx=10, pady=5, sticky=N+S)
decode_button = Button(decoder_tab, text="Decode", command=lambda: popups(0)).grid(
    row=1, column=5, padx=10, rowspan=2, pady=5, sticky=N+S)

# Rotate image button
encoder_rotate_button = Button(encoder_tab, text="Rotate",
                               command=rotate_image)
encoder_rotate_button.grid(row=0, column=3, sticky=S)

# Mirror image button
encoder_mirror_button = Button(encoder_tab, text="Mirror",
                               command=mirror_image)
encoder_mirror_button.grid(row=0, column=3, pady=30, sticky=S)

# Flip image button
encoder_flip_button = Button(encoder_tab, text="Flip",
                               command=flip_image)
encoder_flip_button.grid(row=0, column=3, pady=30, sticky=SW)

# Accept enhancements button
accept_enhance_button = Button(enhancement_frame, text="Add",
                               command=accept_enhancements)
accept_enhance_button.grid(row=8, column=0, sticky=SE)

# Encoder browse buttons
enc_browse_input_button = Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 1)).grid(
    row=2, column=0, padx=10, pady=10, sticky=E)
enc_browse_output_button = Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 0)).grid(
    row=2, column=7, padx=10, pady=5)

# Decoder browse buttons
dec_browse_input_button = Button(decoder_tab, text="Browse", command=lambda: browse_dir(0, 1)).grid(
    row=2, column=1, padx=10, pady=5)
dec_browse_output_button = Button(decoder_tab, text="Browse", command=lambda: browse_dir(0, 0)).grid(
    row=2, column=8, padx=10, pady=5)

# Exit buttons
enc_button_exit = Button(encoder_tab, text="Quit", command=root.quit).grid(
    row=0, column=7, padx=10, pady=10, sticky=SW + SE)
dec_button_exit = Button(decoder_tab, text="Quit", command=root.quit).grid(
    row=1, column=1, sticky=W + E)

# Send to Decoder button
send_to_decoder_button = Button(encoder_tab, text="Send to Decoder", command=send_to_decoder).grid(
    row=1, column=7, padx=5, sticky=W+E)

# Playback and Pause Buttons
playback_button = Button(decoder_tab, text="Play", command=lambda: wav_playback(dec_entry_input_text.get())).grid(
    row=1, column=0)
pause_button = Button(decoder_tab, text="Stop", command=lambda: wav_playback(None)).grid(
    row=2, column=0)

# Main loop for the GUI application
root.mainloop()