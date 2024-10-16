# -*- coding: utf-8 -*-
"""meta-pixel.py
"""
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib.units import inch


from PIL import Image
from PIL.ImageChops import invert
from PIL.ImageOps import scale
import numpy as np
from PIL import Image
import random
import cv2


from generative.utilities import make_transparent, transformed_shape, bounding_box_size, randomColor, GOLDEN_RATIO

max_layers = 2
shapes = 2**7

files = 5
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

max_accent_alpha = 212
min_accent_alpha = 192
max_accent_red = 255
min_accent_red = 192
max_accent_green = 16
min_accent_green = 0
max_accent_blue = 16
min_accent_blue = 0

max_outline_alpha = 255
min_outline_alpha = 128
max_outline_red = 255
min_outline_red = 0
max_outline_green = 255
min_outline_green = 0
max_outline_blue = 255
min_outline_blue = 0

source_folder = 'input/'
image_path = 'input/Rhythms_Circle_DataReferenceSet_1982_2.png'

def findOpaquePixels(image):

    mask_array = np.array(image)

    # Convert the mask to grayscale
    gray_mask = cv2.cvtColor(mask_array, cv2.COLOR_RGBA2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray_mask, 100, 200)

    # Iterate through the edges to find non-transparent pixels
    opaque_pixels = np.argwhere(edges != 0)
    return opaque_pixels


def metaPixel(input_path, pdf_canvas, output_image_path):


  for file in range(0,files):
    print("file", file)

  # Open the image
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

    im = make_transparent(image, 32)
    opaque_pixels = findOpaquePixels(im)

    edge_pixel_cnt = int(len(opaque_pixels))
    edge_increment = int((edge_pixel_cnt) / shapes)
    start = int(edge_pixel_cnt % edge_increment)
    for _ in range(0, max_layers):
      print("layer", _)
      # Create a new image with the mesh
      
      for i in range(start, edge_pixel_cnt, edge_increment):
        width, height = bounding_box_size(max_width, max_height, min_width, min_height)

        sy, sx = opaque_pixels[i] - (height // 2, width // 2)

        if sy < 0 or sx < 0:
          continue

        if random.random() > prob_shape_destination_equals_source:
            dx = int(random.uniform(min_dx, max_dx))
            dy = int(random.uniform(min_dy, max_dy))
        else:
            dx = sx
            dy = sy

        fill=randomColor(globals(),"fill") if random.random() > .02 else randomColor(globals(),"accent")
        

        (out, mask) = transformed_shape(
            image=image,
            x=sx,
            y=sy,
            width=width,
            height=height,
            fill=fill,
            outline=randomColor(globals(),"outline"),
            outline_width=2,
            radius = 5,
            transforms=["blur", "scale"]
        )

        image.paste(out, (dx,dy), mask)
          
    filename = f"output/meta_pixel_image{file}.png"
    image.save(filename)
    # image.show(filename)


    # Add a new page to the PDF with the same size as the image
    pdf_canvas.setPageSize((image.width, image.height))

    # Add the image to the PDF
    pdf_canvas.drawImage(filename, 0, 0, preserveAspectRatio=True, width=image.width, height=image.height)

    pdf_canvas.showPage()



      
# Open a PDF for writing
pdf_path = "output/meta_pixel_output.pdf"
pdf_canvas = canvas.Canvas(pdf_path)

# Call the metaPixel function
output_image_path = "output/meta_pixel_image.png"
metaPixel(image_path, pdf_canvas, output_image_path)

# Save and open the PDF
pdf_canvas.save()

# Open the PDF (Mac-specific command)
import os
os.system(f"open {pdf_path}")

