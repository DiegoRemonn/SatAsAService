from auth import authenticate_earth_engine
from processing import process_image_collection, get_era5_collection
from visualization import create_map, save_map, open_map
from point_extraction import extract_point_values, extract_region_values
from config import ZARAGOZA_COORDS, AOI, VIS_PARAMS, LOCATIONS, INDICES, ERA5_BANDS, SENTINEL_START_DATE, ERA5_START_DATE
from time_series_extraction import get_weekly_image_collection, extract_time_series, save_to_csv
from plot_time_series import plot_indices_per_point, plot_points_per_index
import ee

def main():
    """
    Main function to execute the workflow: authenticate Google Earth Engine, process Satellite data,
    create the map, save it as an HTML file, and open it.
    :return: None
    """
    print("🚀 Starting process...")

    # Authenticate Google Earth Engine
    authenticate_earth_engine()

    print("✅ Earth Engine authenticated.")

    # Process Satellite image collection
    print("📡 Processing Sentinel-2 and ERA5-Land data...")
    collection = process_image_collection(AOI)
    era5_coll = get_era5_collection(AOI, start_date='2024-12-01', end_date='2024-12-31')
    image_collection = get_weekly_image_collection(AOI, start_date=SENTINEL_START_DATE)

    era5_collection = get_era5_collection(AOI, start_date=ERA5_START_DATE)

    print("📊 Extracting time-series data...")

    # Extract Sentinel-2 time-series data for selected locations
    sentinel_data = extract_time_series(image_collection, LOCATIONS, INDICES, scale=10, start_date=SENTINEL_START_DATE,
                                        dataset_name="Sentinel-2", time_interval=14)

    # Save the extracted data to a CSV file
    save_to_csv(sentinel_data, "sentinel_time_series.csv")

    # Extract ERA5 time-series data for selected locations
    era5_data = extract_time_series(era5_collection, LOCATIONS, ERA5_BANDS, scale=11132, start_date=ERA5_START_DATE,
                                    dataset_name="ERA5-Land", time_interval=14)
    save_to_csv(era5_data, "era5_time_series.csv")

    print("📈 Generating time-series plots...")

    # Generate visualizations
    print("\nGenerating time-series plots...")
    plot_indices_per_point("sentinel_time_series.csv") # View all indices in each point
    # plot_points_per_index("sentinel_time_series.csv")  # Uncomment to view each index across all points
    plot_indices_per_point("era5_time_series.csv")

    print("🗺️ Creating and saving the map...")

    # Create the map
    m = create_map(ZARAGOZA_COORDS, collection, era5_coll, VIS_PARAMS)
    html_filename = "map.html" # Default name

    # Save the map as an HTML file
    html_file = save_map(m, html_filename)

    # Open the map in the browser
    open_map(html_file)

    print(f"🌍 Map saved as {html_filename}")
    print("\n🔍 Extracting values at specific locations...")

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

    print("\n🎯 Process completed successfully! 🚀")

if __name__ == '__main__':
    main()