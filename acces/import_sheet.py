import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from .models import Cotisant

def import_cotisants_from_google_sheet(sheet_id, sheet_name):
    # Configuration de l'accès à l'API Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Ouvrir le Google Sheet et accéder à la feuille spécifiée
    spreadsheet = client.open_by_key(sheet_id)  # ID de la feuille Google Sheet
    sheet = spreadsheet.worksheet(sheet_name)  # Nom de l'onglet dans la feuille

    # Récupérer les lignes à partir de la 3ème ligne
    rows = sheet.get_all_values()[2:]  # Récupère toutes les lignes à partir de la 3ème ligne (index 2)

    # Pour garder les noms de colonnes (si vous avez des en-têtes sur la première ligne)
    headers = sheet.row_values(2)  # Supposons que la deuxieme ligne est l'en-tête avec les noms des colonnes
    
    print(headers)
    for row in rows:
        row_dict = dict(zip(headers, row))  # Crée un dictionnaire basé sur les en-têtes et les valeurs de chaque ligne
        try:
            debut_adhesion = datetime.strptime(row_dict["Début d'adhésion"], '%d/%m/%Y')
            fin_adhesion = datetime.strptime(row_dict["Fin d'adhésion"], '%d/%m/%Y')
        except ValueError:
            print(f"Erreur de format de date pour {row_dict['Nom']} {row_dict['Prénom']}")
            continue

        print(row_dict)
        # Vérifier si le cotisant existe déjà dans la base de données
        cotisant = Cotisant.objects.filter(email=row_dict['Mail']).first()
        if cotisant:
            print(f"Cotisant avec l'email {cotisant.email} existe déjà. Mise à jour des informations.")
            cotisant.nom = row_dict['Nom']
            cotisant.prenom = row_dict['Prénom']
            cotisant.promotion = row_dict['Promotion']
            cotisant.type_cotis = row_dict['Type Cotis']
            cotisant.debut_adhesion = debut_adhesion
            cotisant.fin_adhesion = fin_adhesion
            cotisant.duree_restante_annees = int(row_dict['En Année'])
            cotisant.duree_restante_mois = int(row_dict['En Mois'])
            cotisant.cesure = bool(int(row_dict['Césure']))
            cotisant.redoublement = bool(int(row_dict['Redoublement']))
            cotisant.double_diplome = bool(int(row_dict['Double Diplôme']))
            cotisant.save()
        else:
            Cotisant.objects.create(
                nom=row_dict['Nom'],
                prenom=row_dict['Prénom'],
                promotion=row_dict['Promotion'],
                email=row_dict['Mail'],
                type_cotis=row_dict['Type Cotis'],
                debut_adhesion=debut_adhesion,
                fin_adhesion=fin_adhesion,
                duree_restante_annees=int(row_dict['En Année']),
                duree_restante_mois=int(row_dict['En Mois']),
                cesure=bool(int(row_dict['Césure'])),
                redoublement=bool(int(row_dict['Redoublement'])),
                double_diplome=bool(int(row_dict['Double Diplôme']))
            )
            print(f"Cotisant {row_dict['Nom']} {row_dict['Prénom']} ajouté.")

# Utilisation de la fonction
# import_cotisants_from_google_sheet('1ynsxvL5b9B9ZxIFDnI2UjJ88O8gwV3kkAmRyWeBEUmg', 'BDD')