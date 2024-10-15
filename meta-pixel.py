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

from generative.utilities import make_transparent, transformed_shape, bounding_box_size, randomColor, GOLDEN_RATIO
from generative.transforms import create_randomized_aligned_mesh


IN_COLAB = 'google.colab' in sys.modules
test_mesh = False


use_mask = True
max_layers = 1
files = 1
radius = 5
prob_do_transform = 1
prob_shape_destination_equals_source = 1
shapes = 2**8

max_fill_alpha = 128
min_fill_alpha = 32
max_fill_red = 255
min_fill_red = 192
max_fill_green = 255
min_fill_green = 128
max_fill_blue = 64
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


# Open the image
input_path = f"input/{image_path}"

import numpy as np
from PIL import Image

for file in range(0,files):
  print("file", file)
  image = Image.open(input_path)
  image = image.convert('RGBA')

  min_width = image.width * .01
  min_height = image.height * .02
  max_width = image.width * .1/GOLDEN_RATIO
  max_height = image.height * .2

  min_dx = - image.width * .1
  min_dy = - image.height * .1
  max_dx = image.width * .6
  max_dy = image.height * .6

  im = make_transparent(image, 64)

  for _ in range(0, max_layers):
    print("layer", _)
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

        edge_increment = int(len(non_transparent_pixels) / shapes)
        for i in range(0, len(non_transparent_pixels), edge_increment):
            width, height = bounding_box_size(max_width, max_height, min_width, min_height)

            sy, sx = non_transparent_pixels[i] - (height // 2, width // 2)

            if sy < 0 or sx < 0:
              continue

            if random.random() > prob_shape_destination_equals_source:
                dx = int(random.uniform(min_dx, max_dx))
                dy = int(random.uniform(min_dy, max_dy))
            else:
                dx = sx
                dy = sy


            (out, mask) = transformed_shape(
                image=image,
                x=sx,
                y=sy,
                width=width,
                height=height,
                fill=randomColor(globals(),"fill"),
                outline=randomColor(globals(),"outline"),
                outline_width=2,
                radius = 5,
                transforms=["blur", "scale"]
            )

            
            image.paste(out, (dx,dy), mask)

    
  filename = f"output/meta_pixel_image{file}.png"
  image.save(filename)
  image.show(filename)

