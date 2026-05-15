from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scraper", "0004_expediente_materia"),
    ]

    operations = [
        migrations.AddField(
            model_name="expediente",
            name="adolescentes",
            field=models.CharField(blank=True, db_index=True, max_length=1, null=True),
        ),
    ]

