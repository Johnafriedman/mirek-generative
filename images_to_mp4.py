# App to interpoloate images in a directory and output them to an mp4 file
import os
import cv2
import numpy as np
import ffmpeg

def create_video_writer(mp4_file, fps, width, height):
    process = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}', r=fps)
        .output(mp4_file, pix_fmt='yuv420p', vcodec='libx264')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    return process

def write_frame(process, frame):
    process.stdin.write(frame.astype(np.uint8).tobytes())

def close_video_writer(process):
    process.stdin.close()
    process.wait()

def add_pre_fade_delay(process, img, pre_fade_delay_frames):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    for j in range(pre_fade_delay_frames):
        # print(f'Adding pre-fade delay {j+1}/{pre_fade_delay_frames}')
        write_frame(process, img)

def process_frame(process, start_img, end_img, steps_per_frame):
    # Interpolate the images
    for j in range(steps_per_frame):
        # print(f'Processing frame {j+1}/{steps_per_frame}')
        alpha = j / steps_per_frame
        img = cv2.addWeighted(start_img, 1 - alpha, end_img, alpha, 0)

        # Convert the image to ffmpeg format
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Write the image to the video
        write_frame(process, img)

def images_to_mp4(args):

    directory, mp4_file, fps, steps_per_frame, pre_fade_delay = args.values()
    pre_fade_delay_frames = int(fps * pre_fade_delay)

    # Open the the first image file

    if not os.path.exists(directory):
        raise FileNotFoundError(f'Path {directory} does not exist')
        return

    # Get a list of the files in the directory
    files = os.listdir(directory)
    # remove any system files
    files = [f for f in files if not f.startswith('.')]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    # Get the path of the first image
    start_path = os.path.join(directory, files[0])
    start_img = cv2.imread(start_path)
    # crop so height and witdth are divisible by 2
    start_img = start_img[:start_img.shape[0]//2*2, :start_img.shape[1]//2*2]   

    first_img = start_img
    # Get the height and width of the images
    height, width, _ = start_img.shape

    # Get the number of pages
    num_pages = len(files)

    # Check if the file exists and delete it if it does
    if os.path.exists(mp4_file):
        os.remove(mp4_file)

    process = create_video_writer(mp4_file, fps, width, height)
    # Loop through the pages
    for i in range(1, num_pages):
        # Get the path of the next image
        end_path = os.path.join(directory, files[i])
        end_img = cv2.imread(end_path)
        end_img = end_img[:end_img.shape[0]//2*2, :end_img.shape[1]//2*2]   

        if end_img.shape != start_img.shape:
            print(f'Image {end_path} is not the same size as the first image. Skipping')
            continue


        # add a pre-fade delay
        add_pre_fade_delay (process, start_img, pre_fade_delay_frames)

        print(f'Processing page {i+1}/{num_pages} {start_path} -> {end_path}')

        # Process the frames
        process_frame(process, start_img, end_img, steps_per_frame)

        start_img = end_img

    end_img = first_img
    add_pre_fade_delay (process, start_img, pre_fade_delay_frames)
    process_frame(process, start_img, end_img, steps_per_frame)

    # Release the video
    close_video_writer(process)

# Main function
if __name__ == '__main__':
    # Define the arguments

    args = {
        'directory': 'output/pixel_Rhythms_2 Eclipses_6828_3/Illustrations',
        'mp4_file': 'output/pixel_Rhythms_2 Eclipses_6828_3/Illustrations_Rhythms_2_Eclipses_6828_3.mp4',
        'fps': 12,
        'steps_per_frame': 36,
        'pre_fade_delay': 5,
    }

    # Call the pdf_to_mp4 function
    images_to_mp4(args)