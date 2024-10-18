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


create_pdf = True
show_pdf = True
show_image = True

max_layers = 2
shapes = 2**7

files = 1
radius = 5
prob_do_transform = 1
prob_shape_destination_equals_source = 1
shapes = 2**8

eps=20
min_samples=64

accent_color_percentage = .02

min_width_percentage = .01
min_height_percentage = .02
max_width_percentage = .1/GOLDEN_RATIO
max_height_percentage = .2

min_dx_percentage = - .1
min_dy_percentage = - .1
max_dx_percentage = .6
max_dy_percentage = .6

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

def findClusters(points, eps=eps, min_samples=min_samples):
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


  for file in range(0,files):
    print("file", file)

  # Open the image
    image = Image.open(input_path)
    image = image.convert('RGBA')

    min_width = image.width * min_width_percentage
    min_height = image.height *  min_height_percentage
    max_width = image.width * max_width_percentage/GOLDEN_RATIO
    max_height = image.height * max_height_percentage

    min_dx = - image.width * min_dx_percentage
    min_dy = - image.height * min_dy_percentage
    max_dx = image.width * max_dx_percentage
    max_dy = image.height * max_dy_percentage

    im = make_transparent(image, 32)
    opaque_pixels = findOpaquePixels(image)

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

        fill=randomColor(globals(),"fill") if random.random() > accent_color_percentage else randomColor(globals(),"accent")
        

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

    clusters = findClusters(opaque_pixels, min_samples=min_samples, eps=eps)
    image = visualizeClusters(image, clusters)
          
    filename = f"output/meta_pixel_image{file}.png"
    image.save(filename)
    if(show_image):
      image.show(filename)

    if create_pdf:
      # Add a new page to the PDF with the same size as the image
      pdf_canvas.setPageSize((image.width, image.height))

      # Add the image to the PDF
      pdf_canvas.drawImage(filename, 0, 0, preserveAspectRatio=True, width=image.width, height=image.height)

      pdf_canvas.showPage()



if create_pdf:      
# Open a PDF for writing
  pdf_path = "output/meta_pixel_output.pdf"
  pdf_canvas = canvas.Canvas(pdf_path)

# Call the metaPixel function
output_image_path = "output/meta_pixel_image.png"
metaPixel(image_path, pdf_canvas, output_image_path)

if create_pdf:
  # Save and open the PDF
  pdf_canvas.save()

  # Open the PDF (Mac-specific command)
  if show_pdf:
    os.system(f"open {pdf_path}")

