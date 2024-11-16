import cv2
import numpy as np

def apply_fisheye(image, strength=-2.5):
    """Applies a simple fisheye effect to an image."""

    height, width = image.shape[:2]
    center_x, center_y = width // 2, height // 2

    # Create a meshgrid for the image coordinates
    x, y = np.meshgrid(np.arange(width), np.arange(height))

    # Calculate the distance from the center for each pixel
    radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)

    # Calculate the new coordinates for the fisheye effect
    theta = np.arctan2(y - center_y, x - center_x)
    r = radius * (1 + strength * (radius / max(width, height))**2)
    x_new = center_x + r * np.cos(theta)
    y_new = center_y + r * np.sin(theta)

    # Remap the image using the new coordinates
    fisheye_image = cv2.remap(image, x_new.astype(np.float32), y_new.astype(np.float32), cv2.INTER_LINEAR)

    return fisheye_image





def do_apply_fisheye():
    # Read the image
    image_name = "BirdsWire.jpg"
    input_dir = "input/Photos-001/"
    output_dir = "output/"
    image = cv2.imread(f"{input_dir}{image_name}")

    # Define the fisheye distortion strength
    strength = -2.5

    # Apply the fisheye effect
    fisheye_image = apply_fisheye(image, strength)

    # Display the original and fisheye images
    # cv2.imshow("Original", image)
    cv2.imshow("Fisheye", fisheye_image)
    cv2.imwrite(f"{output_dir}{image_name}", fisheye_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    do_apply_fisheye()

