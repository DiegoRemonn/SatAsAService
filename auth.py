import ee

def authenticate_earth_engine():
    """
    Authenticates and initializes Google Earth Engine service.
    :return: None
    """
    try:
        ee.Authenticate()
        ee.Initialize(project="ee-dremon")
    except Exception as e:
        print("Authenticating Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project="ee-dremon")