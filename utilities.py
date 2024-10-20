import numpy as np
import random

from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageChops import invert
from PIL.ImageOps import scale

from constants import GOLDEN_RATIO


def transformed_shape(image, x, y, width, height, fill, outline, outline_width, radius = 5, transforms = ["blur", "invert", "scale"], shapes=["ellipse","rectangle"],do_transform=True):

  
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

  if not do_transform:
    transformed_image = cropped
  else:
    if transform == 'blur':
      transformed_image = cropped.filter(ImageFilter.GaussianBlur(radius))
    elif transform == 'invert':
      red, green, blue, alpha = cropped.split()
      transformed_image = Image.merge('RGBA', (invert(red), invert(green), invert(blue), alpha))
    elif transform == "scale":
      scale_factor =  int(random.uniform(2, 4))
      scaled = scale(cropped, scale_factor, Image.NEAREST)
      transformed_image = scaled.crop((0,0,width,height))



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

def randomColor(name_space, name):
  minr = name_space[f"MIN_{name}_RED"]
  maxr = name_space[f"MAX_{name}_RED"]
  ming = name_space[f"MIN_{name}_GREEN"]
  maxg = name_space[f"MAX_{name}_GREEN"]
  minb = name_space[f"MIN_{name}_BLUE"]
  maxb = name_space[f"MAX_{name}_BLUE"]
  mina = name_space[f"MIN_{name}_ALPHA"]
  maxa = name_space[f"MAX_{name}_ALPHA"]

  return (
    int(random.uniform(minr, maxr)),
    int(random.uniform(ming, maxg)), 
    int(random.uniform(minb, maxb)), 
    int(random.uniform(mina, maxa))
  )

