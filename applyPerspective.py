import cv2
import numpy as np

def apply_perspective(image, src_points, dst_points):


    # Calculate the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Create a meshgrid for the image coordinates
    x, y = np.meshgrid(np.arange(width), np.arange(height))

    # Apply the perspective transform to the coordinates
    coords = np.stack([x.ravel(), y.ravel(), np.ones_like(x).ravel()])
    new_coords = matrix @ coords
    x_new = new_coords[0, :].reshape(height, width) / new_coords[2, :].reshape(height, width)
    y_new = new_coords[1, :].reshape(height, width) / new_coords[2, :].reshape(height, width)

    # Remap the image using the new coordinates
    perspective_image = cv2.remap(image, x_new.astype(np.float32), y_new.astype(np.float32), cv2.INTER_LINEAR)

    return perspective_image


# Read the image
image_name = "hieroglyphics.jpg"
input_dir = "input/"
output_dir = "output/"
image = cv2.imread(f"{input_dir}{image_name}")

# Get the height and width of the image
height, width = image.shape[:2]

# Define source and destination points for the perspective transform
dst_points = np.float32([[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]])
src_points = np.float32([[0, 0], [width * 0.50, 0], [-3.5 * width, height - 1], [4.5 * width, height - 1]])


# Apply the fisheye effect
perspective_image = apply_perspective(image, src_points, dst_points)

# Display the original and fisheye images
# cv2.imshow("Original", image)
cv2.imshow("Perspective", perspective_image)
# cv2.imwrite(f"{output_dir}{image_name}", perspective_image) 
cv2.waitKey(0)
cv2.destroyAllWindows()