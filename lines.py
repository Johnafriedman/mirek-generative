from PIL import Image, ImageDraw
import random
import math

def calculate_total_length(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def create_image(image_size):
    return Image.new('RGB', image_size, (255, 255, 255))

def draw_original_line(draw, x1, y1, x2, y2):
    draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=4)

def calculate_segment_endpoints(current_x, current_y, segment_length, total_length, x1, y1, x2, y2):
    end_x = current_x + (segment_length / total_length) * (x2 - x1)
    end_y = current_y + (segment_length / total_length) * (y2 - y1)
    return end_x, end_y

def calculate_perpendicular_direction(dx, dy, segment_width):
    length = math.sqrt(dx**2 + dy**2)
    perp_dx = -dy / length * segment_width
    perp_dy = dx / length * segment_width
    return perp_dx, perp_dy

def apply_offset(current_x, current_y, end_x, end_y, perp_dx, perp_dy):
    current_x += perp_dx
    current_y += perp_dy
    end_x += perp_dx
    end_y += perp_dy
    return current_x, current_y, end_x, end_y

def draw_segment_lines(draw, current_x, current_y, end_x, end_y, segment_width, varied_segment_width, line_color, line_width, randomness_percentage, perp_dx, perp_dy):
    num_lines = int(varied_segment_width)
    dx = end_x - current_x
    dy = end_y - current_y
    random_factor = randomness_percentage / 100

    for i in range(num_lines):
        offset = (i - num_lines / 2) / num_lines * varied_segment_width
        start_offset_x = current_x + offset * perp_dx / segment_width
        start_offset_y = current_y + offset * perp_dy / segment_width
        end_offset_x = end_x + offset * perp_dx / segment_width
        end_offset_y = end_y + offset * perp_dy / segment_width

        start_offset_x += random.uniform(-random_factor, random_factor) * dx
        start_offset_y += random.uniform(-random_factor, random_factor) * dy
        end_offset_x += random.uniform(-random_factor, random_factor) * dx
        end_offset_y += random.uniform(-random_factor, random_factor) * dy

        slope_variation = random.uniform(-random_factor, random_factor)
        dx = end_offset_x - start_offset_x
        dy = (end_offset_y - start_offset_y) * (1 + slope_variation)

        draw.line([start_offset_x, start_offset_y, start_offset_x + dx, start_offset_y + dy], fill=line_color, width=line_width)

def draw_overlapping_segments(draw, segments, total_length, x1, y1, x2, y2, segment_width, varied_segment_width, line_color, line_width, randomness_percentage, overlap_repeats):
    for _ in range(overlap_repeats):
        new_segments = []
        for segment in segments:
            start_x, start_y, end_x, end_y = segment
            if random.choice([True, False]):
                overlap_length = segment_width
                overlap_x1 = end_x - (overlap_length / total_length) * (x2 - x1)
                overlap_y1 = end_y - (overlap_length / total_length) * (y2 - y1)
                overlap_x2 = end_x + (overlap_length / total_length) * (x2 - x1)
                overlap_y2 = end_y + (overlap_length / total_length) * (y2 - y1)

                dx = end_x - start_x
                dy = end_y - start_y
                perp_dx, perp_dy = calculate_perpendicular_direction(dx, dy, segment_width)

                if random.choice([True, False]):
                    perp_dx = -perp_dx
                    perp_dy = -perp_dy

                overlap_x1, overlap_y1, overlap_x2, overlap_y2 = apply_offset(overlap_x1, overlap_y1, overlap_x2, overlap_y2, perp_dx, perp_dy)

                draw_segment_lines(draw, overlap_x1, overlap_y1, overlap_x2, overlap_y2, segment_width, varied_segment_width, line_color, line_width, randomness_percentage, perp_dx, perp_dy)

                new_segments.append((overlap_x1, overlap_y1, overlap_x2, overlap_y2))
        segments.extend(new_segments)

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
    
    total_length = calculate_total_length(x1, y1, x2, y2)
    img = create_image(image_size)
    draw = ImageDraw.Draw(img)
    
    draw_original_line(draw, x1, y1, x2, y2)
    
    current_length = 0
    current_x, current_y = x1, y1
    segments = []
    
    while current_length < total_length:
        segment_length = random.uniform(segment_length_min, segment_length_max) * total_length
        space_length = random.uniform(space_length_min, space_length_max) * total_length
    
        if current_length + segment_length > total_length:
            segment_length = total_length - current_length
    
        end_x, end_y = calculate_segment_endpoints(current_x, current_y, segment_length, total_length, x1, y1, x2, y2)
    
        dx = end_x - current_x
        dy = end_y - current_y
        perp_dx, perp_dy = calculate_perpendicular_direction(dx, dy, segment_width)

        if random.choice([True, False]):
            perp_dx = -perp_dx
            perp_dy = -perp_dy
            
            current_x, current_y, end_x, end_y = apply_offset(current_x, current_y, end_x, end_y, perp_dx, perp_dy)
    
        varied_segment_width = segment_width * random.uniform(width_variation_min, width_variation_max)
        
        draw_segment_lines(draw, current_x, current_y, end_x, end_y, segment_width, varied_segment_width, line_color, line_width, randomness_percentage, perp_dx, perp_dy)
        
        segments.append((current_x, current_y, end_x, end_y))
        
        current_x = end_x + (space_length / total_length) * (x2 - x1)
        current_y = end_y + (space_length / total_length) * (y2 - y1)
        current_length += segment_length + space_length
    
    draw_overlapping_segments(draw, segments, total_length, x1, y1, x2, y2, segment_width, varied_segment_width, line_color, line_width, randomness_percentage, overlap_repeats)
    
    img.show()

# Example usage
params = {
    'x1': 0,
    'y1': 0,
    'x2': 1000,
    'y2': 1000,
    'image_size': (1200, 1200),
    'line_color': (0, 0, 0),
    'segment_width': 50,
    'randomness_percentage': 20,
    'segment_length_min': 0.05,
    'segment_length_max': 0.10,
    'space_length_min': 0.05,
    'space_length_max': 0.10,
    'width_variation_min': 0.8,
    'width_variation_max': 1.2,
    'overlap_repeats': 3,
    'line_width': 1
}
draw_disconnected_line(params)