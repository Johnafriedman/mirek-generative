import cv2
import numpy as np
import matplotlib.pyplot as plt
# Load the image
image_path = 'Rhythms_Circle_DataReferenceSet_1982_2.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# Get image dimensions
rows, cols = image.shape
# Create meshgrid
x, y = np.meshgrid(np.arange(cols), np.arange(rows))
# Create a spiral distortion
center_x, center_y = cols // 2, rows // 2
angle = np.arctan2(y - center_y, x - center_x)
radius = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
# Spiral warp factor
spiral_strength = 0.05
angle_warp = angle + spiral_strength * radius
x_warp = center_x + radius * np.cos(angle_warp)
y_warp = center_y + radius * np.sin(angle_warp)
# Ensure that indices are within bounds
x_warp = np.clip(x_warp, 0, cols - 1).astype(np.float32)
y_warp = np.clip(y_warp, 0, rows - 1).astype(np.float32)
# Apply the spiral warp effect
spiral_warped_image = cv2.remap(image, x_warp, y_warp,
interpolation=cv2.INTER_LINEAR)
# Display original and spiral-warped images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.subplot(1, 2, 2)
plt.imshow(spiral_warped_image, cmap='gray')
plt.title('Spiral Warped Image')
plt.show()
# Save the result
cv2.imwrite('spiral_warped_image.png', spiral_warped_image)
