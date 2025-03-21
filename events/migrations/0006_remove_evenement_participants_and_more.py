# Generated by Django 4.2.16 on 2024-09-07 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0005_evenement_participants_alter_participant_cotisant_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evenement",
            name="participants",
        ),
        migrations.AlterField(
            model_name="participant",
            name="cotisant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="events.cotisant",
            ),
        ),
        migrations.AlterField(
            model_name="participant",
            name="evenement",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="participants",
                to="events.evenement",
            ),
        ),
    ]
