import numpy as np
import random

from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageChops import invert
from PIL.ImageOps import scale

import tkinter as tk
from PIL import Image, ImageTk
from screeninfo import get_monitors

from constants import GOLDEN_RATIO

def transformed_centroid(image, x, y, width, height, fill, outline, outline_width, transforms = [],do_transform=True):

  
  shape = "ellipse"

  transform = transforms[int(random.uniform(0,len(transforms)))]
  # Create a image mask for the cropped image


  mask = Image.new('L', (width, height), 0)

# Create a draw object for the mask
  draw = ImageDraw.Draw(mask)

  # Define the bounding box for the ellipse
  bounding_box = (0, 0, width, height)  # Adjust as needed

  # do_transform = random.random() < prob_do_transform

  # Draw the shape on the mask (white color fills the ellipse)
  # adjust the fill it is 8 if the width is greater than 90% of the image width and 255 if width is less than 10% of the image width
  if width > .9*image.width:
    mask_fill = 32
  elif width < .1*image.width:
    mask_fill = 255
  # otherwise it varies smoothly between 8 and 255
  else:
    min = 32
    mask_fill = int(min + (255-min)*(width/image.width))


  getattr(draw, shape)(bounding_box, mask_fill)

  # Apply the mask to the image  
  cropped = image.crop((x-width/2,y-height/2,x+width/2,y+height/2))


  if transform['name'] == 'blur':
    transformed_image = cropped.filter(ImageFilter.GaussianBlur(transform['radius']))
  elif transform['name'] == 'invert':
    red, green, blue, alpha = cropped.split()
    transformed_image = Image.merge('RGBA', (invert(red), invert(green), invert(blue), alpha))
  elif transform['name'] == "scale":
    scale_factor =  int(random.uniform(2, transform['scale_factor']))
    scaled = scale(cropped, scale_factor, Image.NEAREST)
    transformed_image = scaled.crop((0,0,width,height))
  else:
    transformed_image = cropped


  overlay = Image.new('RGBA', cropped.size, (0,0,0,0))
  draw = ImageDraw.Draw(overlay)    
  getattr(draw, shape)(bounding_box, fill, outline, outline_width)

  transformed_image = Image.alpha_composite(transformed_image, overlay)

# return the blurred image
  return(transformed_image, mask)


def transformed_shape(image, x, y, width, height, fill, outline, outline_width, transforms = [], shapes=["ellipse","rectangle"],do_transform=True):

  
  shape = shapes[int(random.uniform(0,len(shapes)))]

  transform = transforms[int(random.uniform(0,len(transforms)))]
  # Create a image mask for the cropped image


  mask = Image.new('L', (width, height), 0)

# Create a draw object for the mask
  draw = ImageDraw.Draw(mask)

  # Define the bounding box for the ellipse
  bounding_box = (0, 0, width, height)  # Adjust as needed

  # do_transform = random.random() < prob_do_transform

  # Draw the shape on the mask (white color fills the ellipse)
  getattr(draw, shape)(bounding_box, fill=255)

  # Apply the mask to the image  
  cropped = image.crop((x,y,x+width,y+height))


  if transform['name'] == 'blur':
    transformed_image = cropped.filter(ImageFilter.GaussianBlur(transform['radius']))
  elif transform['name'] == 'invert':
    red, green, blue, alpha = cropped.split()
    transformed_image = Image.merge('RGBA', (invert(red), invert(green), invert(blue), alpha))
  elif transform['name'] == "scale":
    scale_factor =  int(random.uniform(2, transform['scale_factor']))
    scaled = scale(cropped, scale_factor, Image.NEAREST)
    transformed_image = scaled.crop((0,0,width,height))
  else:
    transformed_image = cropped


  overlay = Image.new('RGBA', cropped.size, (0,0,0,0))
  draw = ImageDraw.Draw(overlay)    
  getattr(draw, shape)(bounding_box, fill, outline, outline_width)

  transformed_image = Image.alpha_composite(transformed_image, overlay)

# return the blurred image
  return(transformed_image, mask)

def bounding_box_size(max_width, max_height, min_width, min_height):
  """Calculates bounding box size based on inverse square correlation with probability.

  Args:
    probability: Probability value between 0 and 1.
    max_width: Maximum width of the bounding box.
    max_height: Maximum height of the bounding box.
    min_width: Minimum width of the bounding box.
    min_height: Minimum height of the bounding box.


  Returns:
    Bounding box size as a tuple (width, height).
  """

  r=random.random()
  w_ratio = r**2
  width = min_width + w_ratio * (max_width - min_width)
  height = width*GOLDEN_RATIO
  r=random.random()
  if r > .6:
    w=width
    width=height
    height=w
  elif r < .05:
    height=width


  return int(width), int(height)

def make_mask(width=200, height=200, border=5, rectangle=False):

  # Create a new image with a black background
  image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

  # Create a drawing object
  draw = ImageDraw.Draw(image)

  # Draw a circle with a gradient edge
  shape = draw.rectangle if rectangle else draw.ellipse
  for i in range(border):
    alpha = int(255 * (i / border))  # Calculate alpha value for gradient
    shape(
        (
            i,
            i,
            width - i,
            height - i,
        ),
        fill=(255, 255, 255, alpha),
    )

  # return the image
  return(image)

def draw_mesh(mesh, image):
  """Draws the mesh on the given image.

  Args:
    mesh: A list of tuples, where each tuple is ((bbox_x1, bbox_y1, bbox_x2, bbox_y2), (quad_x1, quad_y1, quad_x2, quad_y2, quad_x3, quad_y3, quad_x4, quad_y4)).
    image: A PIL Image object.
  """
  draw = ImageDraw.Draw(image)

  for bbox, quad in mesh:
    # Draw bounding box in blue
    draw.rectangle(bbox, outline="blue", width=3)

    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    color = (red,green,blue)

    # Draw quad in red
    draw.line((quad[0],quad[1], quad[2],quad[3], quad[4],quad[5], quad[6],quad[7],quad[0],quad[1]), fill=color, width=8)

  return image

def make_transparent(image, luminance_threshold, above=True):
  image = image.convert('RGBA')

  # Convert the image to a NumPy array
  image_array = np.array(image)

  # Calculate luminance
  luminance = 0.299 * image_array[:, :, 0] + 0.587 * image_array[:, :, 1] + 0.114 * image_array[:, :, 2]

  # Create a mask where luminance is above the threshold
  if above:
    mask = luminance > luminance_threshold
  else:
    mask = luminance < luminance_threshold

  # Set the alpha channel to 0 (transparent) where the mask is True
  image_array[mask, 3] = 0

  # Create a new image from the modified array
  transparent_image = Image.fromarray(image_array.astype('uint8'))

  return transparent_image

def random_color(name_space, name):
  c = name_space[f"{name}_color"]
  # gven two colors return a random color from a gradient between them
  color1, color2 = c
  random_factor = random.random()
  random_color = tuple(
      int(color1[i] + (color2[i] - color1[i]) * random_factor) for i in range(4)
  )
  return random_color
  

class ImageWindow:
    def __init__(self, parent, image, model):
        self.parent = parent
        self.image_copy = image.copy()
        self.model = model
        self.scale_update_id = None

    def open(self):
        self.new_window = tk.Toplevel(self.parent)
        self.new_window.title(f"Image Window - {self.parent.model.image_name}")

        # Bind the close event to the on_close method
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create a frame for the canvas and scrollbars
        frame = tk.Frame(self.new_window)
        frame.grid(row=0, column=0, sticky="nsew")

        # Create a canvas widget
        self.canvas = tk.Canvas(frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars to the canvas
        h_scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Create a copy of the image to scale
        self.tk_image = ImageTk.PhotoImage(self.image_copy)
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Configure the scroll region
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Add a scale widget to adjust the size of the image
        self.scale = tk.Scale(self.new_window, from_=10, to=200, orient=tk.HORIZONTAL, label="Scale", command=self.on_scale)
        self.scale.set(100)
        self.scale.grid(row=1, column=0, sticky="ew")

        # Bind mouse wheel events for zooming
        self.new_window.bind("<MouseWheel>", self.zoom)  # For Windows and macOS
        self.new_window.bind("<Button-4>", self.zoom)  # For Linux
        self.new_window.bind("<Button-5>", self.zoom)  # For Linux

        # Configure grid weights for the new window and frame
        self.new_window.grid_rowconfigure(0, weight=1)
        self.new_window.grid_rowconfigure(1, weight=0)
        self.new_window.grid_columnconfigure(0, weight=1)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Position the window on the largest monitor if this is the first ImageWindow
        if len(self.parent.windows) == 1:
            self.position_on_largest_monitor()
        else:
            self.position_on_previous_monitor()

    def position_on_largest_monitor(self):
        monitors = get_monitors()
        largest_monitor = max(monitors, key=lambda m: m.width * m.height)
        self.new_window.geometry(f"{largest_monitor.width}x{largest_monitor.height}+{largest_monitor.x}+{largest_monitor.y}")
        self.new_window.update_idletasks()  # Ensure the window manager is aware of the new geometry

    #position window on the same monitor as the previous window
    def position_on_previous_monitor(self):
        previous_window = self.parent.windows[-2].new_window
        x = previous_window.winfo_x()
        y = previous_window.winfo_y()
        width = previous_window.winfo_width()
        height = previous_window.winfo_height()
        offset = 20
        self.new_window.geometry(f"{width}x{height}+{x+offset}+{y+offset}")
        self.new_window.update_idletasks()

    def on_scale(self, scale_value):
        if self.scale_update_id is not None:
            self.parent.after_cancel(self.scale_update_id)
        self.scale_update_id = self.parent.after(500, lambda: self.scale_image(scale_value))

    def scale_image(self, scale_value):
        scale_value = int(scale_value)
        new_size = (self.image_copy.width * scale_value // 100, self.image_copy.height * scale_value // 100)
        resized_image = self.image_copy.resize(new_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def zoom(self, event):
        if event.delta > 0 or event.num == 4:
            self.scale.set(self.scale.get() + 10)
        elif event.delta < 0 or event.num == 5:
            self.scale.set(self.scale.get() - 10)
        self.on_scale(self.scale.get())

    def on_close(self):
        # Remove the instance from the model's windows array
        self.parent.windows.remove(self)
        # Destroy the window
        self.new_window.destroy()
