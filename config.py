"""
Configuration module for the Satellite as a Service project.

This module defines global configuration variables such as:
  - Geographic coordinates and Areas of Interest (AOI)
  - Visualization parameters for Sentinel-2 imagery
  - Pre-defined extraction locations and spectral indices
  - Dataset start and end dates

It also performs authentication with Google Earth Engine (EE).
"""

import ee
from auth import authenticate_earth_engine
import datetime

# Authenticate Google Earth Engine (if not already authenticated)
authenticate_earth_engine()

# Coordinates for Zaragoza (used for centering maps, etc.)
ZARAGOZA_COORDS = [41.6488, -0.8891]

# Area of interest (AOI) in Zaragoza
AOI = ee.Geometry.Rectangle([-0.9500, 41.5800, -0.8300, 41.7200])

# Area of interest (AOI) in Gallocanta
# This rectangle is defined to cover a larger area (roughly 110km x 110km) centered around Gallocanta.
GALLOCANTA_AOI = ee.Geometry.Rectangle([-2.156, 40.474, -0.846, 41.464])
# Exact geographic location of Gallocanta (longitude, latitude)
GALLOCANTA_LOCATION = (-1.501846, 40.971332)

# Visualization parameters for Sentinel-2 True Color imagery.
VIS_PARAMS = {
   'bands': ['B4', 'B3', 'B2'],  # RGB bands (Red, Green, Blue)
   'min': 500,                   # Minimum pixel value for visualization. Adjust based on typical values.
   'max': 2500,                  # Maximum pixel value for visualization. Adjust based on histogram analysis.
   'gamma': [1.4]                # Gamma correction factor to enhance visualization.
}

# List of extraction locations (latitude, longitude)
LOCATIONS = [
   (41.685004717223144, -0.8918084795693515),  # Athletics Stadium Corona de Aragon
   (41.684055592659014, -0.9003028409380128),  # Ebro River
   (41.68301523336218, -0.904520776405019),    # Crops in Zaragoza
   (41.65631734842274, -0.8788629375118525),   # Pilar Square
]

# List of spectral indices to extract from Sentinel-2 images.
INDICES = ["NDVI", "NDMI", "NDWI", "NDSI"]

# ERA5-Land bands for soil moisture data extraction.
ERA5_BANDS = ["volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2",
              "volumetric_soil_water_layer_3", "volumetric_soil_water_layer_4"]

# Define start dates for each dataset
SENTINEL_START_DATE = "2017-03-28"  # Sentinel-2 operational start date.
ERA5_START_DATE = "2015-01-01" # ERA5-Land start date (note: ERA5-Land data is available from 1950,
                               # but this date is used as required for the project).

# Define end date as the current date (formatted as YYYY-MM-DD)
END_DATE = datetime.datetime.today().strftime("%Y-%m-%d")