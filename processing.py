import ee
from config import END_DATE, ERA5_BANDS

def mask_s2_clouds(image):
    """
    Applies a cloud and cirrus mask to a Sentinel-2 image using the QA60 band.

    This function selects the QA60 band (which contains cloud information), defines bit masks for clouds and cirrus,
    and then creates a combined mask that excludes both. The resulting mask is applied to the image.

    Args:
        image (ee.Image): A Sentinel-2 image to process.

    Returns:
        ee.Image: The input image with clouds and cirrus masked out.
    """
    try:
        # Select the QA60 band (used as a cloud mask).
        qa = image.select('QA60')

        # Define bit masks for clouds (bit 10) and cirrus (bit 11).
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        # Create a mask where both cloud and cirrus bits are equal to zero.
        mask = (qa.bitwiseAnd(cloud_bit_mask).eq(0)) \
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

        # Apply the mask to the original image
        return image.updateMask(mask)
    except Exception as e:
        print(f"Error applying cloud mask: {e}")
        return image

def calculate_indices(image):
    """
    Calculates several spectral indices for a given Sentinel-2 image.

    Computes the following indices:
      - NDVI (Normalized Difference Vegetation Index) using bands B8 and B4.
      - NDMI (Normalized Difference Moisture Index) using bands B8 and B11.
      - NDWI (Normalized Difference Water Index) using bands B3 and B8.
      - NDSI (Normalized Difference Snow Index) using bands B3 and B11.

    Args:
        image (ee.Image): A Sentinel-2 image to compute indices from.

    Returns:
        ee.Image: The input image with additional bands for NDVI, NDMI, NDWI, and NDSI.
    """
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    ndsi = image.normalizedDifference(['B3', 'B11']).rename('NDSI')

    return image.addBands([ndvi, ndmi, ndwi, ndsi]) # Add indices as a new bands to the image

def process_image_collection(aoi):
    """
    Processes a Sentinel-2 image collection for a given Area of Interest (AOI).

    The function filters the Sentinel-2 SR Harmonized collection by date and AOI,
    applies the cloud mask and calculates additional spectral indices, and then creates
    a median composite mosaic from the filtered collection.

    Args:
        aoi (ee.Geometry): The area of interest to filter the image collection.

    Returns:
        ee.Image: A cloud-masked median composite image that includes additional bands (NDVI, NDMI, NDWI, NDSI).
    """
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate('2024-12-01', '2024-12-31') \
        .filter(ee.Filter.bounds(aoi)) \
        .map(mask_s2_clouds) \
        .map(calculate_indices)
    return collection.median()

def get_era5_collection(aoi, start_date, end_date=END_DATE):
    """
    Retrieves ECMWF ERA5-Land soil moisture data for the specified AOI and time range.

    The function loads the ERA5-Land hourly dataset, filters it by the provided date range and AOI,
    and selects the specified bands defined in the configuration.

    Args:
        aoi (ee.Geometry): The area of interest for extracting soil moisture data.
        start_date (str): Start date in "YYYY-MM-DD" format.
        end_date (str): End date in "YYYY-MM-DD" format.

    Returns:
        ee.ImageCollection: The ERA5-Land image collection filtered by date and AOI, with the selected bands.
    """
    collection = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY") \
        .filter(ee.Filter.date(start_date, end_date)) \
        .filter(ee.Filter.bounds(aoi)) \
        .select(ERA5_BANDS)

    return collection