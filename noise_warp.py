import cv2
import numpy as np
import matplotlib.pyplot as plt
# Load the image
image_path = './input/Rhythms_Circle_DataReferenceSet_1982_2.png'
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# Get image dimensions
rows, cols = image.shape
# Create meshgrid
x, y = np.meshgrid(np.arange(cols), np.arange(rows))
# Create random noise for warping
noise_amplitude = 20 # Control the intensity of the noise-based warp
x_noise = noise_amplitude * (np.random.rand(rows, cols) - 0.5)
y_noise = noise_amplitude * (np.random.rand(rows, cols) - 0.5)
# Apply noise to the grid
x_warp = x + x_noise
y_warp = y + y_noise
# Ensure that indices are within bounds
x_warp = np.clip(x_warp, 0, cols - 1).astype(np.float32)
y_warp = np.clip(y_warp, 0, rows - 1).astype(np.float32)
# Apply the noise-based warp
noise_warped_image = cv2.remap(image, x_warp, y_warp,
interpolation=cv2.INTER_LINEAR)
# Display original and noise-warped images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.subplot(1, 2, 2)
plt.imshow(noise_warped_image, cmap='gray')
plt.title('Random Noise Warped Image')
plt.show()
# Save the result
cv2.imwrite('noise_warped_image.png', noise_warped_image)
