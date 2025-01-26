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
            print(f"Point {point.getInfo()} is outside the image bounds.")
            return None

        # Reduce the image at the given point to extract band values
        values = image.reduceRegion(
            reducer=ee.Reducer.first(), # Extract the first value for each band
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