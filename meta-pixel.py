# -*- coding: utf-8 -*-
"""meta-pixel.py
"""


from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageChops import invert
from PIL.ImageOps import scale

from PIL.ImageTransform import MeshTransform

import math
import numpy as np
import random
import cv2

import sys

from generative.utilities import make_mask, make_transparent, draw_mesh
from generative.transforms import create_randomized_aligned_mesh


IN_COLAB = 'google.colab' in sys.modules
test_mesh = False

GOLDEN_RATIO = 1.618


use_mask = True
max_layers = 3
files = 5
radius = 5
prob_do_transform = 1
prob_shape_destination_equals_source = 1

max_fill_alpha = 8
min_fill_alpha = 2
max_fill_red = 255
min_fill_red = 192
max_fill_green = 255
min_fill_green = 128
max_fill_blue = 32
min_fill_blue = 32

max_outline_alpha = 255
min_outline_alpha = 128
max_outline_red = 255
min_outline_red = 0
max_outline_green = 255
min_outline_green = 0
max_outline_blue = 255
min_outline_blue = 0

source_folder = '/content/' if IN_COLAB else 'input/'

if test_mesh:
  image_path = 'grid_image.png'
else:
  image_path = 'Rhythms_Circle_DataReferenceSet_1982_2.png'
##  image_path = 'abstract_artwork_with_neon1.png'
  # image_path = 'rhythms_entropic_heavens_waves_continue_v10.png'
##  image_path = 'myanmar_tm5_2004349_lrg.jpg'
#image_path =  'fence.jpg'

import math

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

def transformed_shape(image, x, y, width, height, radius, fill, outline, outline_width):

  shapes=["ellipse","rectangle"]
  shape = shapes[int(random.uniform(0,len(shapes)))]

  transforms = ["blur", "scale"]
  transform = transforms[int(random.uniform(0,len(transforms)))]
  # Create a image mask for the cropped image


  mask = Image.new('L', (width, height), 0)

# Create a draw object for the mask
  draw = ImageDraw.Draw(mask)

  # Define the bounding box for the ellipse
  bounding_box = (0, 0, width, height)  # Adjust as needed

  # do_transform = random.random() < prob_do_transform
  do_transform=True

  # Draw the shape on the mask (white color fills the ellipse)
  getattr(draw, shape)(bounding_box, fill=255)

  # Apply the mask to the image  
  cropped = image.crop((x,y,x+width,y+height))

  if not do_transform:
    transformed_image = cropped
  else:
    if transform == 'blur':
      transformed_image = cropped.filter(ImageFilter.GaussianBlur(radius))
    elif transform == 'invert':
      red, green, blue, alpha = cropped.split()
      transformed_image = Image.merge('RGBA', (invert(red), invert(green), invert(blue), alpha))
    elif transform == "scale":
      scale_factor =  int(random.uniform(2, 8))
      scaled = scale(cropped, scale_factor, Image.NEAREST)
      transformed_image = scaled.crop((0,0,width,height))



  overlay = Image.new('RGBA', cropped.size, (0,0,0,0))
  draw = ImageDraw.Draw(overlay)    
  getattr(draw, shape)(bounding_box, fill, outline, outline_width)

  transformed_image = Image.alpha_composite(transformed_image, overlay)

# return the blurred image
  return(transformed_image, mask)


# Open the image
input_path = f"input/{image_path}"

import numpy as np
from PIL import Image

def make_transparent(image, luminance_threshold):
    image = image.convert('RGBA')

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Calculate luminance
    luminance = 0.299 * image_array[:, :, 0] + 0.587 * image_array[:, :, 1] + 0.114 * image_array[:, :, 2]

    # Normalize luminance to range [0, 255]
    normalized_luminance = (luminance / 255.0) * 255

    # Invert luminance to make darker colors more opaque
    alpha_channel = 255 - normalized_luminance

    # Set the alpha channel based on the inverted luminance
    image_array[:, :, 3] = alpha_channel

    # Create a new image from the modified array
    transparent_image = Image.fromarray(image_array.astype('uint8'))

    return transparent_image

for file in range(0,files):
  image = Image.open(input_path)
  image = image.convert('RGBA')

  edge_increment = int(image.width * .1)

  min_width = image.width * .01
  min_height = image.height * .02
  max_width = image.width * .1/GOLDEN_RATIO
  max_height = image.height * .2

  min_dx = - image.width * .1
  min_dy = - image.height * .1
  max_dx = image.width * .6
  max_dy = image.height * .6

  im = make_transparent(image, 64)

  layers = int(random.uniform(2, max_layers))
  for _ in range(0, layers):

    # Create a new image with the mesh
    out = im.copy()
    mask = out if use_mask else None
    # Draw the transformed image on the original using a mask
    image.paste(out, None, mask)
    
    if mask is not None:
        # Convert the mask to a NumPy array
        mask_array = np.array(mask)

        # Convert the mask to grayscale
        gray_mask = cv2.cvtColor(mask_array, cv2.COLOR_RGBA2GRAY)

        # Apply Canny edge detection
        edges = cv2.Canny(gray_mask, 100, 200)

        # Iterate through the edges to find non-transparent pixels
        non_transparent_pixels = np.argwhere(edges != 0)

        for i in range(0, len(non_transparent_pixels), edge_increment):
            sy, sx = non_transparent_pixels[i]
            print(sx, sy)
            width = int(random.uniform(min_width, max_width))
            height = int(random.uniform(min_height, max_height))

            if random.random() > prob_shape_destination_equals_source:
                dx = int(random.uniform(min_dx, max_dx))
                dy = int(random.uniform(min_dy, max_dy))
            else:
                dx = sx
                dy = sy

            fill_alpha = int(random.uniform(min_fill_alpha, max_fill_alpha))  

            outline_alpha = int(random.uniform(min_outline_alpha, max_outline_alpha))     
    
            fill_red = int(random.uniform(min_fill_red, max_fill_red))

            outline_red = int(random.uniform(min_outline_red, max_outline_red))   

            fill_green = int(random.uniform(min_fill_green, max_fill_green))  

            outline_green = int(random.uniform(min_outline_green, max_outline_green))   
    
            fill_blue = int(random.uniform(min_fill_blue, max_fill_blue))

            outline_blue = int(random.uniform(min_outline_blue, max_outline_blue)) 

            width, height = bounding_box_size(max_width, max_height, min_width, min_height)

            (out, mask) = transformed_shape(image, sx, sy, width, height, 5, (fill_red, fill_green, fill_blue, fill_alpha), (outline_red, outline_green, outline_blue, outline_alpha), 2)
            image.paste(out, (dx,dy), mask)

    
  filename = f"output/meta_pixel_image{file}.png"
  image.save(filename)
  image.show(filename)
