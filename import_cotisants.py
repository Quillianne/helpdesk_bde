import csv
from datetime import datetime
from events.models import Cotisant

def import_cotisants(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                debut_adhesion = datetime.strptime(row["Début d'adhésion"], '%d/%m/%Y')
                fin_adhesion = datetime.strptime(row["Fin d'adhésion"], '%d/%m/%Y')
            except ValueError:
                print(f"Erreur de format de date pour {row['Nom']} {row['Prénom']}")
                continue
            
            # Vérifier si le cotisant existe déjà
            cotisant = Cotisant.objects.filter(email=row['Email']).first()
            if cotisant:
                print(f"Cotisant avec l'email {cotisant.email} existe déjà. Mise à jour des informations.")
                cotisant.nom = row['Nom']
                cotisant.prenom = row['Prénom']
                cotisant.promotion = row['Promotion']
                cotisant.type_cotis = row['Type Cotis']
                cotisant.debut_adhesion = debut_adhesion
                cotisant.fin_adhesion = fin_adhesion
                cotisant.duree_restante_annees = int(row['En Année'])
                cotisant.duree_restante_mois = int(row['En Mois'])
                cotisant.cesure = bool(int(row['Césure']))
                cotisant.redoublement = bool(int(row['Redoublement']))
                cotisant.double_diplome = bool(int(row['Double Diplôme']))
                cotisant.save()
            else:
                Cotisant.objects.create(
                    nom=row['Nom'],
                    prenom=row['Prénom'],
                    promotion=row['Promotion'],
                    email=row['Email'],
                    type_cotis=row['Type Cotis'],
                    debut_adhesion=debut_adhesion,
                    fin_adhesion=fin_adhesion,
                    duree_restante_annees=int(row['En Année']),
                    duree_restante_mois=int(row['En Mois']),
                    cesure=bool(int(row['Césure'])),
                    redoublement=bool(int(row['Redoublement'])),
                    double_diplome=bool(int(row['Double Diplôme']))
                )
                print(f"Cotisant {row['Nom']} {row['Prénom']} ajouté.")
