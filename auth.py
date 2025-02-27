import ee

# Name of the Google Earth Engine Project name (Put your own project name)
USER_PROJECT = ""

def authenticate_earth_engine():
    """
    Authenticates and initializes Google Earth Engine service.
    :return: None
    """
    try:
        ee.Authenticate()
        ee.Initialize(project=USER_PROJECT)
    except Exception as e:
        print("Authenticating Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=USER_PROJECT)