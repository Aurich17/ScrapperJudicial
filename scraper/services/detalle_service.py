import requests

from scraper.utils.constants import (
    API_URL
)

from scraper.services.auth_service import (
    request_get
)


def obtener_detalle_expediente(
    id_carpeta_judicial
):

    url = (
        f"{API_URL}/portadas/obtener-carpetas-judiciales"
    )

    response = request_get(
        url,
        params={
            "idCarpetaJudicial": id_carpeta_judicial
        },
        timeout=120
    )

    return response.json()
