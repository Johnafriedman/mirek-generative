# -*- coding: utf-8 -*-
"""meta-pixel.py
"""
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib.units import inch
from sklearn.cluster import DBSCAN


from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageChops import invert
from PIL.ImageOps import scale
from PIL.ImageTransform import MeshTransform

import numpy as np
from PIL import Image
import random, os
import cv2

from transforms import create_randomized_aligned_mesh

from constants import *
from utilities import make_transparent, transformed_shape, bounding_box_size, random_color


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

def findClusters(points, eps, min_samples):
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
# edges = findEdges(image)
# clusters = findClusters(image, edges)
# print(clusters)

def findEdges(image, minimum = 100, maximum = 200, apertureSize = 3):

    mask_array = np.array(image)

    # Convert the mask to grayscale
    gray_mask = cv2.cvtColor(mask_array, cv2.COLOR_RGBA2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray_mask, minimum, maximum, 3)

    # Iterate through the edges to find edge pixels
    edges = np.argwhere(edges != 0)
    return edges

def do_mesh_transform(model, image):
        m = model
        width = int(random.uniform(2, m.max_mesh_width))
        height = int(random.uniform(2, m.max_mesh_height))
        mesh = create_randomized_aligned_mesh(width,height,image.width,image.height)
        # Create a new image with the mesh
        out = image.transform(image.size, MeshTransform(mesh))
        mask = out if m.use_mask else None
        #draw the transformed image on the original using a mask
        return (out, mask)

def meta_pixel(m, pdf_canvas):

  for file in range(0, m.files):

    # Open the image
    image = Image.open(m.input_path)
    image = image.convert('RGBA')

    min_width = image.width * m.min_width_percentage
    min_height = image.height * m.min_height_percentage
    max_width = image.width * m.max_width_percentage/GOLDEN_RATIO
    max_height = image.height * m.max_height_percentage

    min_dx = - image.width * m.min_dx_percentage
    min_dy = - image.height * m.min_dy_percentage
    max_dx = image.width * m.max_dx_percentage
    max_dy = image.height * m.max_dy_percentage

    # im = make_transparent(image, m.transparent_threshold, above=m.transparent_above)

    edges = findEdges(image, m.edge_min, m.edge_max, m.edge_aperture)
    edge_pixel_cnt = int(len(edges))
    edge_increment = int((edge_pixel_cnt) / m.shapes) if edge_pixel_cnt else 1
    start = int(edge_pixel_cnt % edge_increment)
    for _ in range(0, m.max_layers):


      # Apply the mesh transform
      if m.do_mesh:
        im = make_transparent(image, m.transparent_threshold, above=m.transparent_above)
        out, mask = do_mesh_transform(m, im)
        image.paste(out, None, mask)


      # Create a new image with the mesh
      # if m.save_layer_images:
      #   overlay = Image.new('RGBA', (image.width, image.height), (0, 0, 0, 0))

      for i in range(start, edge_pixel_cnt, edge_increment):

        for shape_layer in range(1, m.max_shape_layers):
          width, height = bounding_box_size(max_width, max_height, min_width, min_height)

          sy, sx = edges[i] - (height // 2, width // 2)

          if sy < 0 or sx < 0:
            continue

          if random.random() > m.prob_shape_destination_equals_source:
              dx = int(random.uniform(min_dx, max_dx))
              dy = int(random.uniform(min_dy, max_dy))
          else:
              dx = sx
              dy = sy

          fill = random_color(vars(m), "fill") if random.random() > m.accent_color_percentage else random_color(vars(m), "accent")

          transforms = []
          if m.do_scale: transforms.append({"name":"scale", "scale_factor": m.scale_factor})
          if m.do_blur: transforms.append({"name":"blur", "radius": m.blur_radius})
          if m.do_invert: transforms.append({"name":"invert"})  

          (out, mask) = transformed_shape(
              image=image,
              x=sx,
              y=sy,
              width=width,
              height=height,
              fill=fill,
              outline=random_color(vars(m), "outline"),
              outline_width=2,
              transforms=transforms
          )

          image.paste(out, (dx, dy), mask)
          # if m.save_layer_images:
          #   overlay.paste(out, (dx, dy), mask)

      # if m.save_layer_images:
      #   filename = f"{m.output_dir}/meta-pixel_{m.image_name}_{m.image_date}_{file}_{_}.png"
      #   overlay.save(filename)

    if len(edges) > 0:
      clusters = findClusters(edges, min_samples=m.min_samples, eps=m.eps)
      image = visualizeClusters(image, clusters)
          
    filename = f"{m.output_dir}/meta-pixel_{m.image_name}_{m.image_date}_{file}.png"

    m.image = image
    if m.create_pdf:
      m.image.save(filename)

    if m.show_image:
      image.show(filename)

    if m.create_pdf:
      # Add a new page to the PDF with the same size as the image
      pdf_canvas.setPageSize((image.width, image.height))

      # Add the image to the PDF
      pdf_canvas.drawImage(filename, 0, 0, preserveAspectRatio=True, width=image.width, height=image.height)

      pdf_canvas.showPage()

def do_meta_pixel(m):
  if m.create_pdf:      
  # Open a PDF for writing
    m.pdf_path = f"{m.output_dir}/{m.image_name}.pdf"
    pdf_canvas = canvas.Canvas(m.pdf_path)
    m.input_image_path = f"{m.input_dir}/{m.image_name}{m.image_ext}"
  else:
    pdf_canvas = None

  # Call the metaPixel function
  meta_pixel(m, pdf_canvas)

  if m.create_pdf:
    # Save and open the PDF
    pdf_canvas.save()

    # Open the PDF (Mac-specific command)
    if m.show_pdf:
      os.system(f"open {m.pdf_path}")
