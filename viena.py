import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker
import random
import os
from datetime import datetime 

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
        with open(counter_file_path, 'r') as file:
            return int(file.read().strip())
    else:
        return 1  # Si no existe el archivo, empezar desde 1

# Función para guardar el contador en el archivo
def save_counter(counter):
    with open(counter_file_path, 'w') as file:
        file.write(str(counter))

# Función para simular la escritura lenta
def simulate_typing(element, text):
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.1, 0.3))  # Tiempo aleatorio entre cada tecla

# Obtener el contador desde el archivo (o empezar en 1)
counter = get_counter()

while True:
    # Iniciar el navegador
    driver = init_driver()

    try:
        # Abre la página web
        driver.get("https://verlosung.wienerphilharmoniker.at/en/form")

        # Espera hasta que el botón de cookies esté disponible y haz clic en él
        wait = WebDriverWait(driver, 10)
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'accept-cookie-settings')))
        accept_cookies_button.click()

        # Espera para asegurarse de que se haya aceptado las cookies antes de proceder
        time.sleep(3)

        # Encuentra el radio button y desplázate hacia él para asegurarte de que es visible
        radio_button = driver.find_element(By.ID, 'id_konzert_2')
        actions = ActionChains(driver)
        actions.move_to_element(radio_button).perform()

        # Espera hasta que el radio button sea clickeable
        wait.until(EC.element_to_be_clickable((By.ID, 'id_konzert_2')))

        # Si el clic no funciona, usa JavaScript para hacerlo
        driver.execute_script("arguments[0].click();", radio_button)

        # Espera más tiempo para verificar que el radio button está seleccionado
        time.sleep(13)

        # Buscar el botón por su texto visible
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to number of tickets and seat selection')]")))
        continue_button.click()

        time.sleep(13)

        # Espera a que la página se cargue completamente antes de continuar
        # Usamos una espera para asegurarnos de que el select esté visible
        wait.until(EC.presence_of_element_located((By.ID, 'id_anzahl')))  # Espera a que el select esté disponible

        # Si la página está cargada, interactuamos con el select
        seat_select = Select(driver.find_element(By.ID, 'id_anzahl'))
        seat_select.select_by_value('2')  # Selecciona el valor '2'
        #pulsa en el radio button


        kategorie_radio_button = driver.find_element(By.ID, 'id_kategorie_0')
        actions = ActionChains(driver)
        actions.move_to_element(kategorie_radio_button).perform()

        # Espera hasta que el radio button sea clickeable
        wait.until(EC.element_to_be_clickable((By.ID, 'id_kategorie_0')))

        # Si el clic no funciona, usa JavaScript para hacerlo
        driver.execute_script("arguments[0].click();", kategorie_radio_button)

        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue to personal data')]")))
        continue_button.click()

        time.sleep(13)

        # Ahora, rellena el formulario personal
        # Espera a que el formulario esté disponible
        wait.until(EC.presence_of_element_located((By.ID, 'id_anrede')))



        # Genera datos aleatorios usando Faker
        salutation_select = Select(driver.find_element(By.ID, 'id_anrede'))
        salutation_select.select_by_value('Mr.')  # Siempre seleccionamos 'Mr.'

        driver.find_element(By.ID, 'id_titel').send_keys('Dr.')  # Título académico (opcional)
        simulate_typing(driver.find_element(By.ID, 'id_vorname'), fake.first_name_male())  # Nombre japonés
        simulate_typing(driver.find_element(By.ID, 'id_nachname'), fake.last_name())  # Apellido japonés
        simulate_typing(driver.find_element(By.ID, 'id_adresse'), fake.address())  # Dirección simulada
        simulate_typing(driver.find_element(By.ID, 'id_plz'), fake.zipcode())  # Código Postal aleatorio
        simulate_typing(driver.find_element(By.ID, 'id_ort'), fake.city())  # Ciudad aleatoria

        # Selecciona Japón como país
        country_select = Select(driver.find_element(By.ID, 'id_country'))
        country_select.select_by_value('118')  # Japón (ID del país en la lista)

        # Generar un correo electrónico con numeración secuencial
        email = f'espinardonacionusa+{counter}@gmail.com'  # Genera un email con un número
        driver.find_element(By.ID, 'id_email').send_keys(email)  # Email
        driver.find_element(By.ID, 'id_email_confirm').send_keys(email)  # Repetir email

        # No suscribirse al boletín
        if driver.find_element(By.ID, 'id_newsletter').is_selected():
            driver.find_element(By.ID, 'id_newsletter').click()  # Desmarca la casilla si está seleccionada

        # Envía el formulario
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        # Espera para asegurarse de que se ha enviado el formulario
        time.sleep(15)

        # Incrementar el contador para el siguiente correo
        counter += 1

        # Guardar el contador en el archivo
        save_counter(counter)
        
        # Clic en el botón de confirmación en el paso final
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Take part in the drawing now')]")))
        submit_button.click()
        
        # Espera para asegurarse de que se ha enviado el formulario
        time.sleep(25)

        # Cerrar el navegador al final de cada interacción
        driver.quit()

        # Obtener la hora actual
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Genera un intervalo aleatorio entre 15 y 20 minutos
        random_interval = random.randint(15, 18) * 60  # Genera un tiempo aleatorio entre 15 y 20 minutos
        print(f"Esperando {random_interval / 60} minutos antes de la siguiente ejecución... (Hora de ejecución: {current_time})")

        # Espera el intervalo aleatorio
        time.sleep(random_interval)

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        driver.quit()  # Cerrar el navegador en caso de error para reiniciar el ciclo