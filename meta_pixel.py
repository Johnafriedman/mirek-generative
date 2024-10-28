import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from constants import GOLDEN_RATIO
from meta_pixel_view import do_meta_pixel
import datetime, os

# Model
class Model:
    def __init__(self):
        self.create_pdf = True
        self.show_pdf = True
        self.show_image = True

        self.max_layers = 2
        self.max_shape_layers = 2
        self.shapes = 2**7
        self.save_layer_images = False

        self.files = 1
        self.radius = 5
        self.prob_do_transform = 1
        self.prob_shape_destination_equals_source = 1
        self.transparent_threshold = 128
        self.transparent_above_threshold = True

        # Edge detection
        self.edge_min = 100 # 0 - 255
        self.edge_max = 200
        self.edge_aperture = 3

        # Clustering
        self.eps = 20
        self.min_samples = 64

        self.accent_color_percentage = .02

        self.min_width_percentage = .01
        self.min_height_percentage = .02
        self.max_width_percentage = .1/GOLDEN_RATIO
        self.max_height_percentage = .2

        self.min_dx_percentage = - .1
        self.min_dy_percentage = - .1
        self.max_dx_percentage = .6
        self.max_dy_percentage = .6

        self.max_fill_alpha = 128
        self.min_fill_alpha = 32
        self.max_fill_red = 255
        self.min_fill_red = 192
        self.max_fill_green = 255
        self.min_fill_green = 128
        self.max_fill_blue = 64
        self.min_fill_blue = 32

        self.max_accent_alpha = 212
        self.min_accent_alpha = 192
        self.max_accent_red = 255
        self.min_accent_red = 192
        self.max_accent_green = 16
        self.min_accent_green = 0
        self.max_accent_blue = 16
        self.min_accent_blue = 0

        self.max_outline_alpha = 255
        self.min_outline_alpha = 128
        self.max_outline_red = 255
        self.min_outline_red = 0
        self.max_outline_green = 255
        self.min_outline_green = 0
        self.max_outline_blue = 255
        self.min_outline_blue = 0

        self.input_dir = 'input/'
        self.output_dir = 'output/'
        self.image_name = 'Rhythms_Circle_DataReferenceSet_1982_2'
        self.image_ext = '.png'
        self.input_path = f"{self.input_dir}/{self.image_name}{self.image_ext}"
        self.image_date = datetime.datetime.now().strftime('%Y%m%d')

# View
class BaseWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        tk.Toplevel.__init__(self, parent)
        self.controller = controller

""" class ParametersPage(BaseWindow):
    def __init__(self, parent, controller):
        BaseWindow.__init__(self, parent, controller)
        self.title("Meta Pixel: Parameters")
        label = tk.Label(self, text="Parameters of Meta Pixel")
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Generate",
                           command=lambda: controller.show_window("StatusPage"))
        button.pack() """

""" class StatusPage(BaseWindow):
    def __init__(self, parent, controller):
        BaseWindow.__init__(self, parent, controller)
        self.title("Meta Pixel: Status")
        label = tk.Label(self, text="Generating Meta Pixel")
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Go to Parameters Page",
                           command=lambda: controller.show_window("ParametersPage"))
        button.pack() """

# Controller
class Controller(tk.Tk):

    def __init__(self, model):
        tk.Tk.__init__(self)
        self.model = model
        self.title("Meta Pixel")
        self.geometry("800x600")

        # Create a frame for the content
        self.content_frame = tk.Frame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to make the layout responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Create a frame for files with 6 rows and 5 columns
        self.file_frame = tk.Frame(self.content_frame, relief="ridge", width=200, height=100)
        self.file_frame.grid(row=0, column=0, padx=10, sticky="nsew")

        # Configure grid weights for the file frame
        for i in range(6):
            self.file_frame.grid_rowconfigure(i, weight=1)

        self.file_frame.grid_columnconfigure(0, weight=2)
        self.file_frame.grid_columnconfigure(0, weight=2)
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(0, weight=0)

        # Initialize the files frame
        self.init_input_file()
        self.init_output_file()

        button_generate = tk.Button(self.content_frame, text="Generate Meta Pixel",
                        command=lambda: do_meta_pixel(self.model))
        button_generate.grid(row=0, column=0, padx=10, pady=10)
        
        '''

        # Create a frame for the generate button
        frame_generate = tk.Frame(self)
        frame_generate.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        button_generate = tk.Button(frame_generate, text="Generate Meta Pixel",
                        command=lambda: do_meta_pixel(self.model))
        button_generate.grid(row=0, column=0, padx=10, pady=10)

        # Configure grid weights to make the layout responsive
        self.grid_columnconfigure(0, weight=1)
        frame_input_path.grid_columnconfigure(0, weight=1)
        frame_input_path.grid_columnconfigure(1, weight=0)
        frame_generate.grid_columnconfigure(0, weight=1)
        '''
    def init_output_file(self):
        # Place a label "Output" in row 2, column 0
        self.label_output = tk.Label(self.file_frame, text="Output")
        self.label_output.grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # Entry for output_dir in row 3, column 0
        self.entry_output_dir = tk.Entry(self.file_frame)
        self.entry_output_dir.grid(row=3, column=0, padx=10, pady=0, sticky="ew")
        self.entry_output_dir.insert(0, self.model.output_dir)

        # Button for output_select
        self.button_output_select = tk.Button(self.file_frame, text="Select Output Directory", command=self.select_output_directory)
        self.button_output_select.grid(row=3, column=3, padx=10, pady=0, sticky="ew")

    def select_output_directory(self):
        directory =  filedialog.askdirectory(title="Select Output Directory")
        self.model.output_dir = directory

        self.entry_output_dir.delete(0, tk.END)
        self.entry_output_dir.insert(0, directory)

    def init_input_file(self):
        # Place a label "Input" in row 0, column 0
        self.label_input = tk.Label(self.file_frame, text="Input")
        self.label_input.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # Entry for input_dir in row 1, column 0
        self.entry_input_dir = tk.Entry(self.file_frame)
        self.entry_input_dir.grid(row=1, column=0, columnspan=1, padx=10, pady=0, sticky="ew")
        self.entry_input_dir.insert(0, self.model.input_dir)

        # Entry for input_name
        self.entry_input_name = tk.Entry(self.file_frame)
        self.entry_input_name.grid(row=1, column=2, columnspan=2, padx=10, pady=0, sticky="ew")
        self.entry_input_name.insert(0, self.model.image_name)

        # Entry for input_ext
        self.entry_input_ext = tk.Entry(self.file_frame)
        self.entry_input_ext.grid(row=1, column=4, padx=2, pady=0, sticky="ew")
        self.entry_input_ext.insert(0, self.model.image_ext)

        # Button for input_select
        self.button_input_select = tk.Button(self.file_frame, text="Select Input File", command=self.select_input_file)
        self.button_input_select.grid(row=1, column=5, padx=10, pady=0, sticky="ew")

    def select_input_file(self):
        files = [("PNG files", "*.png"), ("JPG files", "*.jpg")]
        input_path = filedialog.askopenfilename(title="Select input File", filetypes=files)
        self.model.input_path = input_path
        directory, name = os.path.split(input_path)
        name, ext = os.path.splitext(name)    
        self.model.input_dir = directory
        self.model.image_name = name
        self.model.image_ext = ext

        self.entry_input_dir.insert(0, directory)

        self.entry_input_name.delete(0, tk.END)
        self.entry_input_name.insert(0, name)

        self.entry_input_ext.delete(0, tk.END)
        self.entry_input_ext.insert(0, ext)

        if self.model.input_path:
            print(f"Selected file: {self.model.input_path}")



        """ 
        button_start = tk.Button(self, text="Generate Meta Pixel",
                                 command=lambda: self.show_window("ParametersPage"))
        button_start.pack(pady=10)

        button_page_one = tk.Button(self, text="Open Page One",
                                    command=lambda: self.show_window("PageOne"))
        button_page_one.pack(pady=10)
        """
        self.windows = {}

    def show_window(self, window_name):
        if window_name in self.windows:
            self.windows[window_name].deiconify()
        else:

            """ if window_name == "StartPage":
                window = StartPage(self, self)
            elif window_name == "PageOne":
                window = PageOne(self, self)
            self.windows[window_name] = window """

# Main Application
if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.mainloop()