from config import LOCATIONS, ERA5_BANDS
import geemap as ui
import webbrowser
import os
import ee

def add_rectangles_to_map(m, locations):
    """
    Adds 100x100 meter rectangles around selected points.

    :param m: geemap.Map
        The map object where the rectangles will be added.
    :param locations: list of tuples
        A list containing (latitude, longitude) of the points.
    """
    for lat, lon in locations:
        region = ee.Geometry.Rectangle([
            lon - 0.00045, lat - 0.00045, lon + 0.00045, lat + 0.00045
        ])
        m.addLayer(region, {'color': 'blue'}, f"100x100m Area ({lat}, {lon})")

def create_map(center_coords, sentinel_collection, era5_collection, vis_params):
    """
    Creates a map centered on the given coordinates and adds layers for Sentinel-2 and ERA5.

    :param center_coords: list
        Coordinates [latitude, longitude] for the map center.
    :param sentinel_collection: ee.Image
        Processed Sentinel-2 image collection.
    :param era5_collection: ee.Image
        Processed ERA5-Land image collection.
    :param vis_params: dict
        Visualization parameters for Sentinel-2.
    :return: geemap.Map
        Object with the added Sentinel-2 and ERA5 layers.
    """
    m = ui.Map(center=center_coords, zoom=10, height="98vh") # Create a map object.

    # Add Sentinel-2 layers
    m.add_ee_layer(sentinel_collection, vis_params, 'Sentinel-2 True Color') # Add the cloud-masked image to the map

    # False color Visualization
    falsecolor = {
        'min': 0,
        'max': 5000,
        'bands': ['B8', 'B4', 'B3']
    }
    m.add_ee_layer(sentinel_collection, falsecolor, 'Sentinel-2 False Color')

    # NDVI Visualization (Sentinel Hub Exact Palette with Defined Ranges)
    ndvi_ramp = [
        [-0.5, '#0c0c0c'], [-0.2, '#bfbfbf'], [-0.1, '#dbdbdb'],
        [0.0, '#eaeaea'], [0.025, '#fff9cc'], [0.05, '#ede8b5'],
        [0.075, '#ddd89b'], [0.1, '#ccc682'], [0.125, '#bcb76b'],
        [0.15, '#afc160'], [0.175, '#a3cc59'], [0.2, '#91bf51'],
        [0.25, '#7fb247'], [0.3, '#70a33f'], [0.35, '#609635'],
        [0.4, '#4f892d'], [0.45, '#3f7c23'], [0.5, '#306d1c'],
        [0.55, '#216011'], [0.6, '#0f540a'], [1.0, '#004400']
    ]

    # Convert the ramp into separate min/max and palette lists
    ndvi_breaks, ndvi_palette = zip(*ndvi_ramp)

    ndvi_vis_params = {
        'min': -0.5,
        'max': 0.6,
        'palette': ndvi_palette
    }

    m.add_ee_layer(sentinel_collection.select('NDVI'), ndvi_vis_params, 'Sentinel-2 NDVI')

    # NDMI Visualization (Sentinel Hub Exact Palette with Defined Ranges)
    ndmi_ramp = [
        [-0.8, '#800000'],  # Rojo oscuro (baja humedad)
        [-0.24, '#ff0000'],  # Rojo brillante (zona seca)
        [-0.032, '#ffff00'],  # Amarillo (transición a humedad)
        [0.032, '#00ffff'],  # Cian (humedad moderada)
        [0.24, '#0000ff'],  # Azul brillante (humedad alta)
        [0.8, '#000080']  # Azul oscuro (máxima humedad)
    ]

    # Convert ramp into separate min/max and palette lists
    ndmi_breaks, ndmi_palette = zip(*ndmi_ramp)

    ndmi_vis_params = {
        'min': -0.24,
        'max': 0.24,
        'palette': ndmi_palette
    }

    # Apply the NDMI visualization layer
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

    # NDSI Visualization
    ndsi = sentinel_collection.select('NDSI')

    # Crear máscara para que solo se muestre nieve y el resto sea transparente
    snow_mask = ndsi.gte(0.4)  # Se considera nieve cuando NDSI > 0.4

    # Aplicar la máscara de nieve sobre el índice NDSI
    ndsi_masked = ndsi.updateMask(snow_mask)

    # Parámetros de visualización: Nieve en Azul brillante
    ndsi_vis_params = {
        'min': 0.0,
        'max': 1.0,
        'palette': ['#0000FF']  # Azul brillante para la nieve
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

    # Add rectangles of 100x100m
    add_rectangles_to_map(m, LOCATIONS)

    m.addLayerControl() # Add Layer control for interactive layer management
    return m

def save_map(m, filename):
    """
    Saves the map to an HTML file.
    :param m: geemap.Map
        Object to be saved.
    :param filename: str
        Name of the HTML file where the map will be saved.
    :return: str
        Absolute path to the saved HTML file.
    """
    html_file = os.path.abspath(filename)
    m.to_html(html_file, width="100%", height="98vh")  # Ajusta el tamaño al 100%
    m.save(html_file)
    print(f"Map saved as '{html_file}'")
    return html_file

def open_map(html_file):
    """
    Opens the HTML file in Google Chrome.
    :param html_file: str
        Absolute path to the HTML file to be opened.
    :return: None
    """
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe" # Root to Google Chrome
    try:
        browser = webbrowser.get(f'"{chrome_path}" %s')
        browser.open(f'file://{html_file}')
    except Exception as e:
        print(f"Error opening the map: {e}")