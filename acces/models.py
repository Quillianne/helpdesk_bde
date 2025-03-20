# acces/models.py

from django.db import models
from events.models import Cotisant  # Importation du modèle Cotisant
from django.contrib.auth.models import User

class President(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Local(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Club(models.Model):
    nom = models.CharField(max_length=100)
    locaux = models.ManyToManyField('Local', related_name='clubs')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='club', null=True, blank=True)

    def __str__(self):
        return self.nom

class Demande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='demandes')
    locaux = models.ManyToManyField(Local, related_name='demandes')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en_attente')
    personnes = models.ManyToManyField(Cotisant, related_name='demandes')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande du club {self.club.nom} - Statut: {self.get_statut_display()}"


class Ticket(models.Model):
    sujet = models.CharField(max_length=200)
    description = models.TextField()
    email = models.EmailField()  # Champ pour l'adresse email
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket de {self.auteur.prenom} {self.auteur.nom} - {self.sujet}"
