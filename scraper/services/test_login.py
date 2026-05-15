from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    page.goto(
        "https://tribunalelectronico.pjedomex.gob.mx/auth/login"
    )

    print("Inicia sesión manualmente...")

    input("Cuando termines presiona ENTER...")

    context.storage_state(path="session.json")

    print("Sesión guardada.")

    browser.close()