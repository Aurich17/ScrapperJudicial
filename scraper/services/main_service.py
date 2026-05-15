import os
import django
import json
import traceback
import time
import requests

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings"
)

django.setup()

from scraper.models import (
    Expediente,
    Documento
)

from scraper.services.expedientes_service import (
    obtener_expedientes
)

from scraper.services.detalle_service import (
    obtener_detalle_expediente
)

from scraper.services.arbol_service import (
    obtener_arbol_expediente,
    guardar_nodos_arbol
)

from scraper.services.pdf_service import (
    descargar_pdf_actuacion
)

from scraper.utils.constants import (
    MATERIAS_DEFAULT
)

from scraper.services.auth_service import (
    login_automatico
)


def guardar_json(
    nombre_archivo,
    data
):

    with open(
        nombre_archivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def main():

    try:

        try:
            login_automatico()
        except Exception:
            pass

        consultas = []
        for materia in MATERIAS_DEFAULT:
            if materia == 3:
                consultas.append((3, None))
                consultas.append((3, "N"))
                continue

            consultas.append((materia, None))

        for materia, adolescentes in consultas:

            try:
                expedientes_json = (
                    obtener_expedientes(
                        materia=materia,
                        adolescentes=adolescentes
                    )
                )
            except requests.exceptions.HTTPError as e:
                response = getattr(e, "response", None)
                if response is not None and response.status_code == 401:
                    print(
                        "No autorizado (401). "
                        "El token/cookies en auth.json "
                        "están inválidos o expiraron."
                    )
                    print(
                        "Abre el portal en Chrome, "
                        "asegúrate de estar logueado, "
                        "y vuelve a enviar el token "
                        "con la extensión y token_server.py."
                    )
                    return
                raise

            if not isinstance(
                expedientes_json.get("data"),
                list
            ):

                print(
                    "Error obteniendo expedientes:"
                )

                print(
                    expedientes_json.get("data")
                )

                return

            juzgados = expedientes_json["data"]

            for juzgado in juzgados:

                if not isinstance(juzgado, dict):
                    print(
                        f"Juzgado inválido: {juzgado}"
                    )
                    continue

                nombre_juzgado = (
                    juzgado.get("DesJuz")
                    or juzgado.get("desJuz")
                    or juzgado.get("DESJUZ")
                    or juzgado.get("descripcion")
                    or juzgado.get("nombre")
                    or f"JUZGADO {juzgado.get('IdJuzgado') or 'SIN_ID'}"
                )

                print(
                    f"\nJUZGADO: "
                    f"{nombre_juzgado} "
                    f"(materia {materia})"
                )

                expedientes = (
                    juzgado.get("expediente", [])
                )

                if not isinstance(expedientes, list):
                    print(
                        f"Expedientes inválidos para juzgado: "
                        f"{nombre_juzgado}"
                    )
                    continue

                for expediente in expedientes:

                    try:

                        numero = expediente.get(
                            "numero"
                        )

                        anio = expediente.get(
                            "anio"
                        )

                        id_carpeta = expediente.get(
                            "idCarpetaJudicial"
                        )

                        print(
                            f"\nProcesando expediente "
                            f"{numero}/{anio}"
                        )

                        detalle_json = (
                            obtener_detalle_expediente(
                                id_carpeta
                            )
                        )

                        guardar_json(
                            f"scraper/samples/"
                            f"detalle_{id_carpeta}.json",
                            detalle_json
                        )

                        data_detalle = (
                            detalle_json.get(
                                "data",
                                {}
                            )
                        )

                        if not isinstance(
                            data_detalle,
                            dict
                        ):

                            print(
                                f"Detalle inválido "
                                f"para expediente "
                                f"{numero}/{anio}"
                            )

                            continue

                        juicio = ""

                        juicio_data = (
                            data_detalle.get(
                                "juicio"
                            )
                        )

                        if juicio_data:

                            juicio = (
                                juicio_data.get(
                                    "descLiti",
                                    ""
                                )
                            )

                        partes = (
                            data_detalle.get(
                                "partes",
                                {}
                            )
                        )

                        actores = (
                            partes.get(
                                "actores",
                                []
                            )
                        )

                        lista_actores = []

                        for actor_item in actores:

                            nombre_actor = (
                                actor_item.get(
                                    "nombreCompleto"
                                )
                            )

                            if nombre_actor:

                                lista_actores.append(
                                    nombre_actor
                                )

                        actor = ", ".join(
                            lista_actores
                        )

                        demandados = (
                            partes.get(
                                "demandados",
                                []
                            )
                        )

                        lista_demandados = []

                        for demandado_item in demandados:

                            nombre_demandado = (
                                demandado_item.get(
                                    "nombreCompleto"
                                )
                            )

                            if nombre_demandado:

                                lista_demandados.append(
                                    nombre_demandado
                                )

                        demandado = ", ".join(
                            lista_demandados
                        )

                        fecha_radicacion = (
                            expediente.get(
                                "fechaRadicacion"
                            )
                        )

                        expediente_db, created = (
                            Expediente.objects.update_or_create(

                                id_carpeta_judicial=id_carpeta,

                                defaults={

                                    "numero":
                                    numero,

                                    "anio":
                                    anio,

                                    "materia":
                                    materia,

                                "adolescentes":
                                adolescentes,

                                    "juzgado":
                                    nombre_juzgado,

                                    "actor":
                                    actor,

                                    "demandado":
                                    demandado,

                                    "juicio":
                                    juicio,

                                    "fecha_radicacion":
                                    fecha_radicacion
                                }
                            )
                        )

                        arbol_json = (
                            obtener_arbol_expediente(
                                id_carpeta
                            )
                        )

                        guardar_json(
                            f"scraper/samples/"
                            f"arbol_{id_carpeta}.json",
                            arbol_json
                        )

                        nodos = (
                            arbol_json.get(
                                "data",
                                []
                            )
                        )

                        guardar_nodos_arbol(
                            nodos,
                            expediente_db
                        )

                        for nodo in (
                            expediente_db.nodos.all()
                        ):

                            try:

                                pdf_data = (
                                    descargar_pdf_actuacion(
                                        nodo
                                    )
                                )

                                if not pdf_data:

                                    continue

                                Documento.objects.update_or_create(

                                    referencia_id=
                                    nodo.referencia_id,

                                    defaults={

                                        "expediente":
                                        expediente_db,

                                        "id_imagen":
                                        nodo.referencia_id,

                                        "ruta":
                                        pdf_data[
                                            "ruta"
                                        ],

                                        "archivo":
                                        pdf_data[
                                            "archivo"
                                        ]
                                    }
                                )

                            except requests.exceptions.HTTPError as e:

                                response = getattr(
                                    e,
                                    "response",
                                    None
                                )

                                if (
                                    response is not None
                                    and response.status_code == 401
                                ):
                                    print(
                                        "No autorizado (401) descargando PDFs. "
                                        "Refresca sesión/token y reintenta."
                                    )
                                    return

                                print(
                                    f"Error descargando "
                                    f"PDF del nodo "
                                    f"{nodo.label}: {e}"
                                )

                            except Exception as e:

                                print(
                                    f"Error descargando "
                                    f"PDF del nodo "
                                    f"{nodo.label}: {e}"
                                )

                        time.sleep(0.2)

                    except Exception as e:

                        print(
                            f"Error procesando "
                            f"expediente: {e}"
                        )

                        traceback.print_exc()

    except Exception as e:

        print(
            f"Error general: {e}"
        )

        traceback.print_exc()


if __name__ == "__main__":
    main()
