import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementNotInteractableException,
)
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker
import random
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Función para iniciar un nuevo navegador
def init_driver():
    # Configurar opciones de Chrome para simular Japón
    chrome_options = Options()
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')  # Mínimo nivel de log
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Desactiva las características de automatización
    #chrome_options.add_argument('--headless')  # Para que no se abra la ventana del navegador (opcional)

    # Crear un servicio usando ChromeDriverManager
    service = Service(ChromeDriverManager().install())

    # Configura el controlador para Chrome utilizando el servicio
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Inicializar Faker
fake = Faker('ja_JP')  # Generar datos específicos para Japón

# Ruta del archivo para guardar el contador
counter_file_path = 'counter.txt'

# Función para leer el contador desde el archivo
def get_counter():
    if os.path.exists(counter_file_path):
        try:
            with open(counter_file_path, 'r') as file:
                return int(file.read().strip())
        except (ValueError, IOError) as e:
            logger.error(f"Error leyendo contador, reiniciando a 1: {e}")
            return 1
    else:
        return 1  # Si no existe el archivo, empezar desde 1

# Función para guardar el contador en el archivo
def save_counter(counter):
    try:
        with open(counter_file_path, 'w') as file:
            file.write(str(counter))
    except IOError as e:
        logger.error(f"Error guardando contador: {e}")

# Función para simular la escritura lenta
def simulate_typing(element, text):
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.1, 0.3))  # Tiempo aleatorio entre cada tecla

# Obtener el contador desde el archivo (o empezar en 1)
counter = get_counter()

while True:
    driver = None
    success = False

    try:
        # Iniciar el navegador
        driver = init_driver()
        wait = WebDriverWait(driver, 10)

        # --- Paso 1: Cargar página ---
        driver.get("https://verlosung.wienerphilharmoniker.at/en/form")

        # --- Paso 2: Aceptar cookies ---
        try:
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'accept-cookie-settings')))
            accept_cookies_button.click()
            time.sleep(3)
        except TimeoutException:
            logger.warning("Botón de cookies no encontrado, puede que ya estén aceptadas")

        # --- Paso 3: Selección de concierto ---
        radio_button = driver.find_element(By.ID, 'id_konzert_2')
        actions = ActionChains(driver)
        actions.move_to_element(radio_button).perform()
        wait.until(EC.element_to_be_clickable((By.ID, 'id_konzert_2')))
        driver.execute_script("arguments[0].click();", radio_button)
        time.sleep(13)

        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to number of tickets and seat selection')]")))
        continue_button.click()
        time.sleep(13)

        # --- Paso 4: Selección de asientos ---
        wait.until(EC.presence_of_element_located((By.ID, 'id_anzahl')))
        seat_select = Select(driver.find_element(By.ID, 'id_anzahl'))
        seat_select.select_by_value('2')

        kategorie_radio_button = driver.find_element(By.ID, 'id_kategorie_0')
        actions = ActionChains(driver)
        actions.move_to_element(kategorie_radio_button).perform()
        wait.until(EC.element_to_be_clickable((By.ID, 'id_kategorie_0')))
        driver.execute_script("arguments[0].click();", kategorie_radio_button)

        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to personal data')]")))
        continue_button.click()
        time.sleep(13)

        # --- Paso 5: Formulario personal ---
        wait.until(EC.presence_of_element_located((By.ID, 'id_anrede')))

        salutation_select = Select(driver.find_element(By.ID, 'id_anrede'))
        salutation_select.select_by_value('Mr.')

        # driver.find_element(By.ID, 'id_titel').send_keys('Dr.')
        simulate_typing(driver.find_element(By.ID, 'id_vorname'), fake.first_name_male())
        simulate_typing(driver.find_element(By.ID, 'id_nachname'), fake.last_name())
        simulate_typing(driver.find_element(By.ID, 'id_adresse'), fake.address())
        simulate_typing(driver.find_element(By.ID, 'id_plz'), fake.zipcode())
        simulate_typing(driver.find_element(By.ID, 'id_ort'), fake.city())

        country_select = Select(driver.find_element(By.ID, 'id_country'))
        country_select.select_by_value('118')

        email = f'espinardonacionusa+{counter}@gmail.com'
        driver.find_element(By.ID, 'id_email').send_keys(email)
        driver.find_element(By.ID, 'id_email_confirm').send_keys(email)

        if driver.find_element(By.ID, 'id_newsletter').is_selected():
            driver.find_element(By.ID, 'id_newsletter').click()

        # --- Paso 6: Envío del formulario ---
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        time.sleep(15)

        # Guardar contador antes de la confirmación final
        counter += 1
        save_counter(counter)

        # --- Paso 7: Confirmación final ---
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Take part in the drawing now')]")))
        submit_button.click()
        time.sleep(25)

        # --- Éxito ---
        success = True
        logger.info(f"Iteración {counter} completada con email: espinardonacionusa+{counter - 1}@gmail.com")

    except TimeoutException as e:
        logger.error(f"Timeout esperando elemento: {e}")
    except NoSuchElementException as e:
        logger.error(f"Elemento no encontrado: {e}")
    except ElementNotInteractableException as e:
        logger.error(f"Elemento no interactuable: {e}")
    except WebDriverException as e:
        logger.error(f"Error del WebDriver: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                logger.warning("No se pudo cerrar el navegador correctamente")

    # Espera entre iteraciones (siempre se ejecuta)
    random_interval = random.randint(15, 18) * 60
    if success:
        logger.info(f"Esperando {random_interval / 60:.0f} minutos antes de la siguiente ejecución...")
    else:
        logger.info(f"Iteración fallida. Reintentando en {random_interval / 60:.0f} minutos...")
    time.sleep(random_interval)