import cv2
import numpy as np
import matplotlib.pyplot as plt
# Load the image
image_path = 'your_image_path_here.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# Get image dimensions
rows, cols = image.shape
# Create meshgrid
x, y = np.meshgrid(np.arange(cols), np.arange(rows))
# Calculate distance from the center
center_x, center_y = cols // 2, rows // 2
distance_from_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
# Create radial warp distortion
# Adjust the factors for different levels of distortion
warp_factor = 1 + 0.001 * distance_from_center
x_warp = (x - center_x) * warp_factor + center_x
y_warp = (y - center_y) * warp_factor + center_y
# Ensure that indices are within bounds
x_warp = np.clip(x_warp, 0, cols - 1).astype(np.float32)
y_warp = np.clip(y_warp, 0, rows - 1).astype(np.float32)
# Apply the radial warp effect
radial_warped_image = cv2.remap(image, x_warp, y_warp,
interpolation=cv2.INTER_LINEAR)
# Display original and radial warped images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.subplot(1, 2, 2)
plt.imshow(radial_warped_image, cmap='gray')
plt.title('Radial Warped Image')
plt.show()
# Save the result
cv2.imwrite('radial_warped_image.png', radial_warped_image)
