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
# Create sinusoidal distortion with added randomness
wave_amplitude = 30 # Amplitude of the wave
wave_frequency = 80 # Frequency of the wave
random_factor = 15 # Intensity of the random component
x_warp = x + wave_amplitude * np.sin(2 * np.pi * y / wave_frequency) +
random_factor * (np.random.rand(rows, cols) - 0.5)
y_warp = y + wave_amplitude * np.sin(2 * np.pi * x / wave_frequency) +
random_factor * (np.random.rand(rows, cols) - 0.5)
# Ensure that indices are within bounds
x_warp = np.clip(x_warp, 0, cols - 1).astype(np.float32)
y_warp = np.clip(y_warp, 0, rows - 1).astype(np.float32)
# Apply the non-linear grid warping
non_linear_warped_image = cv2.remap(image, x_warp, y_warp,
interpolation=cv2.INTER_LINEAR)
# Display original and warped images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.subplot(1, 2, 2)
plt.imshow(non_linear_warped_image, cmap='gray')
plt.title('Non-Linear Warped Image')
plt.show()
# Save the result
cv2.imwrite('non_linear_warped_image.png', non_linear_warped_image)
