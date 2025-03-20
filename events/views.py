from django.shortcuts import render, get_object_or_404, redirect
from .models import Evenement, Participant, Cotisant
from .forms import EvenementForm, ParticipantForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.db import IntegrityError
from django.db.models import Q
import csv


def export_participants_csv(request, soiree_id):
    evenement = Evenement.objects.get(id=soiree_id)
    participants = evenement.participants.all()

    # Créer la réponse HTTP avec en-tête CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="participants_{evenement.nom}.csv"'

    writer = csv.writer(response)
    # Écrire les en-têtes CSV
    writer.writerow(['Nom', 'Prénom', 'Statut'])

    # Écrire les lignes des participants
    for participant in participants:
        if participant.cotisant:
            writer.writerow([participant.cotisant.nom, participant.cotisant.prenom, f"Promotion {participant.cotisant.promotion}"])
        else:
            writer.writerow([participant.nom, participant.prenom, participant.statut])

    return response

def cotisant_autocomplete(request):
    term = request.GET.get('term')
    if term:
        # Diviser le terme en plusieurs mots
        terms = term.split()
        
        # Construire des filtres Q pour chaque combinaison de nom et prénom
        query = Q()
        for t in terms:
            query &= Q(nom__icontains=t) | Q(prenom__icontains=t)
        
        # Filtrer les cotisants selon les termes saisis
        cotisants = Cotisant.objects.filter(query).distinct()
    else:
        cotisants = Cotisant.objects.none()

    results = []
    for cotisant in cotisants:
        results.append({
            'id': cotisant.id,
            'nom': cotisant.nom,
            'prenom': cotisant.prenom,
            'promotion': cotisant.promotion
        })

    return JsonResponse({'results': results})



# def liste_soirees(request):
#     soirees = Evenement.objects.all()
#     return render(request, 'events/liste_soirees.html', {'soirees': soirees})

def liste_soirees(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Si l'utilisateur est un administrateur, récupérer l'historique des soirées
        soirees = Evenement.objects.all().order_by('-date')  # Par exemple, tri par date décroissante
        return render(request, 'events/liste_soirees.html', {'soirees': soirees})
    else:
        # Si l'utilisateur n'est pas un admin, afficher un joli message d'information
        return render(request, 'events/liste_soirees.html')

@login_required
def ajouter_soiree(request):
    # Vérifier si l'utilisateur est administrateur
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour créer une nouvelle soirée.")
        return redirect('events:liste_soirees')  # Redirige vers la liste des soirées ou une autre page

    if request.method == "POST":
        form = EvenementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La soirée a été créée avec succès.")
            return redirect('events:liste_soirees')
    else:
        form = EvenementForm()

    return render(request, 'events/ajouter_soiree.html', {'form': form})



def supprimer_participant(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    soiree_id = participant.evenement.id
    participant.delete()
    messages.success(request, f"{participant.nom or participant.cotisant.nom} {participant.prenom or participant.cotisant.prenom} a été supprimé de l'événement.")
    return redirect('events:detail_soiree', soiree_id=soiree_id)

def detail_soiree(request, soiree_id):
    soiree = get_object_or_404(Evenement, pk=soiree_id)
    now = timezone.now()
    limite_acces = soiree.date + timezone.timedelta(hours=6)

    # Si l'utilisateur est connecté et administrateur, il accède sans identifiant
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        request.session[f'soiree_{soiree.id}_acces'] = True

    # Si l'utilisateur n'est pas connecté, on demande l'identifiant
    elif not request.user.is_authenticated:
        if request.method == "POST" and 'identifiant_verification' in request.POST:
            identifiant_saisi = request.POST.get('identifiant')
            if identifiant_saisi != soiree.identifiant or now > limite_acces:
                messages.error(request, "L'accès à cette soirée a expiré ou l'identifiant est incorrect.")
                return redirect('events:detail_soiree', soiree_id=soiree.id)

            # Enregistrer l'accès validé dans la session
            request.session[f'soiree_{soiree.id}_acces'] = True

        # Vérification de l'accès dans la session
        if not request.session.get(f'soiree_{soiree.id}_acces', False):
            return render(request, 'events/identifiant_verification.html', {'soiree': soiree})

    # Une fois l'accès validé, ou si l'utilisateur est admin, afficher les détails de la soirée
    participants = soiree.participants.all().order_by('cotisant__nom')

    # Compter le nombre total de participants, cotisants et extérieurs
    nombre_cotisants = participants.filter(cotisant__isnull=False).count()
    nombre_exterieurs = participants.filter(cotisant__isnull=True).count()
    nombre_total = participants.count()

    # Gérer l'ajout de cotisants comme extérieurs
    if 'confirm_add_as_exterieur' in request.POST:
        cotisant_id = request.POST.get('cotisant_id')
        cotisant = Cotisant.objects.get(pk=cotisant_id)
        Participant.objects.create(
            evenement=soiree,
            nom=cotisant.nom,
            prenom=cotisant.prenom,
            statut="extérieur"
        )
        messages.success(request, f"{cotisant.nom} {cotisant.prenom} a été ajouté en tant qu'extérieur.")
        return redirect('events:detail_soiree', soiree_id=soiree.id)

    # Gestion du formulaire pour ajouter des participants
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            cotisant = form.cleaned_data['cotisant']
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']

            try:
                # Si un cotisant est sélectionné
                if cotisant:
                    # Vérification si le cotisant est banni
                    if hasattr(cotisant, 'banni') and cotisant.banni.fin_bannissement() > timezone.now():
                        messages.error(request, f"Attention {cotisant.nom} {cotisant.prenom} ne peut pas accéder à la soirée.")
                        return redirect('events:detail_soiree', soiree_id=soiree.id)

                    # Vérification si la date de fin d'adhésion est dépassée
                    if cotisant.fin_adhesion < timezone.now().date():
                        messages.warning(request, f"{cotisant.nom} {cotisant.prenom} n'est plus cotisant. Voulez-vous l'ajouter comme extérieur ?")
                        return render(request, 'events/detail_soiree.html', {
                            'soiree': soiree,
                            'participants': participants,
                            'form': form,
                            'show_confirmation': True,
                            'cotisant': cotisant
                        })
                    else:
                        Participant.objects.create(evenement=soiree, cotisant=cotisant)
                        messages.success(request, f"{cotisant.nom} {cotisant.prenom} a été ajouté à l'événement.")
                        return redirect('events:detail_soiree', soiree_id=soiree.id)

                # Si on ajoute manuellement un participant extérieur
                else:
                    Participant.objects.create(
                        evenement=soiree,
                        nom=nom,
                        prenom=prenom,
                        statut="extérieur"
                    )
                    messages.success(request, f"{nom} {prenom} a été ajouté en tant qu'extérieur.")
                    return redirect('events:detail_soiree', soiree_id=soiree.id)

            except IntegrityError:
                messages.error(request, f"{cotisant.nom if cotisant else nom} {cotisant.prenom if cotisant else prenom} est déjà inscrit à cet événement.")
                return redirect('events:detail_soiree', soiree_id=soiree.id)

    else:
        form = ParticipantForm()

    return render(request, 'events/detail_soiree.html', {
        'soiree': soiree,
        'participants': participants,
        'nombre_cotisants': nombre_cotisants,
        'nombre_exterieurs': nombre_exterieurs,
        'nombre_total': nombre_total,
        'form': form
    })
