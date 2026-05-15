from playwright.sync_api import (
    sync_playwright
)

from scraper.utils.constants import (
    API_URL
)


def token_valido(page):

    try:

        url = (
            f"{API_URL}/expedientes-autorizados"
            f"?cveMateria[]=1"
        )

        data = page.evaluate(
            """
            async (url) => {

                try {

                    const token =
                        localStorage.getItem(
                            "token"
                        );

                    if (!token) {

                        return {
                            error: true
                        };
                    }

                    const response =
                        await fetch(url, {

                        method: "GET",

                        headers: {

                            "Authorization":
                            `Bearer ${token}`,

                            "Content-Type":
                            "application/json"
                        }
                    });

                    return await response.json();

                } catch (e) {

                    return {
                        error: true
                    };
                }
            }
            """,
            url
        )

        return isinstance(
            data.get("data"),
            list
        )

    except Exception:

        return False


def obtener_sesion():

    p = sync_playwright().start()

    browser = p.chromium.connect_over_cdp(
        "http://localhost:9222"
    )

    context = browser.contexts[0]

    if context.pages:

        page = context.pages[0]

    else:

        page = context.new_page()

    print(
        "Validando sesión..."
    )

    valido = token_valido(page)

    if not valido:

        print(
            "Inicia sesión manualmente."
        )

        page.goto(
            "https://tribunalelectronico.pjedomex.gob.mx/auth/login"
        )

        input(
            "Presiona ENTER "
            "después del login..."
        )

    else:

        print(
            "Token activo."
        )

    return {

        "playwright": p,

        "browser": browser,

        "context": context,

        "page": page
    }