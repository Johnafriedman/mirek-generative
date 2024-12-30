# App to interpoloate images in a directory and output them to an mp4 file
import os
import cv2
import numpy as np

def process_frame(video, start_img, end_img, steps_per_frame):
    # Interpolate the images
    for j in range(steps_per_frame):
        print(f'Processing frame {j+1}/{steps_per_frame}')
        alpha = j / steps_per_frame
        img = cv2.addWeighted(start_img, 1 - alpha, end_img, alpha, 0)

        # display the image
        cv2.imshow('image', img)

        # Write the image to the video
        video.write(img)

def images_to_mp4(directory, mp4_file, fps=25, steps_per_frame=25):

    # Open the the first image file

    if not os.path.exists(directory):
        raise FileNotFoundError(f'Path {directory} does not exist')
        return

    # Get a list of the files in the directory
    files = os.listdir(directory)
    start_path = os.path.join(directory, files[0])
    first_img = start_img = cv2.imread(start_path)
    # Get the height and width of the images
    height, width, _ = start_img.shape

    # Get the number of pages
    num_pages = len(files)

    # Create a video writer
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video = cv2.VideoWriter(mp4_file, fourcc, fps, (width, height))

    # Loop through the pages
    for i in range(1, num_pages):
        print(f'Processing page {i+1}/{num_pages}')
        # Get the path of the next image
        end_path = os.path.join(directory, files[i])
        end_img = cv2.imread(end_path)

        # Process the frames
        process_frame(video, start_img, end_img, steps_per_frame)

        start_img = end_img

    end_img = first_img
    process_frame(video, start_img, end_img, steps_per_frame)

    # Release the video
    video.release()
    cv2.destroyAllWindows()

# Main function
if __name__ == '__main__':
    # Define the arguments

    args = {
        'directory': 'output/meta-pixel_IMG_0762_2024-12-30154950',
        'mp4_file': 'output/IMG_0762.mp4',
        'fps': 12,
        'steps_per_frame': 32
    }

    # Call the pdf_to_mp4 function
    images_to_mp4(args['directory'], args['mp4_file'], args['fps'], args['steps_per_frame'])