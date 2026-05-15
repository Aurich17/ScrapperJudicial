import requests

from scraper.utils.constants import (
    API_URL
)

from scraper.services.auth_service import (
    request_get
)


def obtener_expedientes(
    materia=1,
    materias=None,
    adolescentes=None
):

    url = (
        f"{API_URL}/expedientes-autorizados"
    )

    if materias is None:
        materias = [materia]

    params = [
        ("cveMateria[]", m)
        for m in materias
    ]

    if adolescentes is not None:
        params.append(
            ("adolescentes", adolescentes)
        )

    response = request_get(
        url,
        params=params,
        timeout=120
    )

    return response.json()


def obtener_detalle_expediente(
    id_carpeta
):

    url = (
        f"{API_URL}/portadas/obtener-carpetas-judiciales"
    )

    response = request_get(
        url,
        params={
            "idCarpetaJudicial": id_carpeta
        },
        timeout=120
    )

    return response.json()
