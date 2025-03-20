from django import forms
from .models import Demande, Ticket, Local
from events.models import Cotisant

class DemandeForm(forms.ModelForm):
    locaux = forms.ModelMultipleChoiceField(
        queryset=Local.objects.none(),  # Par défaut, aucun local n'est proposé
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    personnes = forms.ModelMultipleChoiceField(
        queryset=Cotisant.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Demande
        fields = ['locaux', 'personnes']

    def __init__(self, *args, **kwargs):
        # On attend un paramètre 'user' pour filtrer les locaux
        user = kwargs.pop('user', None)
        #print(f"USER: {user}")
        super().__init__(*args, **kwargs)
        if user is not None:
            if user.is_superuser:
                # Si l'utilisateur est superuser, on retourne tous les locaux
                self.fields['locaux'].queryset = Local.objects.all()
            elif hasattr(user, 'club'):
                # Sinon, on ne propose que les locaux liés au club de l'utilisateur
                self.fields['locaux'].queryset = user.club.locaux.all()
            else:
                self.fields['locaux'].queryset = Local.objects.none()
        else:
            self.fields['locaux'].queryset = Local.objects.none()

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['sujet', 'description', 'email']  # Ajout de l'email dans les champs du formulaire
