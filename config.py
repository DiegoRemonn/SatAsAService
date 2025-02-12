import ee
from auth import authenticate_earth_engine
import datetime

# Authenticate Google Earth Engine (in case it is not authenticated previously)
authenticate_earth_engine()

# Zaragoza coordinates
ZARAGOZA_COORDS = [41.6488, -0.8891]

# Area of interest (AOI) in Zaragoza
AOI = ee.Geometry.Rectangle([-0.9500, 41.5800, -0.8300, 41.7200])

# Visualization parameters
VIS_PARAMS = {
   'bands': ['B4', 'B3', 'B2'],  # RGB bands
   'min': 500,  # Adjust based on typical pixel values
   'max': 2500,  # Adjust based on histogram analysis of the dataset
   'gamma': [1.4]  # Enhance visualization
}

LOCATIONS = [
   (41.685004717223144, -0.8918084795693515),  # Athletics Stadium Corona de Aragon
   (41.684055592659014, -0.9003028409380128),  # Ebro River
   (41.68301523336218, -0.904520776405019),    # Crops in Zaragoza
   (41.65631734842274, -0.8788629375118525),   # Pilar Square
]

# List of indices to extract
INDICES = ["NDVI", "NDMI", "NDWI", "NDSI"]
ERA5_BANDS = ["volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2",
              "volumetric_soil_water_layer_3", "volumetric_soil_water_layer_4"]

# Define start dates for each dataset
SENTINEL_START_DATE = "2017-03-28"  # Sentinel-2 starts in 2017
ERA5_START_DATE = "2000-01-01"  # ECMWF ERA5-Land starts in 1950 1950-01-01"

# Define end date (current date)
END_DATE = datetime.datetime.today().strftime("%Y-%m-%d")