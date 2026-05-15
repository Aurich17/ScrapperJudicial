from django.urls import path

from scraper.views import (
    lista_expedientes,
    sincronizar_expedientes,
    detalle_expediente
)


urlpatterns = [

    path(
        "",
        lista_expedientes,
        name="lista_expedientes"
    ),

    path(
        "sincronizar/",
        sincronizar_expedientes,
        name="sincronizar_expedientes"
    ),

    path(
        "expediente/<int:id>/",
        detalle_expediente,
        name="detalle_expediente"
    ),

]