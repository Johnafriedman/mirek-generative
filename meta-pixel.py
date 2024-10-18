# -*- coding: utf-8 -*-
"""meta-pixel.py
"""
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib.units import inch
from sklearn.cluster import DBSCAN


from PIL import Image, ImageDraw
from PIL.ImageChops import invert
from PIL.ImageOps import scale
import numpy as np
from PIL import Image
import random, os
import cv2

from generative.utilities import make_transparent, transformed_shape, bounding_box_size, randomColor, GOLDEN_RATIO


CREATE_PDF = True
SHOW_PDF = True
SHOW_IMAGE = True

MAX_LAYERS = 2
SHAPES = 2**7

FILES = 1
RADIUS = 5
PROB_DO_TRANSFORM = 1
PROB_SHAPE_DESTINATION_EQUALS_SOURCE = 1
SHAPES = 2**8

EPS = 20
MIN_SAMPLES = 64

ACCENT_COLOR_PERCENTAGE = .02

MIN_WIDTH_PERCENTAGE = .01
MIN_HEIGHT_PERCENTAGE = .02
MAX_WIDTH_PERCENTAGE = .1/GOLDEN_RATIO
MAX_HEIGHT_PERCENTAGE = .2

MIN_DX_PERCENTAGE = - .1
MIN_DY_PERCENTAGE = - .1
MAX_DX_PERCENTAGE = .6
MAX_DY_PERCENTAGE = .6

MAX_FILL_ALPHA = 128
MIN_FILL_ALPHA = 32
MAX_FILL_RED = 255
MIN_FILL_RED = 192
MAX_FILL_GREEN = 255
MIN_FILL_GREEN = 128
MAX_FILL_BLUE = 64
MIN_FILL_BLUE = 32

MAX_ACCENT_ALPHA = 212
MIN_ACCENT_ALPHA = 192
MAX_ACCENT_RED = 255
MIN_ACCENT_RED = 192
MAX_ACCENT_GREEN = 16
MIN_ACCENT_GREEN = 0
MAX_ACCENT_BLUE = 16
MIN_ACCENT_BLUE = 0

MAX_OUTLINE_ALPHA = 255
MIN_OUTLINE_ALPHA = 128
MAX_OUTLINE_RED = 255
MIN_OUTLINE_RED = 0
MAX_OUTLINE_GREEN = 255
MIN_OUTLINE_GREEN = 0
MAX_OUTLINE_BLUE = 255
MIN_OUTLINE_BLUE = 0

source_folder = 'input/'
image_path = 'input/Rhythms_Circle_DataReferenceSet_1982_2.png'

def visualizeClusters(image, clusters):
    """
    Visualize clusters of points on the image.

    Parameters:
    - image: The input image.
    - clusters: A list of clusters, where each cluster is a list of points.
    """
    output_image = image.copy()
    draw = ImageDraw.Draw(output_image)

    if not clusters:
      return output_image
    
    # Calculate the maximum cluster size for normalization
    max_cluster_size = max(len(cluster) for cluster in clusters)

    for cluster in clusters:
        # Calculate luminance based on the size of the cluster
        cluster_size = len(cluster)
        luminance = int(255 * (1 - (cluster_size / max_cluster_size)))  # Darker for larger clusters
        color = (luminance, 0, luminance)

        # Calculate the centroid of the cluster
        centroid = np.mean(cluster, axis=0).astype(int)

        # Calculate the radius of the circle to encompass the cluster
        distances = np.linalg.norm(cluster - centroid, axis=1)
        radius = int(np.max(distances))

        # Draw the circle around the cluster
        draw.ellipse((centroid[1] - radius, centroid[0] - radius, centroid[1] + radius, centroid[0] + radius), outline=color, width=2)

    return output_image

def findClusters(points, eps=EPS, min_samples=MIN_SAMPLES):
    """
    Find clusters of points in an image.

    Parameters:
    - image: The input image.
    - points: A numpy array of points (x, y).
    - eps: The maximum distance between two samples for one to be considered as in the neighborhood of the other.
    - min_samples: The number of samples in a neighborhood for a point to be considered as a core point.

    Returns:
    - A list of clusters, where each cluster is a list of points.
    """
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(points)
    labels = clustering.labels_

    clusters = []
    for label in set(labels):
        if label != -1:  # -1 is the label for noise points
            cluster_points = points[labels == label]
            clusters.append(cluster_points.tolist())

    return clusters

# Example usage
# image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
# opaque_pixels = findOpaquePixels(image)
# clusters = findClusters(image, opaque_pixels)
# print(clusters)

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


  for file in range(0, FILES):
    print("file", file)

  # Open the image
    image = Image.open(input_path)
    image = image.convert('RGBA')

    min_width = image.width * MIN_WIDTH_PERCENTAGE
    min_height = image.height * MIN_HEIGHT_PERCENTAGE
    max_width = image.width * MAX_WIDTH_PERCENTAGE/GOLDEN_RATIO
    max_height = image.height * MAX_HEIGHT_PERCENTAGE

    min_dx = - image.width * MIN_DX_PERCENTAGE
    min_dy = - image.height * MIN_DY_PERCENTAGE
    max_dx = image.width * MAX_DX_PERCENTAGE
    max_dy = image.height * MAX_DY_PERCENTAGE

    im = make_transparent(image, 32)
    opaque_pixels = findOpaquePixels(image)

    edge_pixel_cnt = int(len(opaque_pixels))
    edge_increment = int((edge_pixel_cnt) / SHAPES)
    start = int(edge_pixel_cnt % edge_increment)
    for _ in range(0, MAX_LAYERS):
      print("layer", _)
      # Create a new image with the mesh
      
      for i in range(start, edge_pixel_cnt, edge_increment):
        width, height = bounding_box_size(max_width, max_height, min_width, min_height)

        sy, sx = opaque_pixels[i] - (height // 2, width // 2)

        if sy < 0 or sx < 0:
          continue

        if random.random() > PROB_SHAPE_DESTINATION_EQUALS_SOURCE:
            dx = int(random.uniform(min_dx, max_dx))
            dy = int(random.uniform(min_dy, max_dy))
        else:
            dx = sx
            dy = sy

        fill=randomColor(globals(),"FILL") if random.random() > ACCENT_COLOR_PERCENTAGE else randomColor(globals(),"ACCENT")
        

        (out, mask) = transformed_shape(
            image=image,
            x=sx,
            y=sy,
            width=width,
            height=height,
            fill=fill,
            outline=randomColor(globals(),"OUTLINE"),
            outline_width=2,
            radius = 5,
            transforms=["blur", "scale"]
        )

        image.paste(out, (dx,dy), mask)

    clusters = findClusters(opaque_pixels, min_samples=MIN_SAMPLES, eps=EPS)
    image = visualizeClusters(image, clusters)
          
    filename = f"output/meta_pixel_image{file}.png"
    image.save(filename)
    if(SHOW_IMAGE):
      image.show(filename)

    if CREATE_PDF:
      # Add a new page to the PDF with the same size as the image
      pdf_canvas.setPageSize((image.width, image.height))

      # Add the image to the PDF
      pdf_canvas.drawImage(filename, 0, 0, preserveAspectRatio=True, width=image.width, height=image.height)

      pdf_canvas.showPage()



if CREATE_PDF:      
# Open a PDF for writing
  pdf_path = "output/meta_pixel_output.pdf"
  pdf_canvas = canvas.Canvas(pdf_path)

# Call the metaPixel function
output_image_path = "output/meta_pixel_image.png"
metaPixel(image_path, pdf_canvas, output_image_path)

if CREATE_PDF:
  # Save and open the PDF
  pdf_canvas.save()

  # Open the PDF (Mac-specific command)
  if SHOW_PDF:
    os.system(f"open {pdf_path}")

