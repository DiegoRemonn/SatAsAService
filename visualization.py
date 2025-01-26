import geemap as ui
import webbrowser
import os

def create_map(center_coords, collection, vis_params):
    """
    Creates a map centered on the given coordinates and adds a layer with the processed image collection.
    :param center_coords: list
        Coordinates [latitude, longitude] for the map center.
    :param collection: ee.Image
        Processed Sentinel-2 image collection.
    :param vis_params: dict
        Visualization parameters for the layer.
    :return: geemap.Map
        Object with the added Sentinel-2 layer.
    """
    m = ui.Map(center=center_coords, zoom=10) # Create a map object.
    m.add_ee_layer(collection, vis_params, 'Sentinel-2 True Color') # Add the cloud-masked image to the map

    ndvi_vis_params = {
        'min': -1.0, # Minimum NDVI value
        'max': 1.0, # Maximum NDVI value
        'palette': ['black', 'gray', 'beige', 'lightgreen', 'green', 'darkgreen'] # Colors for NDVI visualization
    }
    m.add_ee_layer(collection.select('NDVI'), ndvi_vis_params, 'Sentinel-2 NDVI')

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