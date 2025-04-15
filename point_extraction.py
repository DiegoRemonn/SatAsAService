import ee

def extract_point_values(image, point, scale=10):
    """
    Extracts the values of bands or computed indices (e.g., NDVI) at a specified point.

    This function verifies that the given point is within the image bounds and then computes
    the mean value of each band at that point using reduceRegion.

    Args:
        image (ee.Image): The image or mosaic from which to extract the values.
        point (ee.Geometry.Point): The geographic point where values are extracted.
        scale (int, optional): The spatial resolution (in meters) to use for extraction.
                               (Default: 10 for Sentinel-2.)

    Returns:
        dict: A dictionary of band values at the specified point, or None if no data is available
              or the point is out of bounds.
    """
    try:
        # Ensure the point is within the image bounds
        region = image.geometry()
        if not region.contains(point, 1).getInfo():
            print(f"Point {point.getInfo()} is outside the image bounds.")
            return None

        # Reduce the image at the specified point to extract band values.
        values = image.reduceRegion(
            reducer=ee.Reducer.mean(),  # Use the mean reducer for extraction.
            geometry=point,             # The point where values are extracted.
            scale=scale,                # Spatial resolution in meters.
            maxPixels=1e6
        ).getInfo() # Convert the result to a Python dictionary.

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
    Extracts the average band values from a 100x100 meter area centered around a point.

    The function creates a small rectangular region around the center point and reduces the image
    over that area to compute average band values.

    Args:
        image (ee.Image): The image or mosaic from which to extract the values.
        center_point (ee.Geometry.Point): The geographic center point of the region.
        scale (int, optional): The spatial resolution (in meters) to use for extraction.
                               (Default: 10 for Sentinel-2.)

    Returns:
        dict: A dictionary of band values averaged over the defined region, or None if data is unavailable.
    """
    try:
        lon, lat = center_point.getInfo()['coordinates']
        # Define a 100x100 meter region around the point.
        region = ee.Geometry.Rectangle([
            lon - 0.00045, lat - 0.00045, lon + 0.00045, lat + 0.00045
        ])

        values = image.reduceRegion(
            reducer=ee.Reducer.mean(),  # Average values within the region.
            geometry=region,
            scale=scale,
            maxPixels=1e6
        ).getInfo()

        return values if values else None
    except Exception as e:
        print(f"Error extracting region values: {e}")
        return None