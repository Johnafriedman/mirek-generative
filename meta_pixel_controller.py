from ttkwidgets.color import askcolor
import tkinter as tk
from tkinter import filedialog
import os, datetime
from constants import GOLDEN_RATIO

from meta_pixel_view import do_meta_pixel


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


        self.fill_color = [(255,255,64,128),(192,128,32,32)]
        self.accent_color = [(255,16,16,212),(192,192,0,192)]
        self.outline_color = [(255,255,255,255),(128,0,0,0)]

        self.input_dir = 'input'
        self.output_dir = 'output'
        self.image_name = 'Rhythms_Circle_DataReferenceSet_1982_2'
        self.image_ext = '.png'
        self.input_path = f"{self.input_dir}/{self.image_name}{self.image_ext}"
        self.image_date = datetime.datetime.now().strftime('%Y%m%d')


class Controller(tk.Tk):
    def __init__(self, model):
        tk.Tk.__init__(self)
        self.model = model
        self.title("Meta Pixel")
        self.geometry("800x600")

        # Create the main content frame
        self.content_frame = tk.Frame(self, bg="lightgrey")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights to make the layout responsive
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        """         self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1) """

        self.init_file_frame()
        self.init_output_options_frame()
        self.init_shapes_frame()
        self.init_color_frame()
        self.init_action_frame()

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
        files = [("PNG files", "*.png"), ("JPG files", "*.jpg")]
        input_path = filedialog.askopenfilename(title="Select input File", filetypes=files, initialdir=self.model.input_dir)
        input_path = self.get_relative_or_absolute_path(input_path)
        self.model.input_path = input_path
        directory, name = os.path.split(input_path)

        name, ext = os.path.splitext(name)    
        self.model.input_dir = directory
        self.model.image_name = name
        self.model.image_ext = ext

        self.entry_input_dir.delete(0, tk.END)
        self.entry_input_dir.insert(0, directory)

        self.entry_input_name.delete(0, tk.END)
        self.entry_input_name.insert(0, name)

        self.entry_input_ext.delete(0, tk.END)
        self.entry_input_ext.insert(0, ext)

        if self.model.input_path:
            print(f"Selected file: {self.model.input_path}")

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
        self.check_create_pdf = tk.Checkbutton(self.output_options_frame, text="Create PDF", variable=self.var_create_pdf)
        self.check_create_pdf.grid(row=0, column=2, padx=10, pady=0, sticky="w")

        # Checkbutton for show_pdf
        self.var_show_pdf = tk.BooleanVar(value=self.model.show_pdf)
        self.check_show_pdf = tk.Checkbutton(self.output_options_frame, text="Show PDF", variable=self.var_show_pdf)
        self.check_show_pdf.grid(row=0, column=3, padx=10, pady=0, sticky="w")

        # Checkbutton for show_image
        self.var_show_image = tk.BooleanVar(value=self.model.show_image)
        self.check_show_image = tk.Checkbutton(self.output_options_frame, text="Show Image", variable=self.var_show_image)
        self.check_show_image.grid(row=0, column=4, padx=10, pady=0, sticky="w")

    def init_shapes_frame(self):
        # Create a frame for shapes
        self.shapes_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.shapes_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

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
        self.label_width = tk.Label(self.shapes_sub_frame1, text="Width: min/max")
        self.label_width.grid(row=0, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_width_percentage
        self.scale_min_width_percentage = tk.Scale(self.shapes_sub_frame1, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_width)
        self.scale_min_width_percentage.grid(row=0, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_width_percentage.set(self.model.min_width_percentage)

        # Scale for max_width_percentage
        self.scale_max_width_percentage = tk.Scale(self.shapes_sub_frame1, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_width)
        self.scale_max_width_percentage.grid(row=0, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_width_percentage.set(self.model.max_width_percentage)        
        
        def set_min_height(value):
            self.model.min_height_percentage = float(value)

        def set_max_height(value):
            self.model.max_height_percentage = float(value)

        # Label for height
        self.label_height = tk.Label(self.shapes_sub_frame1, text="Height: min/max")
        self.label_height.grid(row=1, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_height_percentage
        self.scale_min_height_percentage = tk.Scale(self.shapes_sub_frame1, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_height)
        self.scale_min_height_percentage.grid(row=1, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_height_percentage.set(self.model.min_height_percentage)

        # Scale for max_height_percentage
        self.scale_max_height_percentage = tk.Scale(self.shapes_sub_frame1, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_height)
        self.scale_max_height_percentage.grid(row=1, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_height_percentage.set(self.model.max_height_percentage)

    def init_shapes_dx_dy(self):
        def set_min_dx(value):
            self.model.min_dx_percentage = float(value)

        def set_max_dx(value):
            self.model.max_dx_percentage = float(value)

        # Label for dx
        self.label_dx = tk.Label(self.shapes_sub_frame1, text="Dx: min/max")
        self.label_dx.grid(row=2, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_dx_percentage
        self.scale_min_dx_percentage = tk.Scale(self.shapes_sub_frame1, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_dx)
        self.scale_min_dx_percentage.grid(row=2, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_dx_percentage.set(self.model.min_dx_percentage)

        # Scale for max_dx_percentage
        self.scale_max_dx_percentage = tk.Scale(self.shapes_sub_frame1, from_=-.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_dx)
        self.scale_max_dx_percentage.grid(row=2, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_dx_percentage.set(self.model.max_dx_percentage)        
        
        def set_min_dy(value):
            self.model.min_dy_percentage = float(value)

        def set_max_dy(value):
            self.model.max_dy_percentage = float(value)

        # Label for dy
        self.label_dy = tk.Label(self.shapes_sub_frame1, text="Dy: min/max")
        self.label_dy.grid(row=3, column=2, padx=10, pady=0, sticky="w")

        # Scale for min_dy_percentage
        self.scale_min_dy_percentage = tk.Scale(self.shapes_sub_frame1, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_min_dy)
        self.scale_min_dy_percentage.grid(row=3, column=3, padx=10, pady=0, sticky="ew")
        self.scale_min_dy_percentage.set(self.model.min_dy_percentage)

        # Scale for max_dy_percentage
        self.scale_max_dy_percentage = tk.Scale(self.shapes_sub_frame1, from_= -.10, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_max_dy)
        self.scale_max_dy_percentage.grid(row=3, column=4, padx=10, pady=0, sticky="ew")
        self.scale_max_dy_percentage.set(self.model.max_dy_percentage)

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

        # Label for radius
        self.label_radius = tk.Label(self.shapes_sub_frame1, text="Radius")
        self.label_radius.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        # Entry for radius
        self.entry_radius = tk.Entry(self.shapes_sub_frame1)
        self.entry_radius.grid(row=3, column=1, padx=0, pady=0, sticky="ew")
        self.entry_radius.insert(0, self.model.radius)

        # Label for prob_do_transform
        self.label_prob_do_transform = tk.Label(self.shapes_sub_frame1, text="Prob Do Transform")
        self.label_prob_do_transform.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        def set_prob_do_transform(value):
            self.model.prob_do_transform = float(value)
            
        # Scale for prob_do_transform
        self.scale_prob_do_transform = tk.Scale(self.shapes_sub_frame1, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=set_prob_do_transform)
        self.scale_prob_do_transform.grid(row=4, column=1, padx=0, pady=0, sticky="ew")
        self.scale_prob_do_transform.set(self.model.prob_do_transform)

        self.init_shapes_width_height()
        self.init_shapes_dx_dy()
       
    def init_color_frame(self):
        # Create a frame for colors
        self.color_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightgrey")
        self.color_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

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

        self.entry_transparent_threshold = tk.Entry(self.color_sub_frame2)
        self.entry_transparent_threshold.grid(row=0, column=1, padx=0, pady=0, sticky="ew")
        self.entry_transparent_threshold.insert(0, self.model.transparent_threshold)

        self.label_accent_color_percentage = tk.Label(self.color_sub_frame2, text="Accent Color Percentage")
        self.label_accent_color_percentage.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        self.entry_accent_color_percentage = tk.Entry(self.color_sub_frame2)
        self.entry_accent_color_percentage.grid(row=3, column=1, padx=0, pady=0, sticky="ew")
        self.entry_accent_color_percentage.insert(0, self.model.accent_color_percentage)

        # initialize the fill color widgets
        self.init_color_widget(self.color_sub_frame1, 0, 0, "fill", 0);
        self.initialize_gradient_widgets(self.color_sub_frame1, 0, 2, "fill");
        self.init_color_widget(self.color_sub_frame1, 0, 2, "fill", 1);

        # initialize the outline color widgets
        self.init_color_widget(self.color_sub_frame1, 1, 0, "outline", 0);
        self.initialize_gradient_widgets(self.color_sub_frame1, 1, 2, "outline");
        self.init_color_widget(self.color_sub_frame1, 1, 2, "outline", 1);

        # initialize the accent color widgets
        self.init_color_widget(self.color_sub_frame1, 2, 0, "accent", 0);
        self.initialize_gradient_widgets(self.color_sub_frame1, 2, 2, "accent");
        self.init_color_widget(self.color_sub_frame1, 2, 2, "accent", 1);

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

        
    
    
    def init_action_frame(self):
        # Create a frame for actions
        self.action_frame = tk.Frame(self.content_frame, relief="ridge", bg="lightcoral")
        self.action_frame.grid(row=14, column=0, padx=10, pady=10, sticky="ews")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        button_exit = tk.Button(self.action_frame, text="Exit", command=self.exit)
        button_exit.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        button_generate = tk.Button(self.action_frame, text="Generate", command=self.generate)
        button_generate.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    def generate(self):
        # Functionality to generate meta pixel
        do_meta_pixel(self.model)

    def exit(self):
        # Functionality to exit the application
        self.quit()

if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.mainloop()