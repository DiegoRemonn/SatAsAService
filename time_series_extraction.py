import ee
import csv
import sys
import datetime
import time
import threading
from processing import calculate_indices, mask_s2_clouds
from point_extraction import extract_point_values, extract_region_values
from config import END_DATE

TIME_INTERVAL = 7 # Days (weekly data)

def get_weekly_image_collection(aoi, start_date, end_date=END_DATE):
    """
    Retrieves a Sentinel-2 image collection filtered by the given Area of Interest (AOI)
    and time range. The collection is pre-processed to calculate vegetation and water indices.

    :param aoi: ee.Geometry
        The Area of Interest (AOI) to filter the satellite image collection.
    :param start_date: str
        Start date in "YYYY-MM-DD" format (default: first available Sentinel-2 data in 2015).
    :param end_date: str
        End date in "YYYY-MM-DD" format (default: today's date).
    :return: ee.ImageCollection
        A collection of Sentinel-2 images with additional calculated indices (NDVI, NDMI, NDWI, NDSI).
    """
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.bounds(aoi)) \
        .map(mask_s2_clouds) \
        .map(calculate_indices) # Add calculated indices

    # Select only essential bands (remove problem bands)
    selected_bands = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9",
                      "B11", "B12", "NDVI", "NDMI", "NDWI", "NDSI"]

    return collection.select(selected_bands)  # Ensure all images have only these bands

def extract_time_series(image_collection, locations, bands, scale, start_date, dataset_name, time_interval=TIME_INTERVAL):
    """
    Extracts time-series data from Sentinel-2 or ERA5-Land for the selected locations.
    The function retrieves weekly aggregated values (median for Sentinel, mean for ERA5) for each band.

    :param image_collection: ee.ImageCollection
        The satellite image collection to process.
    :param locations: list of tuples
        List of geographic coordinates (latitude, longitude) for the points of interest.
    :param bands: list of str
        List of bands/variables to extract.
    :param scale: int
        Spatial resolution for data extraction (e.g., 10m for Sentinel-2, 9000m for ERA5-Land).
    :param start_date: str
        Start date for extracting time series.
    :param dataset_name: str
        Name of the dataset (e.g., "Sentinel-2", "ERA5-Land") for progress display.
    :param time_interval: int, optional
        Time interval in days (default: 7 for weekly aggregation).
    :return: list of dicts
        A list of dictionaries containing date, coordinates, and extracted index values.
    """
    results = []
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")

    total_intervals = (end - start).days // time_interval + 1  # Total number of iterations
    processed_intervals = 0  # Counter for processed intervals

    start_time = time.time()  # Start the timer
    elapsed_time = 0  # Store elapsed time
    stop_timer = False  # Control variable for stopping the timer
    num_images = 0
    progress = 0

    # Function to update the elapsed time in a separate thread
    def update_timer():
        nonlocal elapsed_time
        while not stop_timer:
            elapsed_time = time.time() - start_time
            elapsed_time_str = str(datetime.timedelta(seconds=int(elapsed_time)))
            sys.stdout.write(f"\r[{dataset_name}] Processing time-series: {progress:.2f}% complete | "
                             f"Number of images for this week: {num_images} | Time elapsed: {elapsed_time_str}")
            sys.stdout.flush()
            time.sleep(1)  # Wait for 1 second before updating again

    # Start the timer thread
    timer_thread = threading.Thread(target=update_timer)
    timer_thread.start()

    while start <= end:
        # Convert current date to string format
        date_str = start.strftime("%Y-%m-%d")

        # Filter the image collection for the current week
        filtered = image_collection.filterDate(
            date_str,
            (start + datetime.timedelta(days=time_interval)).strftime("%Y-%m-%d")
        )
        image = filtered.median() if dataset_name == "Sentinel-2" else filtered.mean()  # Sentinel-2 uses median, ERA5 uses mean

        num_images = filtered.size().getInfo()  # Get number of images in the filtered collection

        if image:
            for lat, lon in locations:
                point = ee.Geometry.Point([lon, lat])
                values = extract_point_values(image, point, scale=scale)
                region_values = extract_region_values(image, point, scale=10)

                # Store extracted values if available
                if values:
                    row = {
                        "Date": date_str,
                        "Latitude": lat,
                        "Longitude": lon
                    }
                    for band in bands:
                        row[band] = values.get(band, None) # Retrieve values for each index
                        if dataset_name == "Sentinel-2":
                            row[f"{band}_region"] = region_values.get(band, None) if region_values else None # Retrieve 100x100m region values
                    results.append(row)

        # Update progress
        processed_intervals += 1
        progress = (processed_intervals / total_intervals) * 100

        # Move to the next time interval
        start += datetime.timedelta(days=time_interval)

    stop_timer = True  # Stop the timer thread
    timer_thread.join()  # Wait for the timer thread to finish

    total_time = time.time() - start_time  # Final elapsed time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))

    print(f"\n[{dataset_name}] Time-series extraction completed in {total_time_str}.")  # New line after completion
    return results

def save_to_csv(data, filename="time_series.csv"):
    """
    Saves the extracted time-series data into a CSV file.

    :param data: list of dicts
        The extracted data containing time-series index values.
    :param filename: str
        The name of the output CSV file (default: "time_series.csv").
    :return: None
    """
    if not data:
        print("No data available to save.")
        return

    total_rows = len(data) # Total number of rows to save
    keys = data[0].keys()
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()

        # Iterate over data and track progress
        for i, row in enumerate(data, start=1):
            writer.writerow(row)

            # Calculate and print progress
            progress = (i / total_rows) * 100
            sys.stdout.write(f"\rSaving CSV: {progress:.2f}% complete")  # Overwrite same line
            sys.stdout.flush()

    print("Data saved to {filename}.")