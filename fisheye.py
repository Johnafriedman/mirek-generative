import cv2
import numpy as np
import pygame
import sys

def apply_fisheye(image, c_x, c_y, f_x, f_y, strength=1.0):
    """Applies a fisheye effect to an image using cv2.fisheye.initUndistortRectifyMap."""
    height, width = image.shape[:2]
    K = np.array([[f_x, 0, c_x],
                  [0, f_y, c_y],
                  [0, 0, 1]], dtype=np.float32)
    D = np.array([strength, strength, 0, 0], dtype=np.float32)

    # Create the undistort rectify map
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (width, height), cv2.CV_32FC1)

    # Remap the image using the new coordinates
    fisheye_image = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR)

    return fisheye_image

def display_image_with_pygame(image):
    """Displays an image using Pygame."""
    pygame.init()
    height, width = image.shape[:2]
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fisheye Transformation")

    # Initialize font
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24)

    # Convert the image to a format suitable for Pygame
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_surface = pygame.surfarray.make_surface(image_rgb)

    # Main loop
    running = True
    strength = -2.5  # Initial strength
    mouse_down = False
    last_mouse_x = None
    last_mouse_y = None
    MAX_STRENGTH = -50
    MIN_STRENGTH = 50
    INC_STRENGTH = 0.1
    MAX_FOCAL_LENGTH = width * 10
    MIN_FOCAL_LENGTH = width // 10
    INC_FOCAL_LENGTH = 10
    c_x = width // 2
    c_y = height // 2
    f_x = width
    f_y = width

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # use arrow buttons to adjust strength
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    strength = min(strength + 0.1, MIN_STRENGTH)
                elif event.key == pygame.K_DOWN:
                    strength = max(strength - 0.1, MAX_STRENGTH)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_mouse_x = event.pos[0]
                    last_mouse_y = event.pos[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx = event.pos[0] - last_mouse_x
                    dy = event.pos[1] - last_mouse_y

                    strength += dx * INC_STRENGTH
                    strength = max(min(strength, MIN_STRENGTH), MAX_STRENGTH)
                    
                    f_x += dy * INC_FOCAL_LENGTH
                    f_x = max(min(f_x, MAX_FOCAL_LENGTH), MIN_FOCAL_LENGTH)
                    f_y = f_x
                    
                    last_mouse_x = event.pos[0]
                    last_mouse_y = event.pos[1]


                    print(f" dy: {dy}, last_mouse_y: {last_mouse_y}, f_x: {f_x}")

                else:
                    c_x = event.pos[1]
                    c_y = event.pos[0]

                # Regenerate the fisheye image with the new strength
                fisheye_image = apply_fisheye(image, c_x, c_y, f_x, f_y, strength)
                image_rgb = cv2.cvtColor(fisheye_image, cv2.COLOR_BGR2RGB)
                image_surface = pygame.surfarray.make_surface(image_rgb)

        screen.blit(image_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def main(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image {image_path}")
        return

    # set size of image. algorithem generates a square image
    size = 1600
    dim = (size, size)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    # Display the transformed image using Pygame
    display_image_with_pygame(image)

if __name__ == "__main__":
    # get path from commandline if available
    if len(sys.argv) > 1:
        image_path = sys.argv[1]

    else:
        image_path = "input/Photos-001/PXL_20240724_165101814~3.jpg"  # Replace with the path to your image file

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "output/"

    main(image_path)