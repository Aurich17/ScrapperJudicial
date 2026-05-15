from scraper.utils.constants import API_URL
from scraper.models import NodoArbol
from datetime import datetime


def obtener_arbol_expediente(
    page,
    id_carpeta_judicial
):

    url = (
        f"{API_URL}/expedientes-autorizados/arbol"
        f"?idCarpetaJudicial={id_carpeta_judicial}"
    )

    data = page.evaluate(
        """
        async (url) => {

            const token = localStorage.getItem("token");

            const response = await fetch(url, {

                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            return await response.json();
        }
        """,
        url
    )

    return data

def limpiar_fecha(fecha_str):

    if not fecha_str:
        return None

    try:

        partes = fecha_str.split("-")

        if len(partes) > 3:

            fecha_str = "-".join(partes[1:])

        return datetime.strptime(
            fecha_str,
            "%Y-%m-%d %H:%M:%S"
        )

    except Exception:

        return None

def guardar_nodos_arbol(
    nodos,
    expediente_db,
    parent=None
):

    for nodo in nodos:

        nodo_db, created = (
            NodoArbol.objects.update_or_create(

                expediente=expediente_db,

                referencia_id=nodo.get(
                    "referenciaId"
                ),

                defaults={

                    "expediente":
                    expediente_db,

                    "parent":
                    parent,

                    "label":
                    nodo.get("label"),

                    "fecha":
                    limpiar_fecha(
                        nodo.get("data")
                    ),

                    "icon":
                    nodo.get("icon"),

                    "cve_tipo_actuacion":
                    nodo.get("cveTipoActuacion"),

                    "color":
                    nodo.get("color"),

                    "id_formulario":
                    nodo.get("idFormulario")
                }
            )
        )

        hijos = nodo.get(
            "children",
            []
        )

        if hijos:

            guardar_nodos_arbol(
                hijos,
                expediente_db,
                nodo_db
            )
