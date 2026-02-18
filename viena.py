import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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

# Crear carpeta para screenshots si no existe
SCREENSHOT_DIR = 'screenshots'
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# Función para tomar screenshot cuando hay error
def take_screenshot(driver, step_name):
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{SCREENSHOT_DIR}/{step_name}_{timestamp}.png'
        driver.save_screenshot(filename)
        logger.info(f"Screenshot guardado: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error al guardar screenshot: {e}")
        return None

# Función para iniciar un nuevo navegador
def init_driver():
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    #chrome_options.add_argument('--headless')  # Descomenta para modo headless

    # Crear un servicio usando ChromeDriverManager
    service = Service(ChromeDriverManager().install())

    # Configura el controlador para Chrome utilizando el servicio
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Eliminar la propiedad webdriver para evitar detección
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

# Inicializar Faker
fake = Faker('zh_CN')  # Generar datos específicos para China

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
        logger.info("Iniciando navegador...")
        driver = init_driver()
        wait = WebDriverWait(driver, 15)

        # --- Paso 1: Cargar página ---
        logger.info("Cargando página del formulario...")
        driver.get("https://verlosung.wienerphilharmoniker.at/en/form")
        time.sleep(2)

        # --- Paso 2: Aceptar cookies ---
        logger.info("Intentando aceptar cookies...")
        try:
            accept_cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'accept-cookie-settings')))
            accept_cookies_button.click()
            logger.info("Cookies aceptadas")
            time.sleep(2)
        except TimeoutException:
            logger.info("Botón de cookies no visible, posiblemente ya aceptadas")

        # --- Paso 3: Selección de concierto ---
        logger.info("Seleccionando concierto (New Years Concert)...")
        try:
            radio_button = wait.until(EC.presence_of_element_located((By.ID, 'id_konzert_2')))
            driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", radio_button)
            logger.info("Concierto seleccionado")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error al seleccionar concierto: {e}")
            take_screenshot(driver, "error_concierto")
            raise

        logger.info("Haciendo clic en botón 'Continue to number of tickets and seat selection'...")
        try:
            continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to number of tickets and seat selection')]")))
            continue_button.click()
            logger.info("Avanzando a selección de asientos")
            time.sleep(3)
        except Exception as e:
            logger.error(f"Error al hacer clic en botón de continuar: {e}")
            take_screenshot(driver, "error_continue_1")
            raise

        # --- Paso 4: Selección de asientos ---
        logger.info("Seleccionando número de asientos...")
        try:
            seat_select_element = wait.until(EC.presence_of_element_located((By.ID, 'id_anzahl')))
            seat_select = Select(seat_select_element)
            seat_select.select_by_value('2')
            logger.info("Seleccionados 2 asientos")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error al seleccionar número de asientos: {e}")
            take_screenshot(driver, "error_asientos")
            raise

        logger.info("Seleccionando categoría 1...")
        try:
            kategorie_radio_button = wait.until(EC.presence_of_element_located((By.ID, 'id_kategorie_0')))
            driver.execute_script("arguments[0].scrollIntoView(true);", kategorie_radio_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", kategorie_radio_button)
            logger.info("Categoría 1 seleccionada")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error al seleccionar categoría: {e}")
            take_screenshot(driver, "error_categoria")
            raise

        logger.info("Haciendo clic en 'Continue to personal data'...")
        try:
            continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to personal data')]")))
            # Hacer scroll al botón y esperar un poco
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
            time.sleep(1)
            # Intentar click con JavaScript para mayor confiabilidad
            driver.execute_script("arguments[0].click();", continue_button)
            logger.info("Botón clickeado, esperando carga de página de datos personales...")
            time.sleep(3)

            # Verificar que realmente llegamos a la página de datos personales
            wait.until(EC.presence_of_element_located((By.ID, 'id_anrede')))
            logger.info("Página de datos personales cargada correctamente")

        except TimeoutException as e:
            logger.error(f"La página de datos personales no cargó correctamente: {e}")
            take_screenshot(driver, "error_pagina_no_cargada")
            raise
        except Exception as e:
            logger.error(f"Error al hacer clic en botón de continuar: {e}")
            take_screenshot(driver, "error_continue_2")
            raise

        # --- Paso 5: Formulario personal ---
        logger.info("Rellenando formulario personal...")
        try:
            # Esperar a que el formulario esté listo
            time.sleep(2)

            # Salutation
            logger.info("Seleccionando saludo...")
            anrede_element = wait.until(EC.presence_of_element_located((By.ID, 'id_anrede')))

            # Verificar que es un select
            if anrede_element.tag_name != 'select':
                logger.error(f"Elemento id_anrede es un {anrede_element.tag_name}, no un select")
                take_screenshot(driver, "error_anrede_not_select")
                raise Exception(f"id_anrede no es un elemento select")

            salutation_select = Select(anrede_element)
            salutation_select.select_by_value('Mr.')
            logger.info("Saludo seleccionado")
            time.sleep(0.5)

            # Generar datos
            first_name = fake.first_name_male()
            last_name = fake.last_name()
            address = fake.address()
            zipcode = fake.postcode()
            city = fake.city()

            logger.info(f"Generando datos ficticios para: {first_name} {last_name}")

            # Rellenar campos
            simulate_typing(driver.find_element(By.ID, 'id_vorname'), first_name)
            simulate_typing(driver.find_element(By.ID, 'id_nachname'), last_name)
            simulate_typing(driver.find_element(By.ID, 'id_adresse'), address)
            simulate_typing(driver.find_element(By.ID, 'id_plz'), zipcode)
            simulate_typing(driver.find_element(By.ID, 'id_ort'), city)

            # País (Japón = 118)
            logger.info("Seleccionando país...")
            country_element = driver.find_element(By.ID, 'id_country')

            # Verificar que es un select
            if country_element.tag_name != 'select':
                logger.error(f"Elemento id_country es un {country_element.tag_name}, no un select")
                take_screenshot(driver, "error_country_not_select")
                raise Exception(f"id_country no es un elemento select")

            country_select = Select(country_element)
            country_select.select_by_value('51')
            logger.info("País seleccionado: China")
            time.sleep(0.5)

            # Email
            email = f'discorevivalfilipino1+{counter}@gmail.com'
            driver.find_element(By.ID, 'id_email').send_keys(email)
            driver.find_element(By.ID, 'id_email_confirm').send_keys(email)
            logger.info(f"Email: {email}")
            time.sleep(0.5)

            # Desmarcar newsletter si está marcado
            if driver.find_element(By.ID, 'id_newsletter').is_selected():
                driver.find_element(By.ID, 'id_newsletter').click()
                logger.info("Newsletter desmarcado")

            time.sleep(1)

        except Exception as e:
            logger.error(f"Error al rellenar formulario personal: {e}")
            take_screenshot(driver, "error_formulario")
            raise

        # --- Paso 6: Envío del formulario ---
        logger.info("Enviando formulario (Confirm Data)...")
        try:
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
            submit_button.click()
            logger.info("Formulario enviado, esperando confirmación...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error al enviar formulario: {e}")
            take_screenshot(driver, "error_submit_1")
            raise

        # --- Paso 7: Confirmación final ---
        logger.info("Buscando botón de confirmación final...")
        try:
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Take part in the drawing now')]")))
            submit_button.click()
            logger.info("Confirmación final enviada")
            time.sleep(10)

            # Guardar contador después de la confirmación exitosa
            counter += 1
            save_counter(counter)

            # --- Éxito ---
            success = True
            logger.info(f"✓ Iteración {counter - 1} COMPLETADA EXITOSAMENTE")
            logger.info(f"  Email usado: espinardonacion+{counter - 1}@gmail.com")
            take_screenshot(driver, "exito")

        except Exception as e:
            logger.error(f"Error en confirmación final: {e}")
            take_screenshot(driver, "error_final")
            raise

    except TimeoutException as e:
        logger.error(f"Timeout esperando elemento: {e}")
        if driver:
            take_screenshot(driver, "timeout_error")
    except NoSuchElementException as e:
        logger.error(f"Elemento no encontrado: {e}")
        if driver:
            take_screenshot(driver, "element_not_found")
    except ElementNotInteractableException as e:
        logger.error(f"Elemento no interactuable: {e}")
        if driver:
            take_screenshot(driver, "element_not_interactable")
    except WebDriverException as e:
        logger.error(f"Error del WebDriver: {e}")
        if driver:
            take_screenshot(driver, "webdriver_error")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        if driver:
            take_screenshot(driver, "unexpected_error")
    finally:
        if driver:
            try:
                driver.quit()
            except WebDriverException:
                logger.warning("No se pudo cerrar el navegador correctamente")

    # Espera entre iteraciones (siempre se ejecuta)
    random_interval = random.randint(10, 13) * 60
    if success:
        logger.info(f"Esperando {random_interval / 60:.0f} minutos antes de la siguiente ejecución...")
    else:
        logger.info(f"Iteración fallida. Reintentando en {random_interval / 60:.0f} minutos...")
    time.sleep(random_interval)