from auth import authenticate_earth_engine
from processing import process_image_collection, get_era5_collection
from visualization import create_map, save_map, open_map
from point_extraction import extract_point_values, extract_region_values
from config import (ZARAGOZA_COORDS, AOI, GALLOCANTA_AOI, VIS_PARAMS, LOCATIONS,
                    INDICES, ERA5_BANDS, SENTINEL_START_DATE, ERA5_START_DATE)
from time_series_extraction import get_weekly_image_collection, extract_time_series, save_to_csv, get_monthly_composites
from plot_time_series import plot_indices_per_point, plot_points_per_index
from gif_gen import create_gif_from_urls, merge_gifs
import ee

def main_menu():
    """
    Displays the main menu with available options.

    Returns:
        str: The user's selected menu option.
    """
    print("\n--- Main Menu ---")
    print("1. Process satellite data")
    print("2. Extract time-series data")
    print("3. Generate time-series plots")
    print("4. Create interactive map")
    print("5. Generate GIFs")
    print("6. Merge GIFs")
    print("7. Run complete process")
    print("0. Exit")
    return input("Choose an option (0-7): ")

def process_satellite_data():
    """
    Processes the satellite image collections from Sentinel-2 and ERA5-Land.

    Returns:
        tuple: A tuple containing:
            - collection (ee.Image): Processed Sentinel-2 image collection.
            - era5_coll (ee.Image): ERA5-Land collection for a specific period.
            - image_collection (ee.ImageCollection): Weekly filtered Sentinel-2 images.
            - era5_collection (ee.ImageCollection): Sentinel ERA5-Land images starting from a defined date.
    """
    print("📡 Processing Sentinel-2 and ERA5-Land data...")
    collection = process_image_collection(AOI)
    era5_coll = get_era5_collection(AOI, start_date='2024-12-01', end_date='2024-12-31')

    image_collection = get_weekly_image_collection(AOI, start_date=SENTINEL_START_DATE)
    era5_collection = get_era5_collection(AOI, start_date=ERA5_START_DATE)

    return collection, era5_coll, image_collection, era5_collection

def extract_time_series_data(image_collection, era5_collection):
    """
    Extracts time-series data from satellite collections and saves them as CSV files.

    Args:
        image_collection (ee.ImageCollection): Weekly Sentinel-2 image collection.
        era5_collection (ee.ImageCollection): ERA5-Land image collection.
    """
    print("📊 Extracting time-series data...")
    # Extract time-series data for Sentinel-2 using selected locations and indices.
    sentinel_data = extract_time_series(image_collection, LOCATIONS, INDICES, scale=10, start_date=SENTINEL_START_DATE,
                                        dataset_name="Sentinel-2", time_interval=14)
    save_to_csv(sentinel_data, "sentinel_time_series.csv")

    # Extract time-series data for ERA5-Land using selected locations.
    era5_data = extract_time_series(era5_collection, LOCATIONS, ERA5_BANDS, scale=11132, start_date=ERA5_START_DATE,
                                    dataset_name="ERA5-Land", time_interval=14)
    save_to_csv(era5_data, "era5_time_series.csv")

def generate_time_series_plots():
    """
    Generates time-series plots from previously saved CSV files.
    """
    print("\nGenerating time-series plots...")
    plot_indices_per_point("sentinel_time_series.csv")  # View all indices in each point
    # plot_points_per_index("sentinel_time_series.csv")  # Uncomment to view each index across all points
    plot_indices_per_point("era5_time_series.csv")

def create_interactive_map(collection, era5_coll):
    """
    Creates an interactive map using satellite data and displays point extractions.

    Args:
        collection (ee.Image): Processed Sentinel-2 image collection.
        era5_coll (ee.Image): Processed ERA5-Land image collection.
    """
    print("🗺️ Creating and saving the map...")

    # Create the map
    m = create_map(ZARAGOZA_COORDS, collection, era5_coll, VIS_PARAMS)
    html_filename = "map.html"  # Default name

    # Save the map as an HTML file
    html_file = save_map(m, html_filename)

    # Open the map in the browser
    open_map(html_file)

    print(f"🌍 Map saved as {html_filename}")
    print("\n🔍 Extracting values at specific locations...")

    for lat, lon in LOCATIONS:
        point = ee.Geometry.Point([lon, lat])
        values = extract_point_values(collection, point)  # Extract values at the given point

        # Extraer valores de una región de 100x100m
        region_values = extract_region_values(collection, point)

        if values:
            print(f"Values at point ({lat}, {lon}): {values})")
            print(f"Averaged values in 100x100m area ({lat}, {lon}): {region_values}")
        else:
            print(f"Failed to extract values at point ({lat}, {lon}).")

def generate_gifs():
    """
    Generates monthly composites from the Gallocanta AOI and creates GIFs based on NDMI and ERA5 palettes.
    """
    print("🗺️ Getting the monthly composites...")
    composites, composites_era, dates = get_monthly_composites(GALLOCANTA_AOI, start_year=2018, end_year=2024,
                                                               index="NDMI")

    # Define NDMI ramp and visualization parameters.
    ndmi_ramp = [
        (-0.8, '#800000'),  # Dark red for low moisture
        (-0.24, '#ff0000'),  # Bright red for dry areas
        (-0.032, '#ffff00'),  # Yellow for transitional moisture
        (0.032, '#00ffff'),  # Cyan for moderate moisture
        (0.24, '#0000ff'),  # Bright blue for high moisture
        (0.8, '#000080')  # Dark blue for maximum moisture
    ]

    # Convert ramp into separate min/max and palette lists
    ndmi_breaks, ndmi_palette = zip(*ndmi_ramp)
    ndmi_vis_params = {'min': -0.24, 'max': 0.24, 'palette': ndmi_palette}

    print("🗺️ Downloading the monthly composites...")
    urls_sen = [img.getThumbURL({
        'min': ndmi_vis_params['min'],
        'max': ndmi_vis_params['max'],
        'palette': ndmi_vis_params['palette'],
        'region': GALLOCANTA_AOI.getInfo(),
        'dimensions': 512
    }) for img in composites]

    era5_palette = ['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837']
    urls = [img.getThumbURL({
        'min': 0.0,
        'max': 1.0,
        'region': GALLOCANTA_AOI.getInfo(),
        'palette': era5_palette,
        'dimensions': 512
    }) for img in composites_era]

    print("🗺️ Creating gif...")
    create_gif_from_urls(urls_sen, dates, "ndmi", GALLOCANTA_AOI,
                         output_filename='laguna_gallocanta_evolucion_sen.gif', duration=10)
    create_gif_from_urls(urls, dates, "era5", GALLOCANTA_AOI,
                         output_filename='laguna_gallocanta_evolucion_2ms.gif', duration=10)

def merge_gifs_menu():
    """
    Merges two specified GIF files into a single GIF.
    """
    merge_gifs("laguna_gallocanta_evolucion_pe_(1).gif", "laguna_gallocanta_evolucion_pe_(2).gif",
               "gif_unido.gif", duration=10)

def run_all():
    """
    Executes the complete process by running all the defined tasks in sequence.
    """
    print("🚀 Starting complete process...")
    collection, era5_coll, image_collection, era5_collection = process_satellite_data()
    extract_time_series_data(image_collection, era5_collection)
    generate_time_series_plots()
    create_interactive_map(collection, era5_coll)
    generate_gifs()
    merge_gifs_menu()
    print("\n🎯 Process completed successfully! 🚀")

def main():
    """
    Main function to run the workflow. It authenticates with Earth Engine and
    displays a menu for the user to choose which parts of the workflow to run.

    The workflow includes:
     1. Processing satellite data.
     2. Extracting time-series data.
     3. Generating time-series plots.
     4. Creating an interactive map.
     5. Generating GIFs.
     6. Merging GIFs.
     7. Running the complete process.
     0. Exit.
    """
    print("🚀 Starting process...")
    # Authenticate Google Earth Engine
    authenticate_earth_engine()
    print("✅ Earth Engine authenticated.")

    collection, era5_coll, image_collection, era5_collection = None, None, None, None

    data_processed = False
    series_extracted = False

    while True:
        choice = main_menu()
        if choice == "1":
            collection, era5_coll, image_collection, era5_collection = process_satellite_data()
            data_processed = True
            series_extracted = False
        elif choice == "2":
            if not data_processed:
                print("⚠️ Error: You must run option 1 (Process satellite data) first.")
            else:
                extract_time_series_data(image_collection, era5_collection)
                series_extracted = True
        elif choice == "3":
            if not series_extracted:
                print("⚠️ Error: You must run option 2 (Extract time-series data) first.")
            else:
                generate_time_series_plots()
        elif choice == "4":
            if not data_processed:
                print("⚠️ Error: You must run option 1 (Process satellite data) first.")
            else:
                create_interactive_map(collection, era5_coll)
        elif choice == "5":
            generate_gifs()
        elif choice == "6":
            merge_gifs_menu()
        elif choice == "7":
            run_all()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("⚠️ Invalid option. Please choose a number between 0 and 7.")
        print("\n")  # Newline after each menu action

    print("\n🎯 Process completed successfully! 🚀")

if __name__ == '__main__':
    main()