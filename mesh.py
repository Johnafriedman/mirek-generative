# -*- coding: utf-8 -*-
"""mesh.py
"""

import random, sys, datetime

from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageTransform import MeshTransform

from transforms import create_randomized_aligned_mesh
from utilities import transformed_shape, bounding_box_size, make_transparent, randomColor, GOLDEN_RATIO
import constants as const

IN_COLAB = 'google.colab' in sys.modules
test_mesh = False



use_mask = True
max_mesh_width = 4
max_mesh_height = 6
max_layers = 5
files = 1
shapes = 10
radius = 5
prob_do_transform = .9
prob_shape_destination_equals_source = .5
transparent_threshold = 128
transparent_above = True

max_fill_alpha = 255
min_fill_alpha = 0
max_fill_red = 255
min_fill_red = 0
max_fill_green = 255
min_fill_green = 0
max_fill_blue = 255
min_fill_blue = 0

max_outline_alpha = 255
min_outline_alpha = 0
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
  image_name = 'Rhythms_Circle_DataReferenceSet_1982_2'
  image_ext = '.png'
  image_path = f'{image_name}{image_ext}'
  image_date = datetime.datetime.now().strftime("%Y%m%d")



# Open the image
input_path = f"input/{image_path}"

for file in range(0,files):
  image = Image.open(input_path)
  image = image.convert('RGBA')

  min_width = image.width * .05
  min_height = image.height * .06
  max_width = image.width * .5/GOLDEN_RATIO
  max_height = image.height * .6

  min_dx = - image.width * .1
  min_dy = - image.height * .1
  max_dx = image.width * .9
  max_dy = image.height * .9

  im = make_transparent(image, transparent_threshold, above=transparent_above)

  layers = int(random.uniform(2, max_layers))
  for _ in range(0, layers):
    # Apply the mesh transform
    width = int(random.uniform(2, max_mesh_width))
    height = int(random.uniform(2, max_mesh_height))
    mesh = create_randomized_aligned_mesh(width,height,im.width,im.height)
    # Create a new image with the mesh
    out = im.transform(im.size, MeshTransform(mesh))
    mask = out if use_mask else None
    #draw the transformed image on the original using a mask
    image.paste(out, None, mask)
    
    for shape in range(0,shapes):

      width = int(random.uniform(min_width, max_width))
      height = int(random.uniform(min_height, max_height))
      sx = int(random.uniform(min_dx, max_dx))
      sy = int(random.uniform(min_dy, max_dy))
      if random.random() > prob_shape_destination_equals_source:
        dx = int(random.uniform(min_dx, max_dx))
        dy = int(random.uniform(min_dy, max_dy))
      else:
        dx = sx
        dy = sy

      width, height = bounding_box_size(max_width, max_height, min_width, min_height)

      (out, mask) = transformed_shape(
                image=image,
                x=sx,
                y=sy,
                width=width,
                height=height,
                fill=randomColor(vars(const),"FILL"),
                outline=randomColor(vars(const),"OUTLINE"),
                outline_width=2
            )
      image.paste(out, (dx,dy), mask)

  '''if test_mesh:
    draw_mesh(mesh, image)
    '''
    
  filename = f"output/mesh_{image_name}_{image_date}_{file}.png"
  image.save(filename)
  image.show(filename)

