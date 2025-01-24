import ee
from auth import authenticate_earth_engine

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