from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image
import winsound  # use a different module if not on windows
import pathlib
import subprocess


# Resize keep aspect ratio
def resize_to_fit(image):
    image_width, image_height = image.size
    if image_height >= 500:
        new_height = 400
        ratio = (new_height / float(image_height))
        new_width = int((float(image_width) * float(ratio)))
        image = image.resize((new_width, new_height))
    while image_width >= 1000:
        image_width, image_height = image.size
        image = image.resize((image_width // 2, image_height // 2))
    return image


# Create backward/forward button commands
def forward(image_index):
    global enc_image
    global button_forward
    global button_backward

    # Reset grid and re-place w/ new image and
    enc_image.grid_forget()
    enc_image = Label(enc_image_frame, image=encoder_image_list[image_index - 1], padx=10, pady=10, relief=SUNKEN)
    button_forward = Button(encoder_tab, text=">>", command=lambda: forward(image_index + 1))
    button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index - 1))

    if image_index == len(encoder_image_list):
        button_forward = Button(encoder_tab, text=">>", state=DISABLED)

    enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    button_backward.grid(row=1, column=0, sticky=W, padx=25)
    button_forward.grid(row=1, column=2, sticky=W)

    enc_entry_input_text.set(enc_image_filepath_list[image_index - 1])

    update_status = Label(encoder_tab, text="Image " + str(image_index) + " of " + str(len(encoder_image_list)),
                          bd=1, relief=SUNKEN, anchor=E, bg='light grey')
    update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


def backward(image_index):
    global enc_image
    global button_forward
    global button_backward

    enc_image.grid_forget()
    enc_image = Label(enc_image_frame, image=encoder_image_list[image_index - 1], padx=10, pady=10, relief=SUNKEN)
    button_forward = Button(encoder_tab, text=">>", command=lambda: forward(image_index + 1))
    button_backward = Button(encoder_tab, text="<<", command=lambda: backward(image_index - 1))

    if image_index == 1:
        button_backward = Button(encoder_tab, text="<<", state=DISABLED)

    enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    button_backward.grid(row=1, column=0, sticky=W, padx=25)
    button_forward.grid(row=1, column=2, sticky=W)

    enc_entry_input_text.set(enc_image_filepath_list[image_index - 1])

    update_status = Label(encoder_tab, text="Image " + str(image_index) + " of " + str(len(encoder_image_list)),
                          bd=1, relief=SUNKEN, anchor=E, bg='light grey')
    update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


# Define popup message boxes
def browse_dir(tab, io):
    global enc_image
    global button_forward
    global button_backward
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
    if use_tab.filename != '':  # user doesn't click exit or cancel
        if (tab == 1 and io == 1):  # only applies to input of encoder
            dir_path = use_tab.filename
            new_image_list(dir_path)  # create a new image list with the contents in the directory


def new_image_list(directory_path):
    global enc_image
    global button_forward
    global button_backward
    flipped_filename = ''  # empty string to store file name
    for char in reversed(directory_path):
        # print(char)
        if char == '/':
            break
        flipped_filename += char  # returns the file-name but flipped
        directory_path = directory_path.rstrip(char)  # remove 1 letter off the end until first '/' is found
    print(f'Clicked image dir path: {directory_path}')  # now we have folder file path and the clicked image
    # print(f'flipped name: {flipped_filename}')
    clicked_image = flipped_filename[::-1]  # flips the file name, this was the clicked image
    print(f'Clicked image: {clicked_image}')
    del encoder_image_list[:]  # clear image list to upload new batch   (to load new images into list and into frame)
    del enc_image_filename_list[:]  # clear image filename list    (for indexing purposes)
    del enc_image_filepath_list[:]  # clear the image filepath list (for entry box)
    clicked_image_index = 0  # reset the clicked image index
    for file in pathlib.Path(directory_path).glob('*.*'):  # search all contents in directory path
        image_file_path = str(file)
        if image_file_path.lower().endswith(('.jpg', '.png', '.pgm')):  # if a photo,
            print(image_file_path)
            enc_image_filepath_list.append(image_file_path)  # add the path to the filepath list
            enc_image_filename_list.append(image_file_path[len(directory_path):])  # add it to filename list
            if image_file_path.lower().endswith('.pgm'):  # placeholder photo till i can preview .pgms
                image = ImageTk.PhotoImage(resize_to_fit(Image.open('misc/pgm_placeholder.png')))
            else:
                image = ImageTk.PhotoImage(resize_to_fit(Image.open(image_file_path)))  # add all images in order
            encoder_image_list.append(image)  # to the image_list
    print(f'All images in selected dir: {enc_image_filename_list}')
    print(f'All image filepaths: {enc_image_filepath_list}')
    for image_name in enc_image_filename_list:
        if image_name == clicked_image:
            clicked_image_index = enc_image_filename_list.index(image_name)
            print(f'Clicked image index: {clicked_image_index}')
    enc_image.grid_forget()
    enc_image = Label(enc_image_frame, image=encoder_image_list[clicked_image_index], padx=10, pady=10, relief=SUNKEN)
    enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    print(f'length of image list: {len(encoder_image_list)}')

    # Update the buttons depending on index of selected image
    if clicked_image_index == 0:
        button_backward = Button(encoder_tab,text="<<", command=backward, state=DISABLED)
        button_forward = Button(encoder_tab, text=">>", command=lambda: forward(2))
    elif clicked_image_index == (len(encoder_image_list) - 1):
        button_backward = Button(encoder_tab, text="<<", command=lambda: backward(clicked_image_index))
        button_forward = Button(encoder_tab, text=">>", command=forward, state=DISABLED)
    else:
        button_forward = Button(encoder_tab, text=">>", command=lambda: forward(clicked_image_index + 2))
        button_backward = Button(encoder_tab, text="<<", command=lambda: backward(clicked_image_index - 2))
    #
    button_backward.grid(row=1, column=0, sticky=W, padx=25)
    button_forward.grid(row=1, column=2, sticky=W)

    # Update the status bar
    update_status = Label(encoder_tab, text="Image " + str(clicked_image_index+1) + " of " + str(len(encoder_image_list)),
                          bd=1, relief=SUNKEN, anchor=E, bg='light grey')
    update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


def popups(tab):
    if tab == 1:
        msg = messagebox.askyesno("About to Encode", "Are you sure?")
        call_process = 'python apt_encoder.py '
        used_tab = encoder_tab
        input_entry_used = enc_entry_input_text
        output_entry_used = enc_entry_output_text
    else:
        msg = messagebox.askyesno("About to Decode", "Are you sure?")
        call_process = 'python apt_decoder.py '
        used_tab = decoder_tab
        input_entry_used = dec_entry_input_text
        output_entry_used = dec_entry_output_text
    if msg == 1:
        input_file_path = input_entry_used.get()
        output_file_path = output_entry_used.get()
        subprocess.call(call_process + input_file_path + " " + output_file_path,
                        stdin=subprocess.PIPE)
        # stderr=subprocess.PIPE)
        update_status = Label(used_tab, text="Success.",
                              bd=1, relief=SUNKEN, anchor=E, bg='light grey')
        update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)
    else:
        update_status = Label(used_tab, text="Cancelled.",
                              bd=1, relief=SUNKEN, anchor=E, bg='light grey')
        update_status.grid(row=5, column=0, columnspan=9, sticky=W + E)


# Make simple playback/pause function
def wav_playback(file_path):
    if file_path is None:
        # Stop playback
        winsound.PlaySound(None, winsound.SND_ASYNC)
    else:
        # Start Playback
        winsound.PlaySound(file_path, winsound.SND_ASYNC)


# Function to send output of encoder to input of decoder
def send_to_decoder():
    dec_entry_input_text.set(enc_entry_output_text.get())


background_color = '#AED7D2'  # default bg color
encoder_image_list = []
decoder_image_list = []
enc_image_filename_list = []
enc_image_filepath_list = []

# Make the root GUI, give it a title and icon
root = Tk()
root.title("Simple APT")
root.iconbitmap('misc/sound_wave_icon.ico')
root.configure(background=background_color)
root.option_add("*font", "times 10")

# Create tabs within root
tab_control = ttk.Notebook(root)
encoder_tab = Frame(tab_control, bg=background_color)
decoder_tab = Frame(tab_control, bg=background_color)
terminal_tab = Frame(tab_control, bg=background_color)
help_tab = Frame(tab_control, bg=background_color)

# Add tabs to screen
tab_control.add(encoder_tab, text="Encode")
tab_control.add(decoder_tab, text="Decode")
tab_control.add(terminal_tab, text="Program Output")
tab_control.add(help_tab, text="Help")
tab_control.pack()

# Create Title labels for each tab
encoder_tab_title = Label(encoder_tab, text="SIMPLE APT ENCODER", font="Abadi 24 italic bold",
                          bg='#D3D8C3', padx=10, relief=RIDGE).grid(
    row=0, column=3, columnspan=5, sticky=NE)
decoder_tab_title = Label(decoder_tab, text="SIMPLE APT DECODER", font="Abadi 23 italic bold",
                          bg='#D3D8C3', padx=10, relief=RIDGE).grid(
    row=0, column=0, columnspan=6, sticky=NW)

# Create input/output labels for each tab
encoder_input_label = Label(encoder_tab, text="input", padx=10).grid(
    row=1, column=1)
encoder_output_label = Label(encoder_tab, text="output", padx=10).grid(
    row=1, column=5)
decoder_input_label = Label(decoder_tab, text="input", padx=10).grid(
    row=1, column=2)
decoder_output_label = Label(decoder_tab, text="output", padx=10).grid(
    row=1, column=7)

# Create the plot
enc_plot = Figure(figsize=(3, 2), dpi=100)
dec_plot = Figure(figsize=(3, 2), dpi=100)
enc_subplot = enc_plot.add_subplot(111)
dec_subplot = dec_plot.add_subplot(111)
# t_samples = np.arange(0.0, 2.0, .1)
# test_sig = np.sin(2.0 * np.pi * t_samples)

# init_subplot.plot(0, color="red")
enc_subplot.set_title('Output WAV')
enc_subplot.set_xlabel('Samples')
enc_subplot.set_ylabel('Amplitude')
# init_subplot.legend()

# init_subplot.plot(0, color="red")
dec_subplot.set_title('Input WAV')
dec_subplot.set_xlabel('Samples')
dec_subplot.set_ylabel('Amplitude')
# init_subplot.legend()

# Create Figure objects
enc_canvas = FigureCanvasTkAgg(enc_plot, master=encoder_tab)
enc_canvas.tkcanvas.grid(row=0, column=4, columnspan=4, padx=10, pady=50)

dec_canvas = FigureCanvasTkAgg(dec_plot, master=decoder_tab)
dec_canvas.tkcanvas.grid(row=0, column=0, columnspan=4, padx=10, pady=50)

# Create image objects, replace input file with pictures
initial_image = ImageTk.PhotoImage(resize_to_fit(Image.open('misc/initial_image.png')))

# Create the encoder and decoder image frames
enc_image_frame = LabelFrame(encoder_tab)
enc_image_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
dec_image_frame = LabelFrame(decoder_tab)
dec_image_frame.grid(row=0, column=6, columnspan=3, padx=10, pady=10)

# Create and place an image object in the encoder image frame
enc_image = Label(enc_image_frame, image=initial_image, padx=10, pady=10, relief=SUNKEN)
enc_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
dec_image = Label(dec_image_frame, image=initial_image, padx=10, pady=10, relief=SUNKEN)
dec_image.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Enhancement Frame in the Encoder Tab
enhancement_frame = LabelFrame(encoder_tab)
enhancement_frame.grid(row=0, column=3, padx=10, pady=10)
enc_frame_title = Label(enhancement_frame, text="Enhancements", font="times 12 underline").grid(
    row=0, column=0, sticky=W + E)

# Processing Frame in the DEcoder Tab
processing_frame = LabelFrame(decoder_tab)
processing_frame.grid(row=0, column=4, columnspan=2, padx=10, pady=10)
dec_frame_title = Label(processing_frame, text="Processing", font="times 12 underline").grid(
    row=0, column=0, sticky=W + E)

# Decoder Processing Radio Buttons
processing_values = {"Greyscale": "1",
                     "False Color": "2",
                     "Opt. 3": "3",
                     "Opt. 4": "4",
                     "Opt. 5": "5",
                     "Opt. 6": "6"}

rb_row_placement = 1
r = IntVar()
for (text, value) in processing_values.items():
    Radiobutton(processing_frame, text=text, variable=r, value=value, indicator=1).grid(
        row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1

# Encoder Enhancement Radio Buttons
enhancement_values = {"Opt. 1": "1",
                     "Opt. 2": "2",
                     "Opt. 3": "3",
                     "Opt. 4": "4",
                     "Opt. 5": "5",
                     "Opt. 6": "6"}

rb_row_placement = 1
for (text, value) in enhancement_values.items():
    Radiobutton(enhancement_frame, text=text, variable=r, value=value, indicator=1).grid(
        row=rb_row_placement, column=0, pady=1, sticky=W)
    rb_row_placement += 1

# Initial Status Bars
enc_status = Label(encoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=9, sticky=W + E)
dec_status = Label(decoder_tab, text="Select an input file with 'Browse' or type in the filepath",
                   bd=1, relief=SUNKEN, anchor=E, bg='light grey').grid(
    row=5, column=0, columnspan=9, sticky=SW + SE)

# Create entry boxes for encode and decode tab
enc_entry_input_text = StringVar()
enc_entry_input_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                            textvariable=enc_entry_input_text).grid(row=2, column=1)

enc_entry_output_text = StringVar()
enc_entry_output_box = Entry(encoder_tab, bg='light grey', borderwidth=2,
                             textvariable=enc_entry_output_text).grid(row=2, column=5)

dec_entry_input_text = StringVar()
dec_entry_input_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                            textvariable=dec_entry_input_text).grid(row=2, column=2)

dec_entry_output_text = StringVar()
dec_entry_output_box = Entry(decoder_tab, bg='light grey', borderwidth=2,
                             textvariable=dec_entry_output_text).grid(row=2, column=7)

# Forward and Backward buttons
button_backward = Button(encoder_tab, text="<<", command=backward, state=DISABLED).grid(
    row=1, column=0, padx=25, sticky=W)
button_forward = Button(encoder_tab, text=">>", command=forward, state=DISABLED).grid(
    row=1, column=2, sticky=W)

# Encode/Decode buttons
encode_button = Button(encoder_tab, text="Encode", command=lambda: popups(1)).grid(
    row=1, column=3, rowspan=2, padx=10, pady=5, sticky=N+S)
decode_button = Button(decoder_tab, text="Decode", command=lambda: popups(0)).grid(
    row=1, column=5, padx=10, rowspan=2, pady=5, sticky=N+S)

# Encoder Browse Buttons
enc_browse_input_button = Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 1)).grid(
    row=2, column=0, padx=10, pady=10, sticky=E)
enc_browse_output_button = Button(encoder_tab, text="Browse", command=lambda: browse_dir(1, 0)).grid(
    row=2, column=7, padx=10, pady=5)

# Decoder Browse buttons
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
