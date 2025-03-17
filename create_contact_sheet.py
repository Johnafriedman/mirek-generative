from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_contact_sheet(
    image_folder,
    output_filename="contact_sheet.png",
    rows=4,
    columns=3,
    dpi=300,
    margin_inches=0.5,
    label_font_size=12,
    thumbnail_padding_pixels=10,
    orientation="landscape",
):
    """
    Generates a contact sheet from images in a folder.

    Args:
        image_folder (str): Path to the folder containing images.
        output_filename (str, optional): Name of the output contact sheet file. Defaults to "contact_sheet.png".
        rows (int, optional): Number of rows in the contact sheet. Defaults to 4.
        columns (int, optional): Number of columns in the contact sheet. Defaults to 3.
        dpi (int, optional): Dots per inch for the output image. Defaults to 300.
        margin_inches (float, optional): Margin around the edge of the page in inches. Defaults to 0.5.
        label_font_size (int, optional): Font size for the image labels. Defaults to 30.
        thumbnail_padding_pixels (int, optional): Padding around each thumbnail in pixels. Defaults to 10.
        orientation (str, optional): Page orientation, either "landscape" or "portrait". Defaults to "landscape".
    """

    # --- Constants and Calculations ---
    paper_width_inches = 11
    paper_height_inches = 8.5

    # Swap width and height if portrait
    if orientation == "portrait":
        paper_width_inches, paper_height_inches = paper_height_inches, paper_width_inches

    margin_pixels = int(margin_inches * dpi)

    # Calculate the available space for thumbnails, considering padding and label height
    available_width_pixels = int(paper_width_inches * dpi) - 2 * margin_pixels
    available_height_pixels = int(paper_height_inches * dpi) - 2 * margin_pixels

    # Calculate thumbnail size, accounting for padding
    thumbnail_width_pixels = (
        available_width_pixels - (columns - 1) * thumbnail_padding_pixels
    ) // columns
    # We need to account for the label height in the available height
    # We will assume the label height is 1.2 times the font size
    label_height = int(label_font_size * 1.2)
    thumbnail_height_pixels = (
        available_height_pixels
        - (rows - 1) * thumbnail_padding_pixels
        - rows * label_height
    ) // rows

    thumbnail_size = (thumbnail_width_pixels, thumbnail_height_pixels)

    # --- Image Processing ---
    image_paths = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if os.path.isfile(os.path.join(image_folder, f))
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
    ]

    if not image_paths:
        print("No images found in the specified folder.")
        return

    num_images = len(image_paths)
    total_cells = rows * columns

    # Calculate the number of pages needed
    num_pages = math.ceil(num_images / total_cells)

    # --- Page Creation Loop ---
    for page in range(num_pages):
        # Create a new image for the contact sheet
        contact_sheet = Image.new(
            "RGB",
            (int(paper_width_inches * dpi), int(paper_height_inches * dpi)),
            "white",
        )
        draw = ImageDraw.Draw(contact_sheet)

        # Calculate the starting and ending index for the current page
        start_index = page * total_cells
        end_index = min((page + 1) * total_cells, num_images)

        # --- Thumbnail Placement Loop ---
        image_index = 0
        for row in range(rows):
            for col in range(columns):
                if start_index + image_index >= end_index:
                    break  # Exit if we've processed all images

                path = image_paths[start_index + image_index]
                filename = os.path.basename(path)

                try:
                    img = Image.open(path)
                    img.thumbnail(thumbnail_size)

                    # Calculate position for thumbnail, including padding
                    x_offset = margin_pixels + col * (
                        thumbnail_width_pixels + thumbnail_padding_pixels
                    )
                    y_offset = margin_pixels + row * (
                        thumbnail_height_pixels
                        + thumbnail_padding_pixels
                        + label_height
                    )

                    # Add label above the thumbnail
                    label_x = x_offset
                    label_y = y_offset - label_height  # Place label above
                    draw.text((label_x, label_y), filename, fill="black", font_size=label_font_size)

                    # Paste thumbnail
                    contact_sheet.paste(img, (x_offset, y_offset))

                except Exception as e:
                    print(f"Error processing image {filename}: {e}")

                image_index += 1

        # --- Save the Page ---
        if num_pages > 1:
            page_output_filename = output_filename.replace(
                ".png", f"_page_{page+1}.png"
            )
        else:
            page_output_filename = output_filename
        contact_sheet.save(page_output_filename, dpi=(dpi, dpi))
        print(f"Contact sheet saved as {page_output_filename}")


if __name__ == "__main__":
    folder_path = input("Enter the path to the image folder: ")
    orientation = input(
        "Enter page orientation (landscape or portrait, default is landscape): "
    ).lower()
    if orientation not in ["landscape", "portrait"]:
        orientation = "landscape"
        print("Invalid orientation. Defaulting to landscape.")
    create_contact_sheet(
        folder_path,
        rows=3,
        columns=4,
        dpi=300,
        margin_inches=0.5,
        label_font_size=30,
        thumbnail_padding_pixels=10,
        orientation=orientation,
    )
