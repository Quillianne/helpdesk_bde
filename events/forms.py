from django import forms
from .models import Evenement, Cotisant

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['nom', 'date', 'identifiant']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ParticipantForm(forms.Form):
    cotisant = forms.ModelChoiceField(
        queryset=Cotisant.objects.all(),
        widget=forms.Select(attrs={'class': 'autocomplete'}),
        required=False,  # Le champ peut être laissé vide pour ajouter un participant manuellement
        label="Rechercher un cotisant"
    )
    nom = forms.CharField(max_length=100, required=False, label="Nom")
    prenom = forms.CharField(max_length=100, required=False, label="Prénom")

    def clean(self):
        cleaned_data = super().clean()
        cotisant = cleaned_data.get('cotisant')
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')

        # Si ni le cotisant, ni le nom et prénom ne sont fournis
        if not cotisant and not (nom and prenom):
            raise forms.ValidationError("Vous devez soit sélectionner un cotisant, soit fournir un nom et un prénom.")
        
        return cleaned_data