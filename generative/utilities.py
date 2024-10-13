from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random




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

def make_transparent(image, luminance_threshold):

  image = image.convert('RGBA')

  # Convert the image to a NumPy array
  image_array = np.array(image)

  # Calculate luminance
  luminance = 0.299 * image_array[:, :, 0] + 0.587 * image_array[:, :, 1] + 0.114 * image_array[:, :, 2]

  # Create a mask based on luminance threshold
  mask = luminance > luminance_threshold

  # Set transparent pixels (alpha channel to 0) where mask is True
  image_array[mask, 3] = 0

  # Create a new image from the modified array
  transparent_image = Image.fromarray(image_array)

  return transparent_image