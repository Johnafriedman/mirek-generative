import tkinter as tk
from tkinter import ttk

from constants import GOLDEN_RATIO
from meta_pixel_view import do_meta_pixel
import datetime

# Model
class Model:
    def __init__(self):
        self.data = "Hello, World!"
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

class StartPage(BaseWindow):
    def __init__(self, parent, controller):
        BaseWindow.__init__(self, parent, controller)
        self.title("Start Page")
        label = tk.Label(self, text="This is the start page")
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Go to Page One",
                           command=lambda: controller.show_window("PageOne"))
        button.pack()

class PageOne(BaseWindow):
    def __init__(self, parent, controller):
        BaseWindow.__init__(self, parent, controller)
        self.title("Page One")
        label = tk.Label(self, text="This is page one")
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Go to Start Page",
                           command=lambda: controller.show_window("StartPage"))
        button.pack()
        do_meta_pixel(controller.model)

# Controller
class Controller(tk.Tk):
    def __init__(self, model):
        tk.Tk.__init__(self)
        self.model = model
        self.title("Main Window")
        self.geometry("400x300")

        button_start = tk.Button(self, text="Open Start Page",
                                 command=lambda: self.show_window("StartPage"))
        button_start.pack(pady=10)

        button_page_one = tk.Button(self, text="Open Page One",
                                    command=lambda: self.show_window("PageOne"))
        button_page_one.pack(pady=10)

        self.windows = {}

    def show_window(self, window_name):
        if window_name in self.windows:
            self.windows[window_name].deiconify()
        else:
            if window_name == "StartPage":
                window = StartPage(self, self)
            elif window_name == "PageOne":
                window = PageOne(self, self)
            self.windows[window_name] = window

# Main Application
if __name__ == "__main__":
    model = Model()
    app = Controller(model)
    app.mainloop()