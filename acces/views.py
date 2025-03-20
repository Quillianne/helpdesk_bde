# acces/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import President, Club, Demande, Ticket
from .forms import DemandeForm, TicketForm
from events.models import Cotisant
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .import_sheet import import_cotisants_from_google_sheet
from django.contrib import messages
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings


def home(request):
    return redirect('acces:menu_principal')


@login_required
@csrf_exempt  # Nécessaire pour les requêtes AJAX, mais assurez-vous de l'utiliser uniquement ici
def save_signature(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Accès refusé. Administrateur requis."}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            signature_data = data.get('signature', None)

            if signature_data:
                signature_data = signature_data.split(",")[1]
                signature_image = base64.b64decode(signature_data)

                signature_path = os.path.join(settings.MEDIA_ROOT, 'signatures', 'president_signature.png')
                os.makedirs(os.path.dirname(signature_path), exist_ok=True)

                with open(signature_path, "wb") as f:
                    f.write(signature_image)

                return JsonResponse({"message": "Signature enregistrée avec succès."}, status=200)
            else:
                return JsonResponse({"error": "Aucune signature trouvée dans la requête."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Requête non autorisée."}, status=405)

@login_required  # S'assurer que seul un utilisateur connecté peut accéder à cette vue
def import_cotisants_view(request):
    try:
        # Appel à la fonction qui importe les cotisants depuis Google Sheets
        import_cotisants_from_google_sheet('1ynsxvL5b9B9ZxIFDnI2UjJ88O8gwV3kkAmRyWeBEUmg', 'BDD')
        messages.success(request, "Les cotisants ont été mis à jour depuis Google Sheets.")
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de l'importation des cotisants : {str(e)}")
    
    # Redirection vers la liste des soirées après l'importation
    return redirect('acces:menu_principal')

@login_required
def menu_principal(request):
    # Redirection selon le type d'utilisateur
    if request.user.is_superuser:
        # Redirection vers le menu principal pour les administrateurs
        return render(request, 'acces/menu_principal.html', {'is_admin': True})
    else:
        # Redirection vers la gestion du club pour les utilisateurs non-admin
        return redirect('acces:gestion_club')
    
def cotisant_autocomplete(request):
    term = request.GET.get('term')
    if term:
        terms = term.split()
        query = Q()
        for t in terms:
            query |= Q(nom__icontains=t) | Q(prenom__icontains=t)
        cotisants = Cotisant.objects.filter(query).distinct()
    else:
        cotisants = Cotisant.objects.none()

    results = [
        {'id': cotisant.id, 'nom': cotisant.nom, 'prenom': cotisant.prenom, 'promotion': cotisant.promotion}
        for cotisant in cotisants
    ]

    return JsonResponse({'results': results})

@login_required
def gestion_club(request):
    club = get_object_or_404(Club, user=request.user)  # Récupère le club associé à l'utilisateur connecté
    return render(request, 'acces/gestion_club.html', {'club': club})

@login_required
def club_demandes(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.user:
        raise PermissionDenied  # Restreint l'accès aux seuls utilisateurs associés au club
    demandes = club.demandes.all()
    return render(request, 'acces/club_demandes.html', {'club': club, 'demandes': demandes})

@login_required
def modifier_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)
    if request.user != demande.club.user:
        raise PermissionDenied  # Seuls les utilisateurs associés au club peuvent modifier la demande
    if request.method == 'POST':
        form = DemandeForm(request.POST, user=request.user, instance=demande)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.statut = 'en_attente'  # Réinitialise le statut à "en attente"
            demande.save()
            form.save_m2m()
            return redirect('acces:club_demandes', club_id=demande.club.id)
    else:
        form = DemandeForm(instance=demande, user=request.user)
    return render(request, 'acces/modifier_demande.html', {'form': form, 'demande': demande})

@login_required
def nouvelle_demande(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user != club.user:
        raise PermissionDenied
    if request.method == 'POST':
        #print(f"user: {request.user}")
        form = DemandeForm(request.POST, user=request.user)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.club = club
            demande.save()
            form.save_m2m()
            return redirect('acces:club_demandes', club_id=club.id)
    else:
        form = DemandeForm(user=request.user)
    return render(request, 'acces/nouvelle_demande.html', {'form': form, 'club': club})

@login_required
def nouveau_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.auteur = request.user  # Associe le ticket à l'utilisateur connecté
            ticket.save()
            return redirect('acces:liste_tickets')
    else:
        form = TicketForm()
    return render(request, 'acces/nouveau_ticket.html', {'form': form})

@login_required
def liste_tickets(request):
    tickets = Ticket.objects.filter(auteur=request.user)  # Affiche uniquement les tickets de l'utilisateur connecté
    return render(request, 'acces/liste_tickets.html', {'tickets': tickets})

@login_required
def demandes_president(request):
    # Vérifier si l'utilisateur est le président
    if not request.user.is_superuser:
        raise PermissionDenied

    # Récupérer les demandes en fonction de leur statut
    demandes_en_attente = Demande.objects.filter(statut='en_attente')
    demandes_acceptees = Demande.objects.filter(statut='acceptee')
    president = President.objects.first()

    if request.method == 'POST':
        demande_id = request.POST.get('demande_id')
        action = request.POST.get('action')
        demande = get_object_or_404(Demande, id=demande_id)
        
        # Action d'acceptation ou de rejet
        if action == 'accepter':
            demande.statut = 'acceptee'
            demande.save()
        elif action == 'rejeter':
            demande.statut = 'rejete'
            demande.save()

        # Redirection pour éviter le rechargement en double des formulaires
        return redirect('acces:demandes_president')

    context = {
        'demandes_en_attente': demandes_en_attente,
        'demandes_acceptees': demandes_acceptees,
        'president': president,
    }
    return render(request, 'acces/demandes_president.html', context)


@login_required
def modifier_demande_president(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id)
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = DemandeForm(request.POST, user=request.user, instance=demande)
        if form.is_valid():
            demande = form.save(commit=False)
            action = request.POST.get('action')
            
            # Mise à jour du statut en fonction du bouton cliqué
            if action == 'accepter':
                demande.statut = 'acceptee'
            elif action == 'en_attente':
                demande.statut = 'en_attente'
            
            demande.save()
            form.save_m2m()  # Enregistre les changements de locaux et de personnes

            return redirect('acces:demandes_president')
    else:
        form = DemandeForm(instance=demande, user=request.user)

    return render(request, 'acces/modifier_demande_president.html', {'demande': demande, 'form': form})



@login_required
def telecharger_demande_pdf(request, demande_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    demande = get_object_or_404(Demande, id=demande_id)
    president = President.objects.first()
    
    if not president:
        return HttpResponse("Aucun président défini dans la base de données.", status=500)

    # Chemin absolu de la signature
    signature_path = os.path.join(settings.MEDIA_ROOT, 'signatures', 'president_signature.png')
    signature_exists = os.path.isfile(signature_path)
    signature_url = signature_path if signature_exists else None

    # Ajout de la signature dans le contexte
    html_string = render_to_string('acces/demande_pdf_template.html', {
        'demande': demande,
        'president': president,
        'signature_url': signature_url,
    })

    # Générer le PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=demande_{demande_id}.pdf'
    html.write_pdf(target=response)
    return response


@login_required
def save_president_info(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    president = President.objects.first()  # On suppose qu'il n'y a qu'un seul président
    if not president:
        messages.error(request, "Erreur : aucun président n'a été défini.")
        return redirect('acces:demandes_president')

    if request.method == 'POST':
        # Récupère les informations du formulaire
        president.prenom = request.POST.get('prenom')
        president.nom = request.POST.get('nom')
        president.email = request.POST.get('email')
        president.numero = request.POST.get('numero')
        
        # Enregistrement des modifications
        president.save()
        messages.success(request, "Les informations du président ont été mises à jour avec succès.")
        return redirect('acces:demandes_president')

    # Si la méthode n'est pas POST, redirection vers le tableau de bord du président
    return redirect('acces:demandes_president')