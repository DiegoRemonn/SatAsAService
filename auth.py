import ee
import time

# Name of the Google Earth Engine project. Replace with your project name if needed.
USER_PROJECT = "ee-dremon"

def authenticate_earth_engine():
    """
    Authenticates and initializes the Google Earth Engine service.

    This function calls ee.Authenticate() followed by ee.Initialize() using the specified project name.
    If an exception occurs during the process, it retries the authentication procedure.

    Returns:
        None
    """
    try:
        ee.Authenticate()
        ee.Initialize(project=USER_PROJECT)
    except Exception as e:
        print(f"Error authenticating with Google Earth Engine: {e}")
        print("Authenticating Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=USER_PROJECT)

def reconnect_gee(project_name=USER_PROJECT, max_retries=5, delay=5):
    """
    Attempts to re-authenticate and re-initialize the connection to Google Earth Engine.

    This function is useful when the connection has been lost or the token has expired.
    It will try to reconnect up to 'max_retries' times, waiting 'delay' seconds between each attempt.

    Args:
        project_name (str): The name of the Google Earth Engine project.
        max_retries (int): Maximum number of reconnection attempts.
        delay (int): Number of seconds to wait between attempts.

    Returns:
        bool: True if the connection was successfully re-established, False otherwise.
    """
    for i in range(max_retries):
        try:
            ee.Authenticate()
            ee.Initialize(project=project_name)
            print("Connection to EE re-established.")
            return True
        except Exception as e:
            print(f"Error reconnecting to EE: {e} (Attempt {i+1}/{max_retries}).")
            time.sleep(delay)
    return False