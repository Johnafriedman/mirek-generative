from ttkwidgets.color import askcolor
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os, datetime, sys
from constants import GOLDEN_RATIO
import json, subprocess

from utilities import ImageWindow
from meta_pixel_view import do_meta_pixel

# Model
class Model:
    def __init__(self):

        self._initialized = False

        self.is_video = False
        self.create_pdf = False
        self.show_pdf = False
        self.show_image = True
        self._image = None

        # mesh
        self.do_mesh = False
        self.use_mask = True
        self.max_mesh_width = 4
        self.max_mesh_height = 6

        # perspective transform
        self.do_perspective = False

        self.max_layers = 2
        self.max_shape_layers = 2
        self.shapes = 2**7
        # self.save_layer_images = False
        self.files = 1

        self.do_blur = True
        self.blur_radius = 5
        self.do_scale = True
        self.scale_factor = 8
        self.do_invert = True
        self.prob_shape_destination_equals_source = 1
        self.transparent_threshold = 128
        self.transparent_above = True


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


        self.fill_color = [(255,255,64,128),(192,128,32,32)]
        self.accent_color = [(255,16,16,212),(192,192,0,192)]
        self.outline_color = [(255,255,255,255),(128,0,0,0)]
        self.cluster_color = [(65, 102, 224, 46), (168, 187, 242, 32)]


        self.input_dir = 'input'
        self.output_dir = 'output'
        self.image_name = 'Rhythms_Circle_DataReferenceSet_1982_2'
        self.image_ext = '.png'
        self.input_path = f"{self.input_dir}/{self.image_name}{self.image_ext}"
        self.image_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # preference file name for saving and loading
        self.pref_file = 'meta_pixel.prefs'
        self._initialized = True
        self._existing_attributes = set(self.__dict__.keys())


        # Override __setattr__ at runtime
        self.__setattr__ = self.custom_setattr

    def custom_setattr(self, name, value):
        if self._initialized and not hasattr(self, name):
            print(f"New attribute added: {name}")
        super(Model, self).__setattr__(name, value)
        self._existing_attributes.add(name)

    def load(self):

        with open(self.pref_file, 'r') as f:
            data = json.load(f)
            for key in data:
                setattr(self, key, data[key])

    def save(self):
        with open(self.pref_file, 'w') as f:
            data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
            try:
                json.dump(data, f, indent=4)
            except Exception as e:
                print(f"Error saving preferences: {e}")
                print(f"Data: {data}")


class Controller(tk.Tk):
    def __init__(self, model):
        tk.Tk.__init__(self)
        self.model = model
        self.title("Meta Pixel")
        self.geometry("1024x800")

        self.windows = []


        # Create the main content frame
        self.content_frame = tk.Frame(self, bg="lightgrey")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to make the layout responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.init_all_frames()

        # if preference file exists, load it
        if os.path.exists(self.model.pref_file):
            self.model.load()
            self.load_all_widgets()



        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_x()}+{self.winfo_y()}")

    def init_all_frames(self):
        self.init_file_frame()
        self.init_output_options_frame()
        self.init_mesh_frame()
        self.init_perspective_frame()
        self.init_shapes_frame()
        self.init_analysis_frame()
        self.init_color_frame()
        self.init_action_frame()

    def load_all_widgets(self):
        self.load_path_widgets()
        self.load_output_options_widgets()
        self.load_mesh_widgets()
        self.load_perspective_widgets()
        self.load_shapes_widgets()
        self.load_analsys_widgets()
        self.load_color_widgets()
        self.update_idletasks()

    def store_all_widgets(self):
        self.store_path_widgets()
        self.store_output_options_widgets()
        self.store_mesh_widgets()
        self.store_perspective_widgets()
        self.store_shapes_widgets()
        self.store_analysis_widgets()
        self.store_color_widgets()

    def init_file_frame(self):
        # Create a frame for files
        self.file_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightblue")
        self.file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the file frame
        """ for i in range(4):
            self.file_frame.grid_rowconfigure(i, weight=1)

        column_weights = [1,2,2,0,2]
        for i, weight in enumerate(column_weights):
            self.file_frame.grid_columnconfigure(i, weight=weight)
 """
        # Initialize the files frame
        self.init_input_file()
        self.init_output_file()

    #
    # Load Widgets from Model
    # 

    def load_output_options_widgets(self):
        self.entry_files.delete(0, tk.END)
        self.entry_files.insert(0, self.model.files)
        self.var_create_pdf.set(self.model.create_pdf)
        self.var_show_pdf.set(self.model.show_pdf)
        self.var_show_image.set(self.model.show_image)


    def load_path_widgets(self):
        self.entry_input_dir.delete(0, tk.END)
        self.entry_input_dir.insert(0, self.model.input_dir)

        self.entry_input_name.delete(0, tk.END)
        self.entry_input_name.insert(0, self.model.image_name)

        self.entry_input_ext.delete(0, tk.END)
        self.entry_input_ext.insert(0, self.model.image_ext)

        self.entry_output_dir.delete(0, tk.END)
        self.entry_output_dir.insert(0, self.model.output_dir)

    def load_shapes_widgets(self):
        self.entry_shapes.delete(0, tk.END)
        self.entry_shapes.insert(0, self.model.shapes)

        self.entry_max_layers.delete(0, tk.END)
        self.entry_max_layers.insert(0, self.model.max_layers)

        self.entry_max_shape_layers.delete(0, tk.END)
        self.entry_max_shape_layers.insert(0, self.model.max_shape_layers)

        self.var_do_blur.set(self.model.do_blur)
        self.entry_blur_radius.delete(0, tk.END)
        self.entry_blur_radius.insert(0, self.model.blur_radius)

        self.var_do_scale.set(self.model.do_scale)
        self.entry_scale_factor.delete(0, tk.END)
        self.entry_scale_factor.insert(0, self.model.scale_factor)

        self.var_do_invert.set(self.model.do_invert)

        self.scale_min_width_percentage.set(self.model.min_width_percentage)
        self.scale_max_width_percentage.set(self.model.max_width_percentage)
        self.scale_min_height_percentage.set(self.model.min_height_percentage)
        self.scale_max_height_percentage.set(self.model.max_height_percentage)

        self.scale_min_dx_percentage.set(self.model.min_dx_percentage)
        self.scale_max_dx_percentage.set(self.model.max_dx_percentage)
        self.scale_min_dy_percentage.set(self.model.min_dy_percentage)
        self.scale_max_dy_percentage.set(self.model.max_dy_percentage)

        self.scale_dx_dy_eq_sx_sy.set(self.model.prob_shape_destination_equals_source)

    def load_mesh_widgets(self):
        self.var_do_mesh.set(self.model.do_mesh)
        self.var_use_mask.set(self.model.use_mask)
        self.entry_max_mesh_width.delete(0, tk.END)
        self.entry_max_mesh_width.insert(0, self.model.max_mesh_width)
        self.entry_max_mesh_height.delete(0, tk.END)
        self.entry_max_mesh_height.insert(0, self.model.max_mesh_height)

    def load_perspective_widgets(self):
        self.var_do_perspective.set(self.model.do_perspective)
        self.var_use_mask.set(self.model.use_mask)


    def load_analsys_widgets(self):
        self.entry_edge_min.delete(0, tk.END)
        self.entry_edge_min.insert(0, self.model.edge_min)

        self.entry_edge_max.delete(0, tk.END)
        self.entry_edge_max.insert(0, self.model.edge_max)

        self.entry_edge_aperture.delete(0, tk.END)
        self.entry_edge_aperture.insert(0, self.model.edge_aperture)

        self.entry_eps.delete(0, tk.END)
        self.entry_eps.insert(0, self.model.eps)

        self.entry_min_samples.delete(0, tk.END)
        self.entry_min_samples.insert(0, self.model.min_samples)

    def load_color_widgets(self):
        self.scale_transparent_threshold.set(self.model.transparent_threshold)
        self.var_transparent_above.set(self.model.transparent_above)
        self.scale_accent_color_percentage.set(self.model.accent_color_percentage)
        self.load_gradient_widgets()

    def load_gradient_widgets(self):
        self.draw_gradient(self.__dict__["fill_canvas_gradient"], self.model.fill_color[0], self.model.fill_color[1])
        self.draw_gradient(self.__dict__["outline_canvas_gradient"], self.model.outline_color[0], self.model.outline_color[1])
        self.draw_gradient(self.__dict__["accent_canvas_gradient"], self.model.accent_color[0], self.model.accent_color[1])
        self.draw_gradient(self.__dict__["cluster_canvas_gradient"], self.model.cluster_color[0], self.model.cluster_color[1])

    #
    # Store Widgets in Model 
    #

    def store_path_widgets(self):
        self.model.input_dir = self.entry_input_dir.get()
        self.model.image_name = self.entry_input_name.get()
        self.model.image_ext = self.entry_input_ext.get()
        self.model.output_dir = self.entry_output_dir.get()

    def store_output_options_widgets(self):
        self.model.files = int(self.entry_files.get())
        self.model.create_pdf = self.var_create_pdf.get()
        if self.model.create_pdf:
            self.model.show_pdf = self.var_show_pdf.set(True)
            self.check_show_pdf.config(state="normal")    
        else:
            self.model.show_pdf = False
            self.check_show_pdf.deselect()
            #disable the show_pdf checkbutton
            self.check_show_pdf.config(state="disabled")    
        self.model.show_image = self.var_show_image.get()

    def store_mesh_widgets(self):
        self.model.do_mesh = self.var_do_mesh.get()
        if self.model.do_mesh:
            self.check_use_mask.config(state="normal")
            self.entry_max_mesh_width.config(state="normal")
            self.entry_max_mesh_height.config(state="normal")
            self.model.use_mask = self.var_use_mask
            self.model.max_mesh_width = int(self.entry_max_mesh_width.get())
            self.model.max_mesh_height = int(self.entry_max_mesh_height.get())
        else:
            # disable the remaining mesh widgets
            self.check_use_mask.config(state="disabled")
            self.entry_max_mesh_width.config(state="disabled")
            self.entry_max_mesh_height.config(state="disabled")

    def store_perspective_widgets(self):
        self.model.do_perspective = self.var_do_perspective.get()
        if self.model.do_perspective:
            self.check_use_mask.config(state="normal")
            self.model.use_mask = self.var_use_mask.get()
        else:
            # disable the remaining perspective widgets
            self.check_use_mask.config(state="disabled")



    def store_shapes_widgets(self):
        self.model.shapes = int(self.entry_shapes.get())
        self.model.max_layers = int(self.entry_max_layers.get())
        self.model.max_shape_layers = int(self.entry_max_shape_layers.get())
        self.model.do_blur = self.var_do_blur.get()
        self.model.blur_radius = int(self.entry_blur_radius.get())
        self.model.do_scale = self.var_do_scale.get()
        self.model.scale_factor = int(self.entry_scale_factor.get())
        self.model.do_invert = self.var_do_invert.get()

    def store_analysis_widgets(self):
        self.model.edge_min = int(self.entry_edge_min.get())
        self.model.edge_max = int(self.entry_edge_max.get())
        self.model.edge_aperture = int(self.entry_edge_aperture.get())
        self.model.eps = int(self.entry_eps.get())
        self.model.min_samples = int(self.entry_min_samples.get())

    def store_color_widgets(self):
        self.model.transparent_threshold = int(self.scale_transparent_threshold.get())

        self.model.accent_color_percentage = self.scale_accent_color_percentage.get()

        # self.model.accent_color_percentage = float(self.entry_accent_color_percentage.get())
        self.model.transparent_above = self.var_transparent_above.get()

# 
# Initialize the frames
# 

    def init_input_file(self):

        # Entry for input_dir in row 1, column 0
        self.entry_input_dir = tk.Entry(self.file_frame)
        self.entry_input_dir.grid(row=0, column=0, padx=10, pady=0, sticky="ew")
        self.entry_input_dir.insert(0, self.model.input_dir)

        # Entry for input_name
        self.entry_input_name = tk.Entry(self.file_frame)
        self.entry_input_name.grid(row=0, column=1, padx=10, pady=0, sticky="ew")
        self.entry_input_name.insert(0, self.model.image_name)

        # Entry for input_ext
        self.entry_input_ext = tk.Entry(self.file_frame)
        self.entry_input_ext.grid(row=0, column=2, padx=2, pady=0, sticky="ew")
        self.entry_input_ext.insert(0, self.model.image_ext)

        # Button for input_select
        self.button_input_select = tk.Button(self.file_frame, text="Select Input File", command=self.select_input_file)
        self.button_input_select.grid(row=0, column=3, padx=10, pady=0, sticky="ew")

    def get_relative_or_absolute_path(self, file_path):
        if not file_path:
            return file_path
        try:
            # Get the absolute path of the file
            absolute_path = os.path.abspath(file_path)
            # Get the common prefix between the file path and the current working directory
            common_prefix = os.path.commonprefix([absolute_path, os.getcwd()])
            # If the common prefix is the current working directory, return the relative path
            if common_prefix == os.getcwd():
                return os.path.relpath(file_path)
            else:
                return absolute_path
        except Exception as e:
            print(f"Error determining path: {e}")
            return file_path
        
    def select_input_file(self):
        files = [("Image files", ".png .jpeg .jpg"), ("Video files", ".mp4 .mov")]
        input_path = filedialog.askopenfilename(title="Select input File", filetypes=files, initialdir=self.model.input_dir)
        if not input_path:
            return
        input_path = self.get_relative_or_absolute_path(input_path)
        self.model.input_path = input_path
        directory, name = os.path.split(input_path)

        name, ext = os.path.splitext(name)    
        self.model.input_dir = directory
        self.model.image_name = name
        self.model.image_ext = ext
        if ext.lower() == ".mp4" or ext.lower() == ".mov":
            self.model.is_video = True 
            self.create_pdf = self.var_create_pdf.set(False)
            self.show_pdf = self.var_show_pdf.set(False)
            self.show_image = self.var_show_image.set(False)


        self.entry_input_dir.delete(0, tk.END)
        self.entry_input_dir.insert(0, directory)

        self.entry_input_name.delete(0, tk.END)
        self.entry_input_name.insert(0, name)

        self.entry_input_ext.delete(0, tk.END)
        self.entry_input_ext.insert(0, ext)


    def init_output_file(self):
        # Place a label "Output" in row 1, column 0
        self.label_output = tk.Label(self.file_frame, text="Output")
        self.label_output.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        # Entry for output_dir in row 1, column 0
        self.entry_output_dir = tk.Entry(self.file_frame)
        self.entry_output_dir.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        self.entry_output_dir.insert(0, self.model.output_dir)

        # Button for output_select
        self.button_output_select = tk.Button(self.file_frame, text="Select Output Directory", command=self.select_output_directory)
        self.button_output_select.grid(row=1, column=3, padx=10, pady=0, sticky="ew")

    def select_output_directory(self):
        # Functionality to select output directory
        self.model.output_dir = filedialog.askdirectory(initialdir=self.model.output_dir)
        self.entry_output_dir.delete(0, tk.END)
        self.entry_output_dir.insert(0, self.model.output_dir)


    def init_output_options_frame(self):
        self.output_options_frame = tk.Frame(self.content_frame, relief="ridge", bg="blue")
        self.output_options_frame.grid(row=3, column=0, padx=10, sticky="nsew")
        self.init_output_options()

    def init_output_options(self):

        # Label for files
        self.label_files = tk.Label(self.output_options_frame, text="Files")
        self.label_files.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # Entry for files
        self.entry_files = tk.Entry(self.output_options_frame)
        self.entry_files.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        self.entry_files.insert(0, self.model.files)

        # Checkbutton for create_pdf
        self.var_create_pdf = tk.BooleanVar(value=self.model.create_pdf)
        self.check_create_pdf = tk.Checkbutton(self.output_options_frame, text="Create PDF", variable=self.var_create_pdf, command=self.store_output_options_widgets)
        self.check_create_pdf.grid(row=0, column=2, padx=10, pady=0, sticky="w")

        # Checkbutton for show_pdf
        self.var_show_pdf = tk.BooleanVar(value=self.model.show_pdf)
        self.check_show_pdf = tk.Checkbutton(self.output_options_frame, text="Show PDF", variable=self.var_show_pdf, command=self.store_output_options_widgets)
        self.check_show_pdf.grid(row=0, column=3, padx=10, pady=0, sticky="w")

        # Checkbutton for show_image
        self.var_show_image = tk.BooleanVar(value=self.model.show_image)
        self.check_show_image = tk.Checkbutton(self.output_options_frame, text="Show Image", variable=self.var_show_image, command=self.store_output_options_widgets)
        self.check_show_image.grid(row=0, column=4, padx=10, pady=0, sticky="w")

        #AskOpenFile preferences file
        self.button_save = tk.Button(self.output_options_frame, text="Save Preferences", command=self.select_save_prefs)
        self.button_save.grid(row=0, column=5, padx=10, pady=0, sticky="w")

        #AskOpenFile preferences file
        self.button_load = tk.Button(self.output_options_frame, text="Load Preferences", command=self.select_load_prefs)   
        self.button_load.grid(row=0, column=6, padx=10, pady=0, sticky="w")

    def select_save_prefs(self):
        pref_file = filedialog.asksaveasfilename(initialdir='.', title="Save Preferences", filetypes=([("Prefs files", "*.prefs")]), initialfile=self.model.image_name)
        if pref_file:
            self.store_all_widgets()
            self.model.pref_file = pref_file
            self.model.save()

    def select_load_prefs(self):
        pref_file = filedialog.askopenfilename(initialdir='.', title="Load Preferences", filetypes=([("Prefs files", "*.prefs")]))
        if pref_file:
            self.model.pref_file = pref_file
            self.model.load()
            self.load_all_widgets()


# 
# Initialize the mesh frames
#

    def init_mesh_frame(self):
        # Create a frame for mesh
        self.mesh_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.mesh_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the mesh frame
        self.mesh_frame.grid_rowconfigure(0, weight=1)
        for i in range(6):
            self.mesh_frame.grid_columnconfigure(i, weight=1)

        self.init_mesh_widgets()

    def init_mesh_widgets(self):

        # Checkbutton for do_mesh
        self.var_do_mesh = tk.BooleanVar(value=self.model.do_mesh)
        self.check_do_mesh = tk.Checkbutton(self.mesh_frame, text="Mesh", variable=self.var_do_mesh, command=self.store_mesh_widgets)
        self.check_do_mesh.grid(row=0, column=1, padx=10, pady=0, sticky="w")

        # Checkbutton for use_mask
        self.var_use_mask = tk.BooleanVar(value=self.model.use_mask)
        self.check_use_mask = tk.Checkbutton(self.mesh_frame, text="Mask", variable=self.var_use_mask)
        self.check_use_mask.grid(row=0, column=2, padx=10, pady=0, sticky="w")

        # Label for max_mesh_width
        self.label_max_mesh_width = tk.Label(self.mesh_frame, text="Max Columns")
        self.label_max_mesh_width.grid(row=0, column=3, padx=10, pady=0, sticky="w")

        # Entry for max_mesh_width
        self.entry_max_mesh_width = tk.Entry(self.mesh_frame)
        self.entry_max_mesh_width.grid(row=0, column=4, padx=0, pady=0, sticky="ew")
        self.entry_max_mesh_width.insert(0, self.model.max_mesh_width)

        # Label for max_mesh_height
        self.label_max_mesh_height = tk.Label(self.mesh_frame, text="Max Rows")
        self.label_max_mesh_height.grid(row=0, column=5, padx=10, pady=0, sticky="w")

        # Entry for max_mesh_height
        self.entry_max_mesh_height = tk.Entry(self.mesh_frame)
        self.entry_max_mesh_height.grid(row=0, column=6, padx=0, pady=0, sticky="ew")
        self.entry_max_mesh_height.insert(0, self.model.max_mesh_height)

    def init_perspective_frame(self):
        # Create a frame for perspective
        self.perspective_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.perspective_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the perspective frame
        self.perspective_frame.grid_rowconfigure(0, weight=1)
        for i in range(6):
            self.perspective_frame.grid_columnconfigure(i, weight=1)

        self.init_perspective_widgets()

    def init_perspective_widgets(self):

        # Checkbutton for do_perspective
        self.var_do_perspective = tk.BooleanVar(value=self.model.do_perspective)
        self.check_do_perspective = tk.Checkbutton(self.perspective_frame, text="perspective", variable=self.var_do_perspective, command=self.store_perspective_widgets)
        self.check_do_perspective.grid(row=0, column=1, padx=10, pady=0, sticky="w")

        # Checkbutton for use_mask
        self.var_use_mask = tk.BooleanVar(value=self.model.use_mask)
        self.check_use_mask = tk.Checkbutton(self.perspective_frame, text="Mask", variable=self.var_use_mask)
        self.check_use_mask.grid(row=0, column=2, padx=10, pady=0, sticky="w")

    def init_shapes_frame(self):
        # Create a frame for shapes
        self.shapes_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.shapes_frame.grid(row=8, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the shapes frame
        for i in range(13):
            self.shapes_frame.grid_rowconfigure(i, weight=1)
        self.shapes_frame.grid_columnconfigure(0, weight=1)
        self.shapes_frame.grid_columnconfigure(1, weight=1)

        # Add sub-frames within the shapes frame
        self.shapes_sub_frame1 = tk.Frame(self.shapes_frame, relief="ridge", bg="lightblue")
        self.shapes_sub_frame1.grid(row=0, column=0, rowspan=13, padx=5, pady=5, sticky="nsew")

        self.shapes_sub_frame2 = tk.Frame(self.shapes_frame, relief="ridge", bg="lightgreen")
        self.shapes_sub_frame2.grid(row=0, column=1, rowspan=13, padx=5, pady=5, sticky="nsew")
        self.init_shapes_widgets()

    def init_shapes_width_height(self):
        def set_min_width(value):
            self.model.min_width_percentage = float(value)

        def set_max_width(value):
            self.model.max_width_percentage = float(value)

        # Label for width
        self.label_width = tk.Label(self.shapes_sub_frame2, text="Width: min/max")
        self.label_width.grid(row=0, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_width_percentage
        self.scale_min_width_percentage = tk.Scale(self.shapes_sub_frame2, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_width)
        self.scale_min_width_percentage.grid(row=0, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_width_percentage.set(self.model.min_width_percentage)

        # Scale for max_width_percentage
        self.scale_max_width_percentage = tk.Scale(self.shapes_sub_frame2, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_width)
        self.scale_max_width_percentage.grid(row=0, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_width_percentage.set(self.model.max_width_percentage)        
        
        def set_min_height(value):
            self.model.min_height_percentage = float(value)

        def set_max_height(value):
            self.model.max_height_percentage = float(value)

        # Label for height
        self.label_height = tk.Label(self.shapes_sub_frame2, text="Height: min/max")
        self.label_height.grid(row=1, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_height_percentage
        self.scale_min_height_percentage = tk.Scale(self.shapes_sub_frame2, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_height)
        self.scale_min_height_percentage.grid(row=1, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_height_percentage.set(self.model.min_height_percentage)

        # Scale for max_height_percentage
        self.scale_max_height_percentage = tk.Scale(self.shapes_sub_frame2, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_height)
        self.scale_max_height_percentage.grid(row=1, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_height_percentage.set(self.model.max_height_percentage)

    def init_shapes_dx_dy(self):
        def set_min_dx(value):
            self.model.min_dx_percentage = float(value)

        def set_max_dx(value):
            self.model.max_dx_percentage = float(value)

        # Label for dx
        self.label_dx = tk.Label(self.shapes_sub_frame2, text="Dx: min/max")
        self.label_dx.grid(row=2, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_dx_percentage
        self.scale_min_dx_percentage = tk.Scale(self.shapes_sub_frame2, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_dx)
        self.scale_min_dx_percentage.grid(row=2, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_dx_percentage.set(self.model.min_dx_percentage)

        # Scale for max_dx_percentage
        self.scale_max_dx_percentage = tk.Scale(self.shapes_sub_frame2, from_=-.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_dx)
        self.scale_max_dx_percentage.grid(row=2, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_dx_percentage.set(self.model.max_dx_percentage)        
        
        def set_min_dy(value):
            self.model.min_dy_percentage = float(value)

        def set_max_dy(value):
            self.model.max_dy_percentage = float(value)

        def set_dx_dy_eq_sx_sy(value):
            self.model.prob_shape_destination_equals_source = float(value)

        # Label for dy
        self.label_dy = tk.Label(self.shapes_sub_frame2, text="Dy: min/max")
        self.label_dy.grid(row=3, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_dy_percentage
        self.scale_min_dy_percentage = tk.Scale(self.shapes_sub_frame2, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_dy)
        self.scale_min_dy_percentage.grid(row=3, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_dy_percentage.set(self.model.min_dy_percentage)

        # Scale for max_dy_percentage
        self.scale_max_dy_percentage = tk.Scale(self.shapes_sub_frame2, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_dy)
        self.scale_max_dy_percentage.grid(row=3, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_dy_percentage.set(self.model.max_dy_percentage)

        # Label for prob dx,dy = sx,sy
        self.label_dx_dy_eq_sx_sy = tk.Label(self.shapes_sub_frame2, text="prob dest == src")
        self.label_dx_dy_eq_sx_sy.grid(row=4, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_dy_percentage
        self.scale_dx_dy_eq_sx_sy = tk.Scale(self.shapes_sub_frame2, from_= 0.0, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, command=set_dx_dy_eq_sx_sy)
        self.scale_dx_dy_eq_sx_sy.grid(row=4, column=3, padx=10, pady=0, sticky="ew")
        self.scale_dx_dy_eq_sx_sy.set(self.model.prob_shape_destination_equals_source)


    def init_shapes_widgets(self):
        # Label for shapes
        self.label_shapes = tk.Label(self.shapes_sub_frame1, text="Shapes")
        self.label_shapes.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # Entry for shapes
        self.entry_shapes = tk.Entry(self.shapes_sub_frame1)
        self.entry_shapes.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        self.entry_shapes.insert(0, self.model.shapes)

        # Label for max_layers
        self.label_max_layers = tk.Label(self.shapes_sub_frame1, text="Max Layers")
        self.label_max_layers.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        # Entry for max_layers
        self.entry_max_layers = tk.Entry(self.shapes_sub_frame1)
        self.entry_max_layers.grid(row=1, column=1, padx=0, pady=0, sticky="ew")
        self.entry_max_layers.insert(0, self.model.max_layers)

        # Label for max_shape_layers
        self.label_max_shape_layers = tk.Label(self.shapes_sub_frame1, text="Max Shape Layers")
        self.label_max_shape_layers.grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # Entry for max_shape_layers
        self.entry_max_shape_layers = tk.Entry(self.shapes_sub_frame1)
        self.entry_max_shape_layers.grid(row=2, column=1, padx=0, pady=0, sticky="ew")
        self.entry_max_shape_layers.insert(0, self.model.max_shape_layers)

        # Checkbutton for do_blur
        self.var_do_blur = tk.BooleanVar(value=self.model.do_blur)
        self.check_do_blur = tk.Checkbutton(self.shapes_sub_frame1, text="Blur Radius", variable=self.var_do_blur)
        self.check_do_blur.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        # Entry for radius
        self.entry_blur_radius = tk.Entry(self.shapes_sub_frame1)
        self.entry_blur_radius.grid(row=3, column=1, padx=0, pady=0, sticky="ew")
        self.entry_blur_radius.insert(0, self.model.blur_radius)

        # Checkbutton for scale
        self.var_do_scale = tk.BooleanVar(value=self.model.do_scale)
        self.check_do_scale = tk.Checkbutton(self.shapes_sub_frame1, text="Scale", variable=self.var_do_scale)
        self.check_do_scale.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        # Entry for scale
        self.entry_scale_factor = tk.Entry(self.shapes_sub_frame1)
        self.entry_scale_factor.grid(row=4, column=1, padx=0, pady=0, sticky="ew")
        self.entry_scale_factor.insert(0, self.model.scale_factor)

        # Checkbutton for invert
        self.var_do_invert = tk.BooleanVar(value=self.model.do_invert)
        self.check_do_invert = tk.Checkbutton(self.shapes_sub_frame1, text="Invert", variable=self.var_do_invert)
        self.check_do_invert.grid(row=5, column=0, padx=10, pady=0, sticky="w")

        self.init_shapes_width_height()
        self.init_shapes_dx_dy()


    def init_analysis_frame(self):
        # Create a frame for analysis
        self.analysis_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.analysis_frame.grid(row=15, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the analysis frame
        for i in range(5):
            self.analysis_frame.grid_rowconfigure(i, weight=1)
        self.analysis_frame.grid_columnconfigure(0, weight=1)
        self.analysis_frame.grid_columnconfigure(1, weight=1)

        # Add sub-frames within the analysis frame
        self.analysis_sub_frame1 = tk.Frame(self.analysis_frame, relief="ridge", bg="lightyellow")
        self.analysis_sub_frame1.grid(row=0, column=0, rowspan=5, padx=5, pady=5, sticky="nsew")

        self.analysis_sub_frame2 = tk.Frame(self.analysis_frame, relief="ridge", bg="lightpink")
        self.analysis_sub_frame2.grid(row=0, column=1, rowspan=5, padx=5, pady=5, sticky="nsew")

        self.init_analysis_widgets()
       
    def init_analysis_widgets(self):
        # Label for edge detection
        self.label_edge_detection = tk.Label(self.analysis_sub_frame1, text="Edge Detection")   
        self.label_edge_detection.grid(row=0, column=0, padx=10, pady=0, sticky="w")    

        # Label for edge_min
        self.label_edge_min = tk.Label(self.analysis_sub_frame1, text="Edge Min")   
        self.label_edge_min.grid(row=1, column=0, padx=10, pady=0, sticky="w")  

        # Entry for edge_min
        self.entry_edge_min = tk.Entry(self.analysis_sub_frame1)    
        self.entry_edge_min.grid(row=1, column=1, padx=0, pady=0, sticky="ew")  
        self.entry_edge_min.insert(0, self.model.edge_min)

        # Label for edge_max
        self.label_edge_max = tk.Label(self.analysis_sub_frame1, text="Edge Max")   
        self.label_edge_max.grid(row=2, column=0, padx=10, pady=0, sticky="w")  

        # Entry for edge_max
        self.entry_edge_max = tk.Entry(self.analysis_sub_frame1)    
        self.entry_edge_max.grid(row=2, column=1, padx=0, pady=0, sticky="ew")  
        self.entry_edge_max.insert(0, self.model.edge_max)

        # Label for edge_aperture
        self.label_edge_aperture = tk.Label(self.analysis_sub_frame1, text="Edge Aperture") 
        self.label_edge_aperture.grid(row=3, column=0, padx=10, pady=0, sticky="w") 
        
        # Entry for edge_aperture
        self.entry_edge_aperture = tk.Entry(self.analysis_sub_frame1)   
        self.entry_edge_aperture.grid(row=3, column=1, padx=0, pady=0, sticky="ew") 
        self.entry_edge_aperture.insert(0, self.model.edge_aperture)    

        # Label for clustering
        self.label_clustering = tk.Label(self.analysis_sub_frame2, text="Clustering") 
        self.label_clustering.grid(row=0, column=0, padx=10, pady=0, sticky="w")    

        # Label for eps
        self.label_eps = tk.Label(self.analysis_sub_frame2, text="Eps") 
        self.label_eps.grid(row=1, column=0, padx=10, pady=0, sticky="w")   

        # Entry for eps
        self.entry_eps = tk.Entry(self.analysis_sub_frame2)
        self.entry_eps.grid(row=1, column=1, padx=0, pady=0, sticky="ew")   
        self.entry_eps.insert(0, self.model.eps)

        # Label for min_samples
        self.label_min_samples = tk.Label(self.analysis_sub_frame2, text="Min Samples") 
        self.label_min_samples.grid(row=2, column=0, padx=10, pady=0, sticky="w")   

        # Entry for min_samples
        self.entry_min_samples = tk.Entry(self.analysis_sub_frame2) 
        self.entry_min_samples.grid(row=2, column=1, padx=0, pady=0, sticky="ew")   
        self.entry_min_samples.insert(0, self.model.min_samples)    
        
    def init_color_frame(self):
        # Create a frame for colors
        self.color_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.color_frame.grid(row=16, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights for the color frame
        for i in range(5):
            self.color_frame.grid_rowconfigure(i, weight=1)
        self.color_frame.grid_columnconfigure(0, weight=1)
        self.color_frame.grid_columnconfigure(1, weight=1)

        # Add sub-frames within the color frame
        self.color_sub_frame1 = tk.Frame(self.color_frame, relief="ridge", bg="lightyellow")
        self.color_sub_frame1.grid(row=0, column=0, rowspan=5, padx=5, pady=5, sticky="nsew")

        self.color_sub_frame2 = tk.Frame(self.color_frame, relief="ridge", bg="lightpink")
        self.color_sub_frame2.grid(row=0, column=1, rowspan=5, padx=5, pady=5, sticky="nsew")

        self.init_color_widgets()

    def init_color_widgets(self):
        # Label for transparent_threshold   
        self.label_transparent_threshold = tk.Label(self.color_sub_frame2, text="Transparent Threshold")
        self.label_transparent_threshold.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # Scale for accent color percentage
        self.scale_transparent_threshold = tk.Scale(self.color_sub_frame2, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL)
        self.scale_transparent_threshold.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        self.scale_transparent_threshold.set(self.model.transparent_threshold)
        
        # self.entry_transparent_threshold = tk.Entry(self.color_sub_frame2)
        # self.entry_transparent_threshold.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        # self.entry_transparent_threshold.insert(0, self.model.transparent_threshold)

        self.label_accent_color_percentage = tk.Label(self.color_sub_frame2, text="Accent Color %")
        self.label_accent_color_percentage.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Scale for accent color percentage
        self.scale_accent_color_percentage = tk.Scale(self.color_sub_frame2, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL)
        self.scale_accent_color_percentage.grid(row=4, column=1, padx=0, pady=0, sticky="ew")
        self.scale_accent_color_percentage.set(self.model.accent_color_percentage)

        # Checkbutton for transparent_above
        self.var_transparent_above = tk.BooleanVar(value=self.model.transparent_above)
        self.check_transparent_above = tk.Checkbutton(self.color_sub_frame2, text="Transparent above", variable=self.var_transparent_above)
        self.check_transparent_above.grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # initialize the fill color widgets
        self.init_color_widget(self.color_sub_frame1, 0, 0, "fill", 0)
        self.initialize_gradient_widgets(self.color_sub_frame1, 0, 2, "fill")
        self.init_color_widget(self.color_sub_frame1, 0, 2, "fill", 1)

        # initialize the outline color widgets
        self.init_color_widget(self.color_sub_frame1, 1, 0, "outline", 0)
        self.initialize_gradient_widgets(self.color_sub_frame1, 1, 2, "outline")
        self.init_color_widget(self.color_sub_frame1, 1, 2, "outline", 1)

        # initialize the accent color widgets
        self.init_color_widget(self.color_sub_frame1, 2, 0, "accent", 0)
        self.initialize_gradient_widgets(self.color_sub_frame1, 2, 2, "accent")
        self.init_color_widget(self.color_sub_frame1, 2, 2, "accent", 1)

        # initialize the cluster color widgets
        self.init_color_widget(self.color_sub_frame1, 3, 0, "cluster", 0)
        self.initialize_gradient_widgets(self.color_sub_frame1, 3, 2, "cluster")
        self.init_color_widget(self.color_sub_frame1, 3, 2, "cluster", 1)

    
    def initialize_gradient_widgets(self, frame, row, column, type):
        smd = self.model.__dict__
        sd = self.__dict__
        grd = f"{type}_canvas_gradient"


        # Create a canvas to display the gradient
        sd[grd] = tk.Canvas(frame, width=200, height=20)
        sd[grd].grid(row=row, column=column, padx=10, pady=0, sticky="ew")

        # Draw the gradient
        self.draw_gradient(sd[grd], smd[f"{type}_color"][0], smd[f"{type}_color"][1])

    def draw_gradient(self, canvas, color1, color2):
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        limit = width

        r1, g1, b1, a1 = color1
        r2, g2, b2, a2 = color2

        for i in range(limit):
            r = int(r1 + (r2 - r1) * i / limit)
            g = int(g1 + (g2 - g1) * i / limit)
            b = int(b1 + (b2 - b1) * i / limit)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(i, 0, i, height, fill=color)
        
    def init_color_widget(self, frame, row, column, type, index):
        smd = self.model.__dict__
        clr = f"{type}_color"
        sd = self.__dict__
        sd[f"button_{type}_color_{index}"] = tk.Button(frame, text=f"Select {type.capitalize()} Color {index}", command=lambda: self.select_color(smd[clr][index], type, index))
        sd[f"button_{type}_color_{index}"].grid(row=row, column=column+1, padx=0, pady=0, sticky="ew")

    def select_color(self, current_color, type, index):
    # Functionality to select fill color
        color_code = askcolor(title=f"Choose {type} Color {index}", color=current_color, alpha=True)
        if color_code[0]:
            self.model.__dict__[f"{type}_color"][index] = color_code[0]
            self.draw_gradient(self.__dict__[f"{type}_canvas_gradient"], self.model.__dict__[f"{type}_color"][0], self.model.__dict__[f"{type}_color"][1])
            print(self.model.__dict__[f"{type}_color"][index])

    def set_image_date(self):
        self.model.image_date = datetime.datetime.now().strftime("%Y-%m-%d%H%M%S")
    def generate(self):
        self.store_all_widgets()
        self.set_image_date()
        # Functionality to generate meta pixel
        self.button_generate.config(state="disabled")
        do_meta_pixel(self.model)
        # image_window = ImageWindow(self, self.model._image, self.model)
        # self.windows.append(image_window)
        # image_window.open()
        self.button_generate.config(state="normal")

    def fisheye(self):
        self.store_all_widgets()
        self.set_image_date()

        # execute fisheye.py in the terminal with commandline parameters        
        # Functionality to generate fisheye
        self.button_fisheye.config(state="disabled")
        subprocess.Popen(["python", "./mirek-generative/fisheye.py", self.model.input_path, self.model.output_dir])
        self.button_fisheye.config(state="normal")

    def exit(self):
        # Functionality to exit the application
        self.quit()

    
    def init_action_frame(self):
        # Create a frame for actions
        self.action_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightcoral")
        self.action_frame.grid(row=23, column=0, padx=10, pady=10, sticky="ews")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        self.action_frame.grid_columnconfigure(2, weight=1)

        button_exit = tk.Button(self.action_frame, text="Exit", command=self.exit)
        button_exit.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.button_generate = tk.Button(self.action_frame, text="Generate", command=self.generate)
        self.button_generate.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        self.button_fisheye = tk.Button(self.action_frame, text="Fisheye", command=self.fisheye)
        self.button_fisheye.grid(row=0, column=2, padx=10, pady=10, sticky="e")



if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.mainloop()