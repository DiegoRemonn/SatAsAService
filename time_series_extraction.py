import ee
import csv
import sys
import datetime
from processing import calculate_indices, mask_s2_clouds

# Define the start date (when Sentinel-2 data is available)
START_DATE = "2015-06-23"
END_DATE = datetime.datetime.today().strftime("%Y-%m-%d") # Current date
TIME_INTERVAL = 7 # Days (weekly data)

def get_weekly_image_collection(aoi, start_date=START_DATE, end_date=END_DATE):
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

def extract_time_series(image_collection, locations, indices, time_interval=TIME_INTERVAL):
    """
    Extracts time-series data from Sentinel-2 images for the selected locations.
    The function retrieves weekly aggregated values (median) for each index at each point.

    :param image_collection: ee.ImageCollection
        Processed Sentinel-2 image collection containing calculated indices.
    :param locations: list of tuples
        List of geographic coordinates (latitude, longitude) for the points of interest.
    :param indices: list of str
        List of indices to extract (e.g., "NDVI", "NDMI", "NDWI", "NDSI").
    :param time_interval: int
        Time interval in days (default: 7 for weekly aggregation).
    :return: list of dicts
        A list of dictionaries, each containing the date, coordinates, and extracted index values.
    """
    results = []
    start = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")

    total_intervals = (end - start).days // time_interval + 1  # Total number of iterations
    processed_intervals = 0  # Counter for processed intervals

    while start <= end:
        # Convert current date to string format
        date_str = start.strftime("%Y-%m-%d")

        # Filter the image collection for the current week
        filtered = image_collection.filterDate(
            date_str,
            (start + datetime.timedelta(days=time_interval)).strftime("%Y-%m-%d")
        )
        image = filtered.median() # Aggregate data using median for the given week

        if image:
            for lat, lon in locations:
                point = ee.Geometry.Point([lon, lat])
                values = image.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=point,
                    scale=10, # Sentinel-2 pixel resolution (10m)
                    maxPixels=1e6
                ).getInfo()

                # Store extracted values if available
                if values:
                    row = {
                        "Date": date_str,
                        "Latitude": lat,
                        "Longitude": lon
                    }
                    for index in indices:
                        row[index] = values.get(index, None) # Retrieve values for each index
                    results.append(row)

        # Update progress
        processed_intervals += 1
        progress = (processed_intervals / total_intervals) * 100
        sys.stdout.write(f"\rProcessing time-series: {progress:.2f}% complete")
        sys.stdout.flush()

        # Move to the next time interval
        start += datetime.timedelta(days=time_interval)

    print("\nTime-series extraction completed.")  # New line after completion
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