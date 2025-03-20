# acces/urls.py

from django.urls import path
from . import views

app_name = 'acces'

urlpatterns = [
    path('gestion_club/', views.gestion_club, name='gestion_club'),
    path('club/<int:club_id>/demandes/', views.club_demandes, name='club_demandes'),
    path('demande/nouvelle/<int:club_id>/', views.nouvelle_demande, name='nouvelle_demande'),
    path('demande/modifier/<int:demande_id>/', views.modifier_demande, name='modifier_demande'),
    path('tickets/', views.liste_tickets, name='liste_tickets'),
    path('ticket/nouveau/', views.nouveau_ticket, name='nouveau_ticket'),
    path('president/', views.demandes_president, name='demandes_president'),
    path('president/demande/modifier/<int:demande_id>/', views.modifier_demande_president, name='modifier_demande_president'),
    path('demande/<int:demande_id>/telecharger/', views.telecharger_demande_pdf, name='telecharger_demande_pdf'),
    path('import-cotisants/', views.import_cotisants_view, name='import_cotisants'),
    path('president/save_info/', views.save_president_info, name='save_president_info'),
    path('', views.menu_principal, name='menu_principal'),
    path('save_signature/', views.save_signature, name='save_signature'),
]



urlpatterns += [
    path('cotisants/autocomplete/', views.cotisant_autocomplete, name='cotisant_autocomplete'),
]

