from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse

class Cotisant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    promotion = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    type_cotis = models.CharField(max_length=10)
    debut_adhesion = models.DateField()
    fin_adhesion = models.DateField()
    duree_restante_annees = models.IntegerField()
    duree_restante_mois = models.IntegerField()
    cesure = models.BooleanField(default=False)
    redoublement = models.BooleanField(default=False)
    double_diplome = models.BooleanField(default=False)

    def est_banni(self):
        """Vérifie si le cotisant est banni en fonction de l'existence d'un objet Banni lié."""
        return hasattr(self, 'banni') and self.banni.fin_bannissement() > timezone.now()


    def __str__(self):
        return f"{self.nom} {self.prenom}"



class Banni(models.Model):
    MOTIF_CHOICES = [
        ('Sanction', 'Sanction'),
        ('Mesure préventive', 'Mesure préventive'),
    ]

    cotisant = models.OneToOneField(Cotisant, on_delete=models.CASCADE, related_name='banni')
    date_bannissement = models.DateTimeField(default=timezone.now)
    duree_bannissement = models.IntegerField(help_text="Durée du bannissement en jours")
    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES)

    def fin_bannissement(self):
        """Calcule la date de fin de bannissement."""
        return self.date_bannissement + timedelta(days=self.duree_bannissement)

    def __str__(self):
        return f"Banni : {self.cotisant.nom} {self.cotisant.prenom}"

class Evenement(models.Model):
    nom = models.CharField(max_length=100)
    date = models.DateTimeField()
    identifiant = models.CharField(max_length=100, help_text="Choisissez un identifiant pour sécuriser l'accès à cet événement.")


    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('detail_soiree', args=[str(self.id)])

class Participant(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='participants')
    cotisant = models.ForeignKey(Cotisant, null=True, blank=True, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    statut = models.CharField(max_length=100)

    class Meta:
        unique_together = ('evenement', 'cotisant')  # Contrainte d'unicité

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.evenement.nom}"