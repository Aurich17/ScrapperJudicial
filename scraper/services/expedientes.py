import requests

BASE_URL = "https://tribunalelectronicobk.pjedomex.gob.mx/api"


def obtener_expedientes(session):

    url = f"{BASE_URL}/expedientes-autorizados"

    params = {
        "cveMateria[]": 1
    }

    response = session.get(url, params=params)

    data = response.json()

    return data