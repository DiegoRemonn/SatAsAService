import imageio
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

from auth import reconnect_gee
from config import GALLOCANTA_LOCATION

def create_colorbar(width, height, ramp, font=None):
    """
    Generates a PIL image containing a vertical gradient based on the provided ramp.

    The ramp is a list of tuples (value, color_hex) that defines breakpoints for the gradient.
    The generated image also includes labels drawn to the right side.

    Args:
        width (int): The width (in pixels) for the gradient area.
        height (int): The height (in pixels) for the gradient.
        ramp (list of tuples): List of (value, color_hex) breakpoints, e.g., [(-0.8, '#800000'), ...].
        font (PIL.ImageFont, optional): Font used to draw the labels. If None, a default bold font (arialbd.ttf)
                                        is attempted with size 4.

    Returns:
        PIL.Image: An RGBA image of the colorbar with labels.
    """
    colorbar = Image.new('RGBA', (width * 3 + 8, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(colorbar)

    min_val, _ = ramp[0]
    max_val, _ = ramp[-1]
    val_range = max_val - min_val

    def interpolate_color(c1, c2, t):
        """
        Linearly interpolates between two colors.

        Args:
            c1 (tuple): First color as (R, G, B).
            c2 (tuple): Second color as (R, G, B).
            t (float): Interpolation parameter between 0 and 1.

        Returns:
            tuple: Interpolated color as (R, G, B).
        """
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    # Convert hex colors to RGB and store in ramp_rgb.
    ramp_rgb = []
    for val, hexcolor in ramp:
        rgb = tuple(int(hexcolor[i:i+2], 16) for i in (1, 3, 5))
        ramp_rgb.append((rgb, val))

    # Create the vertical gradient.
    for row in range(height):
        frac = row / float(height - 1)
        current_val = min_val + frac * val_range

        color_row = (0, 0, 0)
        for i in range(len(ramp_rgb) - 1):
            val_i = ramp_rgb[i][1]
            val_ip1 = ramp_rgb[i+1][1]
            if val_i <= current_val <= val_ip1:
                local_frac = (current_val - val_i) / (val_ip1 - val_i)
                c1 = ramp_rgb[i][0]
                c2 = ramp_rgb[i+1][0]
                color_row = interpolate_color(c1, c2, local_frac)
                break
        else:
            # If out of range, use the extreme color.
            if current_val < ramp_rgb[0][1]:
                color_row = ramp_rgb[0][0]
            elif current_val > ramp_rgb[-1][1]:
                color_row = ramp_rgb[-1][0]

        # Fill the current row of the gradient.
        for col in range(width):
            colorbar.putpixel((col, height - 1 - row), color_row)

    # Set up the font if not provided.
    if not font:
        try:
            font = ImageFont.truetype("arialbd.ttf", 4)
        except IOError:
            font = ImageFont.load_default()

    # Draw labels to the right of the gradient.
    text_x = width + 5
    for val, hexcolor in ramp:
        frac_label = (val - min_val) / val_range
        label_row = height - int(frac_label * (height - 1))
        label_str = f"{val:g}"

        # Apply a dynamic vertical offset based on the value.
        if -0.5 < val < 0 or val > 0.5:
            y_offset = 1   # Move down
        elif 0.5 > val > 0:
            y_offset = -10 # Move up
        elif val < -0.5:
            y_offset = -15 # Move up
        else:
            y_offset = 0   # For zero, centered

        # Draw the text applying the offset
        draw.text((text_x, label_row + y_offset), label_str, fill="black", font=font)

    return colorbar

def draw_marker(draw, point, aoi_info, image_size, marker_color="red", marker_radius=5, text="Localidad"):
    """
    Draws a marker (a circle) on an image at a given geographic location and places a label above it.

    This function converts geographic coordinates into pixel coordinates using the AOI's boundary.

    Args:
        draw (PIL.ImageDraw): Drawing context.
        point (tuple): (longitude, latitude) for the marker.
        aoi_info (dict): AOI information from ee.Geometry.getInfo().
        image_size (tuple): (width, height) of the image in pixels.
        marker_color (str): Color of the marker.
        marker_radius (int): Radius (in pixels) of the marker circle.
        text (str): Text label to display above the marker.
    """
    # Extract polygon coordinates from the AOI info.
    coords = aoi_info["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    xmin, xmax = min(lons), max(lons)
    ymin, ymax = min(lats), max(lats)

    width_px, height_px = image_size
    lon, lat = point
    # Convert geographic coordinate to pixel coordinate.
    x_pixel = (lon - xmin) / (xmax - xmin) * width_px
    y_pixel = (ymax - lat) / (ymax - ymin) * height_px

    # Draw the circular marker.
    draw.ellipse(
        [(x_pixel - marker_radius, y_pixel - marker_radius),
         (x_pixel + marker_radius, y_pixel + marker_radius)],
        fill=marker_color
    )

    # Load the font for the marker label.
    try:
        font = ImageFont.truetype("arialbd.ttf", 12)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text width for horizontal centering.
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    # Determine label position above the marker.
    # Centered horizontally and, vertically placed 5 pixels above the marker
    x_text = x_pixel - text_width / 2
    y_text = y_pixel - marker_radius - 5 - (bbox[3] - bbox[1])
    draw.text((x_text, y_text), text, fill=marker_color, font=font)

def download_thumbnail(url, timeout=60, check_interval=0.5):
    """
    Attempts to download the image from the specified URL, waiting until the image is available.

    If a 401 error is detected, it attempts to re-authenticate and reconnect to Earth Engine.

    Args:
        url (str): URL of the image.
        timeout (float): Maximum time in seconds to wait for a successful download.
        check_interval (float): Seconds to wait between successive attempts.

    Returns:
        requests.Response: The HTTP response if the image is successfully downloaded, or None on timeout.
    """
    start_time = time.time()
    reconnect_done = False
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            elif response.status_code == 401 and not reconnect_done:
                print(f"\nError 401 detected at {url}. Attempting to re-authenticate and reconnect to EE...")
                if reconnect_gee():
                    reconnect_done = True
                else:
                    print("Failed to reconnect to EE.")
            else:
                print(f"\nError downloading image from: {url} (Status code: {response.status_code})")

            # Check the timeout
            if time.time() - start_time > timeout:
                print(f"\nTimeout reached while downloading image from: {url}")
                return None
            time.sleep(check_interval)
        except Exception as e:
            print(f"\nException while trying to download {url}: {e}")
            if time.time() - start_time > timeout:
                print(f"\nTimeout reached (exception) while downloading {url}")
                return None
            time.sleep(check_interval)

def create_gif_from_urls(urls, dates, legend_palette, aoi, output_filename='laguna_gallocanta_evolucion.gif', duration=1):
    """
    Downloads images from a list of URLs, annotates each image with a date label, pastes a static colorbar legend,
    draws a geographic marker, and creates an animated GIF.

    Args:
        urls (list of str): List of image URLs.
        dates (list of str): List of corresponding date strings for each image.
        legend_palette (str): Identifier for the satellite layer used ('ndmi' or other).
        aoi (ee.Geometry): Area of interest; its .getInfo() is used to determine pixel mappings.
        output_filename (str): Filename for the output GIF.
        duration (float): Time (in seconds) each frame is displayed in the GIF.
    """
    if legend_palette == "ndmi":
        legend_items = [
            (-0.8, '#800000'),  # Dark red (low moisture)
            (-0.24, '#ff0000'),  # Bright red (dry area)
            (-0.032, '#ffff00'),  # Yellow (transition moisture)
            (0.032, '#00ffff'),  # Cyan (moderate moisture)
            (0.24, '#0000ff'),  # Bright blue (high moisture)
            (0.8, '#000080')  # Dark blue (maximum moisture)
        ]
    else:
        legend_items = [
            (0.0, '#ffffcc'),
            (0.2, '#c2e699'),
            (0.4, '#78c679'),
            (0.6, '#31a354'),
            (0.8, '#006837'),
        ] # Green colors for ERA5 satellite frames

    images = []
    counter = 0
    total = len(urls)

    # Generate the continuous colorbar legend once.
    colorbar_width = 20
    colorbar_height = 100

    try:
        font_bar = ImageFont.truetype("arialbd.ttf", 15)
    except IOError:
        font_bar = ImageFont.load_default()

    legend_img = create_colorbar(colorbar_width, colorbar_height, legend_items, font=font_bar)

    marker_point = GALLOCANTA_LOCATION
    aoi_info = aoi.getInfo()

    for url, date_text in zip(urls, dates):
        response = download_thumbnail(url, timeout=20)
        if response is not None:
            # Read image from binary data.
            img_array = imageio.v2.imread(BytesIO(response.content))
            pil_img = Image.fromarray(img_array)
            draw = ImageDraw.Draw(pil_img)

            try:
                font = ImageFont.truetype("arialbd.ttf", 20)
            except IOError:
                font = ImageFont.load_default()

            # Calculate text size and position in the bottom-right corner.
            text = date_text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            width, height = pil_img.size
            x_date = width - text_width - 5  # 5 pixels from right border
            y_date = height - text_height - 5  # 5 pixels from bottom border
            draw.text((x_date, y_date), text, fill="black", font=font)

            # Paste the colorbar legend in the top-right corner.
            # Make sure the bar is not bigger than the frame
            x_bar = width - legend_img.width - 5
            y_bar = 5
            pil_img.paste(legend_img, (x_bar, y_bar), legend_img)

            # Draw the geographic marker with label.
            draw_marker(draw, marker_point, aoi_info, pil_img.size, marker_color="black", marker_radius=3, text="Laguna de Gallocanta")

            # Convert annotated image to NumPy array and append to frames list.
            annotated_array = np.array(pil_img)
            images.append(annotated_array)
        else:
            print(f"Final error downloading the frame from: {url}")
        counter += 1

        # Update progress on the same line.
        progress = counter / total
        bar_length = 50 # Total length of the bar
        filled_length = int(bar_length * progress)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        print(f"\rProgress: [{bar}] {progress*100:6.2f}%", end="", flush=True)

    print(f"\n")
    # Create the animated GIF.
    imageio.mimsave(output_filename, images, duration=duration)
    print(f"GIF created and saved as {output_filename}")

def merge_gifs(gif_paths, output_path, duration=0.1):
    """
    Merges multiple GIFs consecutively into a single animated GIF.

    Args:
        gif_paths (list of str): List of file paths for the GIFs to merge.
        output_path (str): File path for the output merged GIF.
        duration (float): Duration (in seconds) each frame is displayed in the final GIF.

    Returns:
        None
    """
    all_frames = []
    for path in gif_paths:
        try:
            frames = imageio.mimread(path)
            all_frames.extend(frames)
        except Exception as e:
            print(f"Error reading {path}: {e}")
    imageio.mimsave(output_path, all_frames, duration=duration)
    print(f"Merged GIF saved at {output_path}")