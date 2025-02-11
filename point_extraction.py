import ee

def extract_point_values(image, point, scale=10):
    """
    Extract the values of bands or computed indices (e.g., NDVI) at specific point.
    :param image: ee.Image
        The image or mosaic from which to extract the values.
    :param point: ee.Geometry.Point
        The geographic point where values are extracted.
    :param scale: int
        The spatial resolution (in meters) at which to extract the values (default: 10 for Sentinel-2).
    :return: dict
        A dictionary of band values at the specified point.
    """
    try:
        # Ensure the point is within the image bounds
        region = image.geometry()
        if not region.contains(point, 1).getInfo():
            #print(f"Point {point.getInfo()} is outside the image bounds.")
            return None

        # Reduce the image at the given point to extract band values
        values = image.reduceRegion(
            reducer=ee.Reducer.mean(), # Extract the first value for each band
            geometry=point, # The point where values are extracted
            scale=scale, # Resolution to use for extraction
            maxPixels=1e6
        ).getInfo() # Get the results as a Python dictionary

        # Check if the values are valid (not None)
        if values:
            return values
        else:
            print("No data available at the specified point.")
            return None
    except Exception as e:
        print(f"Error extracting point values: {e}")
        return None

def extract_region_values(image, center_point, scale=10):
    """
    Extract values from a 100x100 meter area centered around a point.

    :param image: ee.Image
        The image or mosaic from which to extract the values.
    :param center_point: ee.Geometry.Point
        The geographic center point of the region.
    :param scale: int
        The spatial resolution (in meters) at which to extract the values (default: 10 for Sentinel-2).
    :return: dict
        A dictionary of band values averaged over the region.
    """
    try:
        lon, lat = center_point.getInfo()['coordinates']
        region = ee.Geometry.Rectangle([
            lon - 0.00045, lat - 0.00045, lon + 0.00045, lat + 0.00045
        ])

        values = image.reduceRegion(
            reducer=ee.Reducer.mean(),  # Promedio de valores dentro del área
            geometry=region,
            scale=scale,
            maxPixels=1e6
        ).getInfo()

        return values if values else None
    except Exception as e:
        print(f"Error extracting region values: {e}")
        return None