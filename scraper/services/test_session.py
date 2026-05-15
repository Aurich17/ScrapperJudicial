from playwright.sync_api import sync_playwright

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

    input("Verifica si sigue autenticado...")

    browser.close()