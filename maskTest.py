import numpy as np
from PIL import Image

# Load the image
image = Image.open('./Rhythms_Circle_DataReferenceSet_1982_2.png')

# Convert to NumPy array
image_array = np.array(image)

# Calculate the sum of RGB channels for each pixel
rgb_sum = image_array[:, :, 0] + image_array[:, :, 1] + image_array[:, :, 2]

# Create the mask
mask = rgb_sum > 512

# Apply the mask to the image (optional)
masked_image = image_array.copy()
masked_image[~mask] = 0  # Set pixels outside the mask to black

# Display the masked image
Image.show(masked_image)

