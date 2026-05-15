import os
import django
import json
import traceback
import time

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

from scraper.services.auth_service import (
    obtener_sesion
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

    auth = obtener_sesion()

    page = auth["page"]

    try:

        expedientes_json = (
            obtener_expedientes(page)
        )

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

        guardar_json(
            "scraper/samples/expedientes.json",
            expedientes_json
        )

        juzgados = expedientes_json["data"]

        for juzgado in juzgados:

            nombre_juzgado = (
                juzgado["DesJuz"]
            )

            print(
                f"\nJUZGADO: "
                f"{nombre_juzgado}"
            )

            expedientes = (
                juzgado["expediente"]
            )

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

                    # ======================
                    # DETALLE EXPEDIENTE
                    # ======================

                    detalle_json = (
                        obtener_detalle_expediente(
                            page,
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

                    # ======================
                    # JUICIO
                    # ======================

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

                    # ======================
                    # ACTORES
                    # ======================

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

                    # ======================
                    # DEMANDADOS
                    # ======================

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

                    # ======================
                    # EXPEDIENTE
                    # ======================

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

                    # ======================
                    # ARBOL JUDICIAL
                    # ======================

                    arbol_json = (
                        obtener_arbol_expediente(
                            page,
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

                    # ======================
                    # DESCARGAR PDFs
                    # ======================

                    for nodo in (
                        expediente_db.nodos.all()
                    ):

                        try:

                            pdf_data = (
                                descargar_pdf_actuacion(
                                    page,
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

                        except Exception as e:

                            print(
                                f"Error descargando "
                                f"PDF del nodo "
                                f"{nodo.label}: {e}"
                            )

                    time.sleep(0.5)

                except Exception as e:

                    print(
                        f"Error procesando "
                        f"expediente: {e}"
                    )

                    traceback.print_exc()

    finally:

        auth["browser"].close()

        auth["playwright"].stop()


if __name__ == "__main__":
    main()