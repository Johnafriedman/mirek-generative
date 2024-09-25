from PIL import Image, ImageDraw
import random
import math

def draw_disconnected_line(params):
    x1, y1 = params['x1'], params['y1']
    x2, y2 = params['x2'], params['y2']
    image_size = params.get('image_size', (1200, 1200))
    line_color = params.get('line_color', (0, 0, 0))
    segment_width = params.get('segment_width', 50)
    randomness_percentage = params.get('randomness_percentage', 20)
    segment_length_min = params.get('segment_length_min', 0.05)
    segment_length_max = params.get('segment_length_max', 0.10)
    space_length_min = params.get('space_length_min', 0.05)
    space_length_max = params.get('space_length_max', 0.10)
    width_variation_min = params.get('width_variation_min', 0.8)
    width_variation_max = params.get('width_variation_max', 1.2)
    overlap_repeats = params.get('overlap_repeats', 3)
    line_width = params.get('line_width', 1)
    
    # Calculate the total length of the line
    total_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    # Create an image with white background
    img = Image.new('RGB', image_size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw the original line in black with width 4
    draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=4)
    
    current_length = 0
    current_x, current_y = x1, y1
    segments = []
    
    while current_length < total_length:
        # Determine the length of the next segment
        segment_length = random.uniform(segment_length_min, segment_length_max) * total_length
        # Determine the length of the space after the segment
        space_length = random.uniform(space_length_min, space_length_max) * total_length
    
        # Calculate the end point of the segment
        if current_length + segment_length > total_length:
            segment_length = total_length - current_length
    
        end_x = current_x + (segment_length / total_length) * (x2 - x1)
        end_y = current_y + (segment_length / total_length) * (y2 - y1)
    
        # Calculate the perpendicular direction
        dx = end_x - current_x
        dy = end_y - current_y
        length = math.sqrt(dx**2 + dy**2)
        perp_dx = -dy / length * segment_width
        perp_dy = dx / length * segment_width

        # Randomly decide whether to offset the segment
        if random.choice([True, False]):
            # Randomly choose the direction of the offset
            if random.choice([True, False]):
                perp_dx = -perp_dx
                perp_dy = -perp_dy
            
            # Apply the offset
            current_x += perp_dx
            current_y += perp_dy
            end_x += perp_dx
            end_y += perp_dy
    
        # Vary the segment width
        varied_segment_width = segment_width * random.uniform(width_variation_min, width_variation_max)
        
        # Draw multiple lines of specified width to fill the rectangle
        num_lines = int(varied_segment_width)
        for i in range(num_lines):
            # Calculate the start and end points along the perpendicular direction
            offset = (i - num_lines / 2) / num_lines * varied_segment_width
            start_offset_x = current_x + offset * perp_dx / segment_width
            start_offset_y = current_y + offset * perp_dy / segment_width
            end_offset_x = end_x + offset * perp_dx / segment_width
            end_offset_y = end_y + offset * perp_dy / segment_width
            
            # Add or subtract a percentage to the beginning and end points
            random_factor = randomness_percentage / 100
            start_offset_x += random.uniform(-random_factor, random_factor) * dx
            start_offset_y += random.uniform(-random_factor, random_factor) * dy
            end_offset_x += random.uniform(-random_factor, random_factor) * dx
            end_offset_y += random.uniform(-random_factor, random_factor) * dy
            
            # Calculate the slope with a random variation
            slope_variation = random.uniform(-random_factor, random_factor)
            dx = end_offset_x - start_offset_x
            dy = (end_offset_y - start_offset_y) * (1 + slope_variation)
            
            # Draw the line
            draw.line([start_offset_x, start_offset_y, start_offset_x + dx, start_offset_y + dy], fill=line_color, width=line_width)
        
        segments.append((current_x, current_y, end_x, end_y))
        
        # Update the current position and length
        current_x = end_x + (space_length / total_length) * (x2 - x1)
        current_y = end_y + (space_length / total_length) * (y2 - y1)
        current_length += segment_length + space_length
    
    # Repeat the overlapping process
    for _ in range(overlap_repeats):
        new_segments = []
        for segment in segments:
            start_x, start_y, end_x, end_y = segment
            if random.choice([True, False]):
                # Calculate the overlapping segment
                overlap_length = segment_width
                overlap_x1 = end_x - (overlap_length / total_length) * (x2 - x1)
                overlap_y1 = end_y - (overlap_length / total_length) * (y2 - y1)
                overlap_x2 = end_x + (overlap_length / total_length) * (x2 - x1)
                overlap_y2 = end_y + (overlap_length / total_length) * (y2 - y1)
                
                # Calculate the perpendicular direction for the connecting segment
                dx = end_x - start_x
                dy = end_y - start_y
                length = math.sqrt(dx**2 + dy**2)
                perp_dx = -dy / length * segment_width
                perp_dy = dx / length * segment_width
                
                # Randomly choose the direction of the offset
                if random.choice([True, False]):
                    perp_dx = -perp_dx
                    perp_dy = -perp_dy
                
                # Apply the offset to the connecting segment
                overlap_x1 += perp_dx
                overlap_y1 += perp_dy
                overlap_x2 += perp_dx
                overlap_y2 += perp_dy
                
                # Vary the segment width
                varied_segment_width = segment_width * random.uniform(width_variation_min, width_variation_max)
                
                # Draw multiple lines of specified width for the overlapping segment
                num_lines = int(varied_segment_width)
                for i in range(num_lines):
                    # Calculate the start and end points along the perpendicular direction
                    offset = (i - num_lines / 2) / num_lines * varied_segment_width
                    start_offset_x = overlap_x1 + offset * perp_dx / segment_width
                    start_offset_y = overlap_y1 + offset * perp_dy / segment_width
                    end_offset_x = overlap_x2 + offset * perp_dx / segment_width
                    end_offset_y = overlap_y2 + offset * perp_dy / segment_width
                    
                    # Add or subtract a percentage to the beginning and end points
                    start_offset_x += random.uniform(-random_factor, random_factor) * dx
                    start_offset_y += random.uniform(-random_factor, random_factor) * dy
                    end_offset_x += random.uniform(-random_factor, random_factor) * dx
                    end_offset_y += random.uniform(-random_factor, random_factor) * dy
                    
                    # Calculate the slope with a random variation
                    slope_variation = random.uniform(-random_factor, random_factor)
                    dx = end_offset_x - start_offset_x
                    dy = (end_offset_y - start_offset_y) * (1 + slope_variation)
                    
                    # Draw the line
                    draw.line([start_offset_x, start_offset_y, start_offset_x + dx, start_offset_y + dy], fill=line_color, width=line_width)
                
                new_segments.append((overlap_x1, overlap_y1, overlap_x2, overlap_y2))
        segments.extend(new_segments)
    
    # Save or display the image
    img.show()

# Example usage
params = {
    'x1': 0,
    'y1': 0,
    'x2': 1200,
    'y2': 1200,
    'image_size': (1200, 1200),
    'line_color': (0, 0, 0),
    'segment_width': 20,
    'randomness_percentage': 20,
    'segment_length_min': 0.08,
    'segment_length_max': 0.15,
    'space_length_min': 0.05,
    'space_length_max': 0.10,
    'width_variation_min': 1.2,
    'width_variation_max': 3.2,
    'overlap_repeats': 3,
    'line_width': 1
}
draw_disconnected_line(params)