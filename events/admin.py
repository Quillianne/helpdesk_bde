from django.contrib import admin
from .models import Cotisant, Banni, Evenement, Participant
from django.utils.translation import gettext_lazy as _

class EstBanniFilter(admin.SimpleListFilter):
    title = _('Est banni')
    parameter_name = 'est_banni'

    def lookups(self, request, model_admin):
        """Options de filtrage qui apparaissent dans l'administration."""
        return (
            ('Oui', _('Oui')),
            ('Non', _('Non')),
        )

    def queryset(self, request, queryset):
        """Filtre les résultats en fonction de l'option sélectionnée."""
        if self.value() == 'Oui':
            return queryset.filter(banni__isnull=False)
        elif self.value() == 'Non':
            return queryset.filter(banni__isnull=True)
        return queryset


@admin.register(Cotisant)
class CotisantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'promotion', 'email', 'est_banni_status')
    list_filter = ('promotion', EstBanniFilter)  # Utilisation du filtre personnalisé

    def est_banni_status(self, obj):
        return obj.est_banni()
    
    est_banni_status.boolean = True  # Affiche une icône oui/non dans l'interface d'administration
    est_banni_status.short_description = 'Est banni'

@admin.register(Banni)
class BanniAdmin(admin.ModelAdmin):
    list_display = ('cotisant', 'date_bannissement', 'duree_bannissement', 'fin_bannissement', 'motif')
    list_filter = ('motif',)
    search_fields = ('cotisant__nom', 'cotisant__prenom')

    def save_model(self, request, obj, form, change):
        obj.cotisant.est_banni = True
        obj.cotisant.save()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj.cotisant.est_banni = False
        obj.cotisant.save()
        super().delete_model(request, obj)

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date', 'identifiant')  # Ajout de participants_list
    list_filter = ('nom', 'date')
    search_fields = ('nom', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)



@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('get_nom', 'get_prenom', 'get_statut', 'evenement')
    list_filter = ('evenement', 'cotisant__nom')  # Ajout du filtre par événement et nom
    search_fields = ('cotisant__nom', 'cotisant__prenom', 'nom', 'prenom', 'evenement__nom')  # Recherche par nom et événement

    def get_nom(self, obj):
        if obj.cotisant:  # Si le participant est un cotisant
            return obj.cotisant.nom
        return obj.nom  # Sinon, c'est un extérieur

    def get_prenom(self, obj):
        if obj.cotisant:  # Si le participant est un cotisant
            return obj.cotisant.prenom
        return obj.prenom  # Sinon, c'est un extérieur

    def get_statut(self, obj):
        if obj.cotisant:  # Si le participant est un cotisant
            return f"Promotion {obj.cotisant.promotion}"  # Retourne la promotion du cotisant
        return obj.statut  # Sinon, retourne le statut normal (extérieur)

    get_nom.short_description = 'Nom'
    get_prenom.short_description = 'Prénom'
    get_statut.short_description = 'Statut'



