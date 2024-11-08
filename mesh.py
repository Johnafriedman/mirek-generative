# -*- coding: utf-8 -*-
"""mesh.py
"""

import random, sys, datetime

from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageTransform import MeshTransform

from transforms import create_randomized_aligned_mesh
from utilities import transformed_shape, bounding_box_size, make_transparent, random_color, GOLDEN_RATIO
import constants as const

test_mesh = False

def do_mesh(m):

  
  for file in range(0,m.files):
    image = Image.open(m.input_path)
    image = image.convert('RGBA')

    m.min_width = image.width * .05
    m.min_height = image.height * .06
    m.max_width = image.width * .5/GOLDEN_RATIO
    m.max_height = image.height * .6

    m.min_dx = - image.width * .1
    m.min_dy = - image.height * .1
    m.max_dx = image.width * .9
    m.max_dy = image.height * .9

    im = make_transparent(image, m.transparent_threshold, above=m.transparent_above)

    layers = int(random.uniform(2, m.max_layers))
    for _ in range(0, layers):
      # Apply the mesh transform
      width = int(random.uniform(2, m.max_mesh_width))
      height = int(random.uniform(2, m.max_mesh_height))
      mesh = create_randomized_aligned_mesh(width,height,im.width,im.height)
      # Create a new image with the mesh
      out = im.transform(im.size, MeshTransform(mesh))
      mask = out if m.use_mask else None
      #draw the transformed image on the original using a mask
      image.paste(out, None, mask)
      
      for shape in range(0,m.shapes):

        width = int(random.uniform(m.min_width, m.max_width))
        height = int(random.uniform(m.min_height, m.max_height))
        sx = int(random.uniform(m.min_dx, m.max_dx))
        sy = int(random.uniform(m.min_dy, m.max_dy))
        if random.random() > m.prob_shape_destination_equals_source:
          dx = int(random.uniform(m.min_dx, m.max_dx))
          dy = int(random.uniform(m.min_dy, m.max_dy))
        else:
          dx = sx
          dy = sy

        width, height = bounding_box_size(m.max_width, m.max_height, m.min_width, m.min_height)
        fill = random_color(vars(m), "fill") if random.random() > m.accent_color_percentage else random_color(vars(m), "accent")


        (out, mask) = transformed_shape(
                  image=image,
                  x=sx,
                  y=sy,
                  width=width,
                  height=height,
                  fill=fill,
                  outline=random_color(vars(m),"outline"),
                  outline_width=2
              )
        image.paste(out, (dx,dy), mask)

    '''if test_mesh:
      draw_mesh(mesh, image)
      '''
      
    filename = f"output/mesh_{m.image_name}_{m.image_date}_{file}.png"
    image.save(filename)
    image.show(filename)

if __name__ == '__main__':
  # Model
  class Model:
      def __init__(self):
        self.use_mask = True
        self.max_mesh_width = 4
        self.max_mesh_height = 6
        self.max_layers = 5
        self.files = 1
        self.shapes = 10
        self.radius = 5
        self.prob_do_transform = .9
        self.prob_shape_destination_equals_source = .5
        self.transparent_threshold = 128
        self.transparent_above = False

        self.fill_color = [(255,255,64,128),(192,128,32,32)]
        self.accent_color = [(255,16,16,212),(192,192,0,192)]
        self.outline_color = [(255,255,255,255),(128,0,0,0)]
        self.accent_color_percentage = .02

        self.source_folder = 'input/'
        if test_mesh:
          self.image_path = 'grid_image.png'
        else:
          self.image_name = 'lightwater'
          self.image_ext = '.jpg'
          self.image_path = f'{self.image_name}{self.image_ext}'
          self.image_date = datetime.datetime.now().strftime("%Y%m%d")

          self.input_path = f"input/{self.image_path}"

  m = Model()
  do_mesh(m)