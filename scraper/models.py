from django.db import models


class Expediente(models.Model):

    numero = models.CharField(
        max_length=50
    )

    anio = models.IntegerField()

    materia = models.IntegerField(
        null=True,
        blank=True,
        db_index=True
    )

    adolescentes = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        db_index=True
    )

    juzgado = models.TextField()

    actor = models.TextField(
        null=True,
        blank=True
    )

    demandado = models.TextField(
        null=True,
        blank=True
    )

    juicio = models.TextField(
        null=True,
        blank=True
    )

    id_carpeta_judicial = models.BigIntegerField(
        unique=True
    )

    fecha_radicacion = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.numero}/{self.anio}"
        )

    @property
    def materia_etiqueta(self):
        from scraper.utils.constants import MATERIA_ETIQUETAS

        if self.materia is None:
            return "Sin materia"

        if self.materia == 3:
            if self.adolescentes == "N":
                return "PENAL"
            return "PENAL INDÍGENAS"

        return MATERIA_ETIQUETAS.get(
            self.materia,
            f"Materia {self.materia}"
        )


class Documento(models.Model):

    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name="documentos"
    )

    id_imagen = models.BigIntegerField(
        unique=True
    )

    referencia_id = models.BigIntegerField(
        null=True,
        blank=True
    )

    ruta = models.TextField()

    archivo = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.archivo


class NodoArbol(models.Model):

    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name="nodos"
    )

    referencia_id = models.BigIntegerField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )

    label = models.TextField()

    fecha = models.DateTimeField(
        null=True,
        blank=True
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    cve_tipo_actuacion = models.IntegerField(
        null=True,
        blank=True
    )

    color = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    id_formulario = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    class Meta:

        ordering = ["fecha"]

    def __str__(self):

        return self.label
