import ee
from config import END_DATE, ERA5_BANDS

def mask_s2_clouds(image):
    """
    Masks clouds and cirrus from Sentinel-2 images using the QA60 band.
    :param image: ee.Image
        Sentinel-2 image to be processed.
    :return: ee.Image
        Map with clouds and cirrus masked out.
    """
    try:
        # Select the QA60 band (cloud mask)
        qa = image.select('QA60')

        # Define cloud and cirrus bit masks
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        # Create a mask where both cloud and cirrus bits are zero
        mask = (qa.bitwiseAnd(cloud_bit_mask).eq(0)) \
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

        # Apply the mask to the original image
        return image.updateMask(mask)
    except Exception as e:
        print(f"Error applying cloud mask: {e}")
        return image

def calculate_indices(image):
    """
    Calculates NDVI, NDMI, SWIR, NDWI, and NDSI for a given image.
    :param image: ee.Image
        Sentinel-2 image to calculate indices from.
    :return: ee.Image
        Map with an additional index bands.
    """
    # NDVI (Normalized Difference Vegetation Index)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # NDMI (Normalized Difference Moisture Index)
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')

    # NDWI (Normalized Difference Water Index)
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')

    # NDSI (Normalized Difference Snow Index)
    ndsi = image.normalizedDifference(['B3', 'B11']).rename('NDSI')

    return image.addBands([ndvi, ndmi, ndwi, ndsi]) # Add indices as a new bands to the image

def process_image_collection(aoi):
    """
    Processes a Sentinel-2 image collection by applying a cloud mask and combining images into a single mosaic.
    Add NDVI, NDMI, SWIR, NDWI, and NDSI bands.
    :param aoi: ee.Geometry
        Area of interest to filter the image collection.
    :return: ee.Image
        Cloud-masked mosaic of the image collection with additional indices.
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

    :param aoi: ee.Geometry
        The area of interest for soil moisture extraction.
    :param start_date: str
        Start date in "YYYY-MM-DD" format.
    :param end_date: str
        End date in "YYYY-MM-DD" format.
    :return: ee.ImageCollection
        ERA5-Land soil moisture dataset filtered by date and location.
    """
    collection = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY") \
        .filter(ee.Filter.date(start_date, end_date)) \
        .filter(ee.Filter.bounds(aoi)) \
        .select(ERA5_BANDS)

    return collection # Get median value over the period