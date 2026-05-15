import subprocess
from scraper.models import Expediente, NodoArbol
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.html import escape
from django.utils.safestring import mark_safe

from scraper.utils.constants import (
    MATERIAS_DEFAULT,
    MATERIA_ETIQUETAS
)

def lista_expedientes(request):

    materia_seleccionada = None
    adolescentes_seleccionado = None
    materia_seleccionada_key = ""
    materia_param = request.GET.get(
        "materia"
    )

    if materia_param:
        materia_seleccionada_key = materia_param
        if materia_param.upper() == "3N":
            materia_seleccionada = 3
            adolescentes_seleccionado = "N"
        else:
            try:
                materia_seleccionada = int(
                    materia_param
                )
            except ValueError:
                materia_seleccionada = None

    expedientes = (
        Expediente.objects
        .prefetch_related("documentos")
        .all()
        .order_by("-created_at")
    )

    if materia_seleccionada is not None:
        expedientes = (
            expedientes.filter(
                materia=materia_seleccionada
            )
        )

        if materia_seleccionada == 3:
            if adolescentes_seleccionado == "N":
                expedientes = expedientes.filter(
                    adolescentes="N"
                )
            else:
                expedientes = expedientes.filter(
                    Q(adolescentes__isnull=True) | Q(adolescentes="")
                )

    return render(

        request,

        "scraper/expedientes.html",

        {
            "expedientes": expedientes,
            "materias": [
                {
                    "id": (
                        "3N"
                        if m == 3 and variante == "N"
                        else str(m)
                    ),
                    "label": (
                        "PENAL"
                        if m == 3 and variante == "N"
                        else MATERIA_ETIQUETAS.get(
                            m,
                            f"Materia {m}"
                        )
                    )
                }
                for m in MATERIAS_DEFAULT
                for variante in (
                    ["N", None]
                    if m == 3
                    else [None]
                )
            ],
            "materia_seleccionada": materia_seleccionada_key
        }
    )


def sincronizar_expedientes(request):

    subprocess.Popen(

        [
            "venv/Scripts/python.exe",

            "-m",

            "scraper.services.main_service"
        ]

    )

    return redirect(
        "lista_expedientes"
    )

def detalle_expediente(request, id):

    expediente = get_object_or_404(
        Expediente,
        id=id
    )

    nodos_raiz = NodoArbol.objects.filter(
        expediente=expediente,
        parent__isnull=True
    ).prefetch_related(
        "children"
    ).order_by("-fecha")

    documentos = expediente.documentos.all()

    documentos_por_referencia = {
        d.referencia_id: d
        for d in documentos
        if d.referencia_id
    }

    def renderizar_nodos(nodos):
        items = []

        for nodo in nodos:
            tiene_hijos = nodo.children.exists()
            icono = "📂" if tiene_hijos else "📄"

            documento = documentos_por_referencia.get(
                nodo.referencia_id
            )

            boton_pdf = ""
            if documento:
                boton_pdf = (
                    '<a href="/downloads/'
                    + escape(documento.archivo)
                    + '" target="_blank" class="btn btn-primary btn-sm">Ver PDF</a>'
                )

            fecha = (
                escape(str(nodo.fecha))
                if nodo.fecha
                else ""
            )

            hijos_html = ""
            if tiene_hijos:
                hijos_html = (
                    '<div class="ms-4 mt-2 border-start ps-3">'
                    + renderizar_nodos(nodo.children.all())
                    + "</div>"
                )

            items.append(
                '<li class="mb-3">'
                '<div class="border rounded p-3 bg-white shadow-sm">'
                '<div class="d-flex justify-content-between align-items-start flex-wrap gap-3">'
                "<div>"
                '<div class="fw-semibold mb-1">'
                + icono
                + " "
                + escape(nodo.label)
                + "</div>"
                '<small class="text-muted">'
                + fecha
                + "</small>"
                "</div>"
                "<div>"
                + boton_pdf
                + "</div>"
                "</div>"
                "</div>"
                + hijos_html
                + "</li>"
            )

        return (
            '<ul class="list-unstyled ms-3">'
            + "".join(items)
            + "</ul>"
        )

    arbol_html = ""
    if nodos_raiz.exists():
        arbol_html = mark_safe(
            renderizar_nodos(nodos_raiz)
        )

    return render(
        request,
        "scraper/detalle_expediente.html",
        {
            "expediente": expediente,
            "nodos_raiz": nodos_raiz,
            "documentos": documentos,
            "arbol_html": arbol_html
        }
    )
