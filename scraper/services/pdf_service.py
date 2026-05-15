import os
import requests

from pypdf import PdfWriter
from pypdf import PdfReader

from urllib.parse import quote

from scraper.utils.constants import (
    API_URL
)

from scraper.services.auth_service import (
    request_get
)


DOWNLOADS_PATH = "downloads"

TEMP_PATH = "temp_pdfs"

os.makedirs(
    DOWNLOADS_PATH,
    exist_ok=True
)

os.makedirs(
    TEMP_PATH,
    exist_ok=True
)


def limpiar_nombre_archivo(nombre):

    caracteres_invalidos = [
        "\\",
        "/",
        ":",
        "*",
        "?",
        "\"",
        "<",
        ">",
        "|"
    ]

    for caracter in caracteres_invalidos:

        nombre = nombre.replace(
            caracter,
            "-"
        )

    return nombre.strip()


def obtener_imagenes_actuacion(
    id_actuacion
):

    url = (
        f"{API_URL}/expedientes-autorizados/imagenes"
    )

    response = request_get(
        url,
        params={
            "idActuacion": id_actuacion
        },
        timeout=120
    )

    return response.json()


def obtener_imagenes_carpeta(
    id_carpeta_judicial
):

    url = (
        f"{API_URL}/expedientes-autorizados/imagenes"
    )

    response = request_get(
        url,
        params={
            "idCarpetaJudicial": id_carpeta_judicial
        },
        timeout=120
    )

    return response.json()


def descargar_pagina_pdf(
    ruta,
    ruta_destino
):

    url = (
        f"{API_URL}/expedientes-autorizados/get-imagen"
    )

    response = request_get(
        url,
        params={
            "ruta": quote(ruta)
        },
        timeout=120,
        stream=True
    )

    with open(
        ruta_destino,
        "wb"
    ) as f:

        for chunk in response.iter_content(
            chunk_size=1024 * 256
        ):
            if chunk:
                f.write(chunk)


def fusionar_pdfs(
    archivos_pdf,
    salida_pdf
):

    writer = PdfWriter()

    for archivo in archivos_pdf:

        reader = PdfReader(
            archivo
        )

        for pagina in reader.pages:

            writer.add_page(
                pagina
            )

    with open(
        salida_pdf,
        "wb"
    ) as output:

        writer.write(output)


def descargar_pdf_principal(
    nodo
):

    expediente = nodo.expediente

    imagenes_json = (
        obtener_imagenes_carpeta(
            expediente.id_carpeta_judicial
        )
    )

    imagenes = imagenes_json.get(
        "data",
        []
    )

    if not imagenes:

        return None

    imagen_principal = next(

        (
            img for img in imagenes
            if img.get("posicion") == 1
        ),

        None
    )

    if not imagen_principal:

        return None

    nombre_final = (
        limpiar_nombre_archivo(
            f"{nodo.label}.pdf"
        )
    )

    ruta_final = os.path.join(
        DOWNLOADS_PATH,
        nombre_final
    )

    if os.path.exists(ruta_final):

        print(
            f"PDF principal ya existe: "
            f"{nombre_final}"
        )

        return {

            "archivo":
            nombre_final,

            "ruta":
            ruta_final
        }

    ruta_pdf = (
        imagen_principal.get(
            "ruta"
        )
    )

    print(
        f"Descargando PDF principal: "
        f"{nombre_final}"
    )

    descargar_pagina_pdf(
        ruta_pdf,
        ruta_final
    )

    return {

        "archivo":
        nombre_final,

        "ruta":
        ruta_final
    }


def descargar_pdf_actuacion(
    nodo
):

    if nodo.cve_tipo_actuacion is None:

        return descargar_pdf_principal(
            nodo
        )

    referencia_id = (
        nodo.referencia_id
    )

    imagenes_json = (
        obtener_imagenes_actuacion(
            referencia_id
        )
    )

    imagenes = imagenes_json.get(
        "data",
        []
    )

    if not imagenes:

        return None

    nombre_final = (
        limpiar_nombre_archivo(
            f"{nodo.label}.pdf"
        )
    )

    ruta_final = os.path.join(
        DOWNLOADS_PATH,
        nombre_final
    )

    if os.path.exists(ruta_final):

        print(
            f"PDF ya existe: "
            f"{nombre_final}"
        )

        return {

            "archivo":
            nombre_final,

            "ruta":
            ruta_final
        }

    archivos_temporales = []

    for index, imagen in enumerate(imagenes):

        try:

            ruta = imagen.get(
                "ruta"
            )

            temp_pdf = os.path.join(
                TEMP_PATH,
                f"{referencia_id}_{index}.pdf"
            )

            print(
                f"Descargando página "
                f"{index + 1} "
                f"de {nombre_final}"
            )

            descargar_pagina_pdf(
                ruta,
                temp_pdf
            )

            archivos_temporales.append(
                temp_pdf
            )

        except Exception as e:

            print(
                f"Error descargando página: "
                f"{e}"
            )

    if not archivos_temporales:

        return None

    print(
        f"Fusionando PDF: "
        f"{nombre_final}"
    )

    fusionar_pdfs(
        archivos_temporales,
        ruta_final
    )

    for archivo_temp in archivos_temporales:

        try:

            os.remove(
                archivo_temp
            )

        except:
            pass

    return {

        "archivo":
        nombre_final,

        "ruta":
        ruta_final
    }
