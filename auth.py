import ee
import time

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

def reconnect_gee(project_name=USER_PROJECT, max_retries=5, delay=5):
    """
    Intenta re-autenticar y re-inicializar la conexión con EE.
    :param project_name: Nombre del proyecto EE.
    :param max_retries: Número máximo de intentos.
    :param delay: Tiempo en segundos de espera entre intentos.
    :return: True si se restableció la conexión, False en caso contrario.
    """
    for i in range(max_retries):
        try:
            ee.Authenticate()
            ee.Initialize(project=project_name)
            print("Conexión a EE restablecida.")
            return True
        except Exception as e:
            print(f"Error al reconectar a EE: {e} (Intento {i+1}/{max_retries}).")
            time.sleep(delay)
    return False