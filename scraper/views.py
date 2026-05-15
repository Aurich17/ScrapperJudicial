import subprocess
from scraper.models import Expediente
from scraper.models import NodoArbol
from django.shortcuts import render, get_object_or_404

from django.shortcuts import (
    render,
    redirect
)

from scraper.models import (
    Expediente
)

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

def lista_expedientes(request):

    expedientes = (
        Expediente.objects
        .prefetch_related("documentos")
        .all()
        .order_by("-created_at")
    )

    return render(

        request,

        "scraper/expedientes.html",

        {
            "expedientes": expedientes
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

    return render(
        request,
        "scraper/detalle_expediente.html",
        {
            "expediente": expediente,
            "nodos_raiz": nodos_raiz,
            "documentos": documentos
        }
    )