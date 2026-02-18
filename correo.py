import imaplib
import email
from email.header import decode_header
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# --- CONFIGURACIÓN ---
EMAIL = "tu_correo@gmail.com"
PASSWORD = "xxxx xxxx xxxx xxxx"
TEXTO_BOTON = "Confirm participation"

def pausa_humana(min_seg=1.5, max_seg=4.0):
    """Pausa aleatoria como lo haría una persona"""
    time.sleep(random.uniform(min_seg, max_seg))

def scroll_natural(driver):
    """Hace scroll poco a poco como si estuviera leyendo"""
    altura_total = driver.execute_script("return document.body.scrollHeight")
    posicion_actual = 0
    
    while posicion_actual < altura_total:
        incremento = random.randint(100, 300)
        posicion_actual += incremento
        driver.execute_script(f"window.scrollTo(0, {posicion_actual});")
        time.sleep(random.uniform(0.3, 0.8))

def mover_raton_y_clicar(driver, elemento):
    """Mueve el ratón de forma natural hasta el elemento y hace clic"""
    actions = ActionChains(driver)
    
    # Moverse al elemento con pequeña desviación aleatoria
    actions.move_to_element_with_offset(
        elemento,
        random.randint(-5, 5),
        random.randint(-5, 5)
    )
    actions.pause(random.uniform(0.3, 0.8))  # pausa antes de clicar
    actions.click()
    actions.perform()

def crear_driver_humano():
    options = webdriver.ChromeOptions()
    
    # User-agent de un Chrome normal
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Eliminar flags que delatan automatización
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Tamaño de ventana normal (no maximizado por defecto como los bots)
    options.add_argument("--window-size=1366,768")
    
    driver = webdriver.Chrome(options=options)
    
    # Ocultar que es Selenium via JavaScript
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def pulsar_boton(url):
    driver = crear_driver_humano()
    
    try:
        print(f"  Abriendo página...")
        driver.get(url)
        
        # Esperar como si estuviera cargando la página
        pausa_humana(2, 5)
        
        # Hacer scroll leyendo la página
        print(f"  Leyendo la página...")
        scroll_natural(driver)
        
        # Otra pausa antes de buscar el botón
        pausa_humana(1, 3)
        
        wait = WebDriverWait(driver, 10)
        boton = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(text(), '{TEXTO_BOTON}')]")
        ))
        
        # Scroll hasta el botón
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
        pausa_humana(0.8, 2)
        
        # Mover el ratón y clicar de forma natural
        print(f"  Haciendo clic en el botón...")
        mover_raton_y_clicar(driver, boton)
        
        print(f"  ✅ Botón '{TEXTO_BOTON}' pulsado correctamente")
        pausa_humana(3, 6)  # esperar respuesta de la web
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        driver.quit()

# --- El resto del código es igual que antes ---

def conectar_gmail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def buscar_correos(mail):
    status, mensajes = mail.search(None, 'UNSEEN')
    ids = mensajes[0].split()
    
    ids_filtrados = []
    for msg_id in ids:
        status, data = mail.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        asunto_raw = decode_header(msg["Subject"])[0][0]
        if isinstance(asunto_raw, bytes):
            asunto_raw = asunto_raw.decode()
        if "New Year's Concert" in asunto_raw or "Ticket Drawing" in asunto_raw:
            ids_filtrados.append(msg_id)
    
    return ids_filtrados

def extraer_link(mail, msg_id):
    status, data = mail.fetch(msg_id, "(RFC822)")
    msg = email.message_from_bytes(data[0][1])
    
    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break
    else:
        if msg.get_content_type() == "text/html":
            html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    
    if not html_body:
        return None
    
    soup = BeautifulSoup(html_body, "html.parser")
    for link in soup.find_all("a"):
        if TEXTO_BOTON.lower() in link.get_text().strip().lower():
            return link.get("href")
    
    return None

def marcar_como_leido(mail, msg_id):
    mail.store(msg_id, "+FLAGS", "\\Seen")

def revisar_correo():
    print(f"\n[{time.strftime('%H:%M:%S')}] Revisando correo...")
    try:
        mail = conectar_gmail()
        ids = buscar_correos(mail)
        
        if not ids:
            print("  No hay correos nuevos con ese asunto.")
        else:
            print(f"  ¡Encontrados {len(ids)} correo(s)!")
            for msg_id in ids:
                link = extraer_link(mail, msg_id)
                if link:
                    print(f"  Link encontrado: {link}")
                    pulsar_boton(link)
                    marcar_como_leido(mail, msg_id)
                else:
                    print(f"  No se encontró el botón '{TEXTO_BOTON}' en el correo.")
        
        mail.logout()
    except Exception as e:
        print(f"  ❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🎵 Bot iniciado - revisando cada 10 minutos")
    print(f"   Buscando: \"New Year's Concert | Ticket Drawing\"")
    print(f"   Botón: \"{TEXTO_BOTON}\"")
    print("   Pulsa Ctrl+C para detener\n")
    
    while True:
        revisar_correo()
        print(f"  Próxima revisión en 10 minutos...")
        time.sleep(600)