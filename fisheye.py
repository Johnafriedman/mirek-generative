import cv2
import numpy as np
import pygame
import sys

def apply_fisheye(image, strength=1.0):
    """Applies a fisheye effect to an image using cv2.fisheye.initUndistortRectifyMap."""
    height, width = image.shape[:2]
    K = np.array([[width, 0, width / 2],
                  [0, width, height / 2],
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

    # Convert the image to a format suitable for Pygame
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_surface = pygame.surfarray.make_surface(image_rgb)

    # Main loop
    running = True
    strength = -2.5  # Initial strength
    mouse_down = False
    last_mouse_x = None
    MAX_STRENGTH = -50
    MIN_STRENGTH = -1
    INC_STRENGTH = 0.1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # use arrow buttons to adjust strength
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_mouse_x = event.pos[0]
                elif event.button == 4:  # Mouse wheel up
                    strength = min(strength + 0.1, MIN_STRENGTH)
                elif event.button == 5:  # Mouse wheel down
                    strength = max(strength - 0.1, MAX_STRENGTH)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                dx = event.pos[0] - last_mouse_x
                strength += dx * INC_STRENGTH
                strength = max(min(strength, MIN_STRENGTH), MAX_STRENGTH)
                last_mouse_x = event.pos[0]

                # Regenerate the fisheye image with the new strength
                fisheye_image = apply_fisheye(image, strength)
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

# scale image down proportionately so the width is 1280
    scale_percent = 1280 / image.shape[1] * 100
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


    # Display the transformed image using Pygame
    display_image_with_pygame(image)

if __name__ == "__main__":
    image_path = "input/Photos-001/Glass1.jpg"  # Replace with the path to your image file
    main(image_path)