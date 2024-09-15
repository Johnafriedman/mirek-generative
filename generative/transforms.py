import random

test_coords = False


def create_randomized_aligned_mesh(rows, cols, image_width, image_height):
  """Creates a randomized mesh where all edges align.

  Args:
    rows: Number of rows in the mesh.
    cols: Number of columns in the mesh.
    image_width: Width of the image the mesh will be applied to.
    image_height: Height of the image the mesh will be applied to.

  Returns:
    A list of quadrilaterals representing the mesh.
  """

  # Generate random x and y coordinates for the grid lines
  if not test_coords:
    top_x_coords = [0] + sorted([int(random.uniform(0, image_width)) for _ in range(cols - 1)]) + [image_width]
    bottom_x_coords = [0] + sorted([int(random.uniform(0, image_width)) for _ in range(cols - 1)]) + [image_width]
    left_y_coords = [0] + sorted([int(random.uniform(0, image_height)) for _ in range(rows - 1)]) + [image_height]
    right_y_coords = [0] + sorted([int(random.uniform(0, image_height)) for _ in range(rows - 1)]) + [image_height]
  else: 
    top_x_coords =    [0] + [image_width /3, 2* image_width/3 ] + [image_width]
    bottom_x_coords = [0] + [image_width /3, 2* image_width/3 ] + [image_width]
    left_y_coords =   [0] + [image_height/3, 2* image_height/3] + [image_height]
    right_y_coords =  [0] + [image_height/3, 2* image_height/3] + [image_height]

  mesh = []
  sx = image_width/cols
  sy = image_height/rows
  for row in range(rows):
    for col in range(cols):

      TL_X = 0
      TL_Y = 1
      BL_X = 2
      BL_Y = 3
      BR_X = 4
      BR_Y = 5
      TR_X = 6
      TR_Y = 7
      
      prev_col = row * cols + col -1
      prev_row = (row-1) * cols + col
      top_left_x = mesh[prev_col][1][TR_X] if col else top_x_coords[col]
      bottom_left_x = mesh[prev_col][1][BR_X] if col else bottom_x_coords[col]
      bottom_right_x = bottom_x_coords[col+1]
      top_right_x = top_x_coords[col+1]

      top_left_y = mesh[prev_row][1][BL_Y] if row else left_y_coords[row]
      top_right_y = mesh[prev_row][1][BR_Y] if row else right_y_coords[row]
      bottom_left_y = left_y_coords[row + 1]
      bottom_right_y = right_y_coords[row + 1]

      x1 = col*sx
      y1 = row*sy
      x2 = (col+1)*sx
      y2 = (row+1)*sy

      #Source rectangle (unchanged)
      bbox = (int(x1), int(y1), int(x2), int(y2))
      
      # Create a quadrilateral representing the grid line
      quad = (
        top_left_x, top_left_y,
        bottom_left_x, bottom_left_y, 
        bottom_right_x, bottom_right_y,
        top_right_x, top_right_y
        )

      iquad = tuple(map(int, quad))

      mesh.append((bbox,iquad))

  return mesh

