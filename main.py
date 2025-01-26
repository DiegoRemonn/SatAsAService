from auth import authenticate_earth_engine
from processing import process_image_collection
from visualization import create_map, save_map, open_map
from point_extraction import extract_point_values
from config import ZARAGOZA_COORDS, AOI, VIS_PARAMS
import ee

def main():
    """
    Main function to execute the workflow: authenticate Google Earth Engine, process Satellite data,
    create the map, save it as an HTML file, and open it.
    :return: None
    """
    # Authenticate Google Earth Engine
    authenticate_earth_engine()

    # Process Satellite image collection
    collection = process_image_collection(AOI)

    # Create the map
    m = create_map(ZARAGOZA_COORDS, collection, VIS_PARAMS)

    # Ask the user for the HTML file name
    html_filename = input("Enter the name for the HTML file (e.g., map.html): ").strip()

    # Ensure the file has a .html extension
    if not html_filename.endswith(".html"):
        html_filename += ".html"

    # Save the map as an HTML file
    html_file = save_map(m, html_filename)

    # Open the map in the browser
    open_map(html_file)

    # Ask the user for a point to extract values
    lat = float(input("Enter latitude for the point: "))
    lon = float(input("Enter longitude for the point: "))
    point = ee.Geometry.Point([lon, lat])

    # Extract values at the given point
    values = extract_point_values(collection, point)

    if values:
        print(f"Values at point ({lat}, {lon}): {values})")
    else:
        print("Failed to extract values at the specified point.")

if __name__ == '__main__':
    main()