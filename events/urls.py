from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('soirees/', views.liste_soirees, name='liste_soirees'),
    path('soirees/ajouter/', views.ajouter_soiree, name='ajouter_soiree'),
    path('soirees/<int:soiree_id>/', views.detail_soiree, name='detail_soiree'),
    path('cotisants/autocomplete/', views.cotisant_autocomplete, name='cotisant_autocomplete'),
    path('participants/supprimer/<int:participant_id>/', views.supprimer_participant, name='supprimer_participant'),
    path('events/soirees/<int:soiree_id>/export_csv/', views.export_participants_csv, name='export_participants_csv'),
]
