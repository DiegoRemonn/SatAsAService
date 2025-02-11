from auth import authenticate_earth_engine
from processing import process_image_collection
from visualization import create_map, save_map, open_map
from point_extraction import extract_point_values, extract_region_values
from config import ZARAGOZA_COORDS, AOI, VIS_PARAMS, LOCATIONS, INDICES
from time_series_extraction import get_weekly_image_collection, extract_time_series, save_to_csv
from plot_time_series import plot_indices_per_point, plot_points_per_index
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
    image_collection = get_weekly_image_collection(AOI)

    # Extract time-series data for selected locations
    time_series_data = extract_time_series(image_collection, LOCATIONS, INDICES, time_interval=14)

    # Save the extracted data to a CSV file
    csv_filename = "time_series.csv"
    save_to_csv(time_series_data)

    # Generate visualizations
    print("\nGenerating time-series plots...")
    plot_indices_per_point(csv_filename) # View all indices in each point
    # plot_points_per_index(csv_filename)  # Uncomment to view each index across all points

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

    for lat, lon in LOCATIONS:
        point = ee.Geometry.Point([lon, lat])
        values = extract_point_values(collection, point) # Extract values at the given point

        # Extraer valores de una región de 100x100m
        region_values = extract_region_values(collection, point)

        if values:
            print(f"Values at point ({lat}, {lon}): {values})")
            print(f"Averaged values in 100x100m area ({lat}, {lon}): {region_values}")
        else:
            print(f"Failed to extract values at point ({lat}, {lon}).")

if __name__ == '__main__':
    main()