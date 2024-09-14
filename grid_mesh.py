import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image using OpenCV
image_path = 'your_image_path_here.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# Get image dimensions
rows, cols = image.shape
# Create meshgrid
x, y = np.meshgrid(np.arange(cols), np.arange(rows))
# Create the mesh warp effect
# You can modify the sinusoidal wave for more drastic or subtle warping
x_warp = x + 20 * np.sin(2 * np.pi * y / 60) # Warping along the x-axis with
sinusoidal curve
y_warp = y + 20 * np.sin(2 * np.pi * x / 60) # Warping along the y-axis
# Ensure that indices are within bounds
x_warp = np.clip(x_warp, 0, cols - 1).astype(np.float32)
y_warp = np.clip(y_warp, 0, rows - 1).astype(np.float32)
# Apply the mesh warp using remap function
warped_image = cv2.remap(image, x_warp, y_warp, interpolation=cv2.INTER_LINEAR)
# Display the original and warped image using matplotlib
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.subplot(1, 2, 2)
plt.imshow(warped_image, cmap='gray')
plt.title('Mesh Warped Image')
plt.show()
# Save the output image
cv2.imwrite('mesh_warped_image.png', warped_image)
