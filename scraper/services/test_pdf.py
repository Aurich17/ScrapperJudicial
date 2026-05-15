import requests
from playwright.sync_api import sync_playwright


BASE_URL = "https://tribunalelectronicobk.pjedomex.gob.mx"


def descargar_pdf(session, ruta, nombre_archivo):

    url = f"{BASE_URL}/api/expedientes-autorizados/get-imagen"

    params = {
        "ruta": ruta
    }

    response = session.get(
        url,
        params=params
    )

    print("STATUS:", response.status_code)

    if response.status_code == 200:

        with open(nombre_archivo, "wb") as f:
            f.write(response.content)

        print("PDF descargado correctamente")

    else:
        print("Error descargando PDF")


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state="session.json"
    )

    page = context.new_page()

    page.goto(
        "https://tribunalelectronico.pjedomex.gob.mx/"
    )

    # Crear sesión requests
    session = requests.Session()

    # Pasar cookies Playwright -> requests
    cookies = context.cookies()

    for cookie in cookies:

        session.cookies.set(
            cookie["name"],
            cookie["value"]
        )

    # Ruta PDF
    ruta = "imagenes/ecatepec/civil/10218/2026/expediente/82/EXPE442027740.pdf"

    # Descargar
    descargar_pdf(
        session,
        ruta,
        "archivo1.pdf"
    )

    browser.close()