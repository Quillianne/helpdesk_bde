# Generated by Django 4.2.16 on 2024-09-07 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cotisant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
                ("prenom", models.CharField(max_length=100)),
                ("promotion", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("type_cotis", models.CharField(max_length=10)),
                ("debut_adhesion", models.DateField()),
                ("fin_adhesion", models.DateField()),
                ("duree_restante_annees", models.IntegerField()),
                ("duree_restante_mois", models.IntegerField()),
                ("cesure", models.BooleanField(default=False)),
                ("redoublement", models.BooleanField(default=False)),
                ("double_diplome", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Evenement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
                ("date", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Participant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cotisant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.cotisant",
                    ),
                ),
                (
                    "evenement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participants",
                        to="events.evenement",
                    ),
                ),
            ],
        ),
    ]
