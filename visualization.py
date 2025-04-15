from config import LOCATIONS, ERA5_BANDS
import geemap as ui
import webbrowser
import os
import ee

def add_rectangles_to_map(m, locations):
    """
    Adds 100x100 meter rectangles around each specified location on the map.

    Args:
        m (geemap.Map): The map object where the rectangles will be added.
        locations (list of tuple): A list of geographic points (latitude, longitude) for which to draw rectangles.

    Returns:
        None
    """
    for lat, lon in locations:
        region = ee.Geometry.Rectangle([
            lon - 0.00045, lat - 0.00045, lon + 0.00045, lat + 0.00045
        ])
        m.addLayer(region, {'color': 'blue'}, f"100x100m Area ({lat}, {lon})")

def create_map(center_coords, sentinel_collection, era5_collection, vis_params):
    """
    Creates an interactive map centered on the given coordinates and adds multiple layers for Sentinel-2 and ERA5 data.

    This function adds various layers (True Color, False Color, NDVI, NDMI, SWIR, NDWI, NDSI, Scene Classification)
    from Sentinel-2 imagery and ERA5-Land soil moisture bands to the map. It also adds markers and rectangles
    corresponding to selected locations.

    Args:
        center_coords (list): A list containing the map's center coordinates [latitude, longitude].
        sentinel_collection (ee.Image): Cloud-masked Sentinel-2 composite image.
        era5_collection (ee.Image): Processed ERA5-Land composite image.
        vis_params (dict): Visualization parameters for the Sentinel-2 True Color layer.

    Returns:
        geemap.Map: A map object with all added layers and controls.
    """
    # Create a map object centered at center_coords, with a zoom level of 10 and nearly full height.
    m = ui.Map(center=center_coords, zoom=10, height="98vh") # Create a map object.

    # Add Sentinel-2 True Color layer.
    m.add_ee_layer(sentinel_collection, vis_params, 'Sentinel-2 True Color') # Add the cloud-masked image to the map

    # Add Sentinel-2 False Color visualization.
    falsecolor = {
        'min': 0,
        'max': 5000,
        'bands': ['B8', 'B4', 'B3']
    }
    m.add_ee_layer(sentinel_collection, falsecolor, 'Sentinel-2 False Color')

    # NDVI Visualization using a custom exact palette.
    ndvi_ramp = [
        [-0.5, '#0c0c0c'], [-0.2, '#bfbfbf'], [-0.1, '#dbdbdb'],
        [0.0, '#eaeaea'], [0.025, '#fff9cc'], [0.05, '#ede8b5'],
        [0.075, '#ddd89b'], [0.1, '#ccc682'], [0.125, '#bcb76b'],
        [0.15, '#afc160'], [0.175, '#a3cc59'], [0.2, '#91bf51'],
        [0.25, '#7fb247'], [0.3, '#70a33f'], [0.35, '#609635'],
        [0.4, '#4f892d'], [0.45, '#3f7c23'], [0.5, '#306d1c'],
        [0.55, '#216011'], [0.6, '#0f540a'], [1.0, '#004400']
    ]
    ndvi_breaks, ndvi_palette = zip(*ndvi_ramp)
    ndvi_vis_params = {
        'min': -0.5,
        'max': 0.6,
        'palette': ndvi_palette
    }
    m.add_ee_layer(sentinel_collection.select('NDVI'), ndvi_vis_params, 'Sentinel-2 NDVI')

    # NDMI Visualization using a custom exact palette.
    ndmi_ramp = [
        [-0.8, '#800000'],  # Dark red (low moisture)
        [-0.24, '#ff0000'],  # Bright red (dry area)
        [-0.032, '#ffff00'],  # Yellow (transition moisture)
        [0.032, '#00ffff'],  # Cyan (moderate moisture)
        [0.24, '#0000ff'],  # Bright blue (high moisture)
        [0.8, '#000080']  # Dark blue (maximum moisture)
    ]
    ndmi_breaks, ndmi_palette = zip(*ndmi_ramp)
    ndmi_vis_params = {
        'min': -0.24,
        'max': 0.24,
        'palette': ndmi_palette
    }
    m.add_ee_layer(sentinel_collection.select('NDMI'), ndmi_vis_params, 'Sentinel-2 NDMI')

    # SWIR Visualization
    swir_vis_params = {
        'min': 0,
        'max': 5000,
        'bands': ['B12', 'B8A', 'B4']
    }
    m.add_ee_layer(sentinel_collection, swir_vis_params, 'Sentinel-2 SWIR')

    # NDWI Visualization
    ndwi_vis_params = {
        'min': -1.0,
        'max': 1.0,
        'palette': ['#008000', '#FFFFFF', '#0000CC']
    }
    m.add_ee_layer(sentinel_collection.select('NDWI'), ndwi_vis_params, 'Sentinel-2 NDWI')

    # NDSI Visualization with a snow mask.
    ndsi = sentinel_collection.select('NDSI')
    snow_mask = ndsi.gte(0.4)  # Consider snow when NDSI > 0.4
    ndsi_masked = ndsi.updateMask(snow_mask)
    ndsi_vis_params = {
        'min': 0.0,
        'max': 1.0,
        'palette': ['#0000FF']  # Brilliant blue for snow
    }
    m.add_ee_layer(ndsi_masked, ndsi_vis_params, 'Sentinel-2 NDSI')

    # Sentinel-2 L2A Scene Classification Map
    scl_vis_params = {
        'min': 0,
        'max': 11,
        'palette': ['#000000', '#ff0000', '#2f2f2f', '#643200', '#00a000', '#ffe65a', '#0000ff',
                    '#808080', '#c0c0c0', '#ffffff', '#64c8ff', '#ff96ff']
    }
    m.add_ee_layer(sentinel_collection.select('SCL'), scl_vis_params, 'Sentinel-2 Scene Classification')

    # ERA5-Land Soil Moisture Visualization
    soil_moisture_palette = ['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837']  # Dry to wet color scale

    for i, band in enumerate(ERA5_BANDS):
        era5_vis_params = {
            'min': 0.0,
            'max': 1.0,
            'palette': soil_moisture_palette
        }
        m.add_ee_layer(era5_collection.select(band), era5_vis_params, f"ERA5-Land {band}")

    # Add location markers
    for lat, lon in LOCATIONS:
        point = ee.Geometry.Point([lon, lat])  # Create a point geometry
        feature = ee.Feature(point)  # Convert to an EE Feature
        feature_collection = ee.FeatureCollection([feature])  # Wrap in a FeatureCollection

        # Add the marker to the map
        marker_style = {'color': 'red'}  # Marker style (red points)
        m.addLayer(feature_collection, marker_style, f"Point ({lat}, {lon})")

    # Add 100x100 meter rectangles around the locations.
    add_rectangles_to_map(m, LOCATIONS)

    # Add layer control to toggle layers.
    m.addLayerControl()
    return m

def save_map(m, filename):
    """
    Saves a geemap.Map object as an HTML file.

    Args:
        m (geemap.Map): The map object to be saved.
        filename (str): The desired filename for the HTML file.

    Returns:
        str: The absolute path to the saved HTML file.
    """
    html_file = os.path.abspath(filename)
    m.to_html(html_file, width="100%", height="98vh")
    m.save(html_file)
    print(f"Map saved as '{html_file}'")
    return html_file

def open_map(html_file):
    """
    Opens the specified HTML file in Google Chrome.

    Args:
        html_file (str): The absolute path to the HTML file.

    Returns:
        None
    """
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe" # Root to Google Chrome
    try:
        browser = webbrowser.get(f'"{chrome_path}" %s')
        browser.open(f'file://{html_file}')
    except Exception as e:
        print(f"Error opening the map: {e}")