import ee
import geemap as ui
import webbrowser
import matplotlib.pyplot as plt

# Authenticate and Initialize Earth Engine
try:
    ee.Initialize(project="ee-dremon")
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project="ee-dremon")

def mask_s2_clouds(image):
    """Masks clouds and cirrus from Sentinel-2 images using the QA60 band."""
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

# Zaragoza coordinates
zaragoza_coords = [41.6488, -0.8891]

# Create a map object.
m = ui.Map(center=[20, 0], zoom=10)

# Add Layer control for interactive layer management
m.addLayerControl()

# Define Zaragoza area of interest
aoi = ee.Geometry.Rectangle([-0.9500, 41.5800, -0.8300, 41.7200])

# Load Sentinel-2 image collection
collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
   .filterDate('2021-01-01', '2021-12-31') \
   .filter(ee.Filter.bounds(aoi)) \
   .map(mask_s2_clouds) \
   .median()

# Visualization parameters
vis_params = {
   'bands': ['B4', 'B3', 'B2'],  # RGB bands
   'min': 500,  # Adjust based on typical pixel values
   'max': 2500,  # Adjust based on histogram analysis of the dataset
   'gamma': [1.4]  # Enhance visualization
}

# Add the cloud-masked image to the map
m.add_ee_layer(collection, vis_params, 'Sentinel-2 Zaragoza')

try:
    # Save the map to an HTML file
    m.save('zaragoza_map.html')
    print("Map saved as 'zaragoza_map.html'")
    # Open the map in the default web browser
    webbrowser.open('zaragoza_map.html')
except Exception as e:
    print(f"Error saving or opening the map: {e}")