import locale

import time

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *


def reverse_voivodeship(v_id):
    return reverse('voivodeship_api', args=[v_id])


def reverse_district(d_id):
    return reverse('district_api', args=[d_id])


def reverse_municipality(m_id):
    return reverse('municipality_api', args=[m_id])


def generate_breadcrumb_voivodeships(place_qs):
    return [(Voivodeship.objects.get(id=v_id).name, reverse_voivodeship(v_id))
            for v_id, in place_qs.values_list('voivodeship').distinct()]


def generate_breadcrumb_districts(place_qs):
    return [('okręg nr {}'.format(d_id), reverse_district(d_id))
            for d_id, in place_qs.values_list('district').distinct()]


def index(request):
    return render(request, 'elections/base.html')


def results_to_dict(results_obj):
    return {
        'eligible_voters': results_obj.eligible_voters,
        'issued_ballots': results_obj.issued_ballots,
        'spoilt_ballots': results_obj.spoilt_ballots
    }


def votes_qs_to_dict(votes_qs):
    return [
        {
            'name': str(v.candidate),
            'votes': v.amount
        }
        for v in votes_qs.order_by('candidate__id')]


def country_api(request):
    return JsonResponse({
        'type': 'country',
        'title': 'Polska',
        'breadcrumb': ['Polska'],
        'results_title': 'Polsce',
        'children_title': 'województwach',
        'stats_here': Results.objects.filter(voivodeship__isnull=False).aggregate(
            eligible_voters=Sum('eligible_voters'),
            issued_ballots=Sum('issued_ballots'),
            spoilt_ballots=Sum('spoilt_ballots')
        ),
        'results_here': [
            {
                'name': str(c),
                'votes': Votes.objects.filter(
                    parent__voivodeship__isnull=False, candidate=c
                ).aggregate(Sum('amount'))['amount__sum']
            }
            for c in Candidate.objects.all().order_by('id')
        ],
        'candidates': list(Candidate.objects.all().order_by('id').values('first_name', 'last_name')),
        'children': list(Voivodeship.objects.all().order_by('id').values('id', 'name')),
        'children_stats': list(Results.objects.filter(voivodeship__isnull=False).order_by('voivodeship__id')
                               .values('eligible_voters', 'issued_ballots', 'spoilt_ballots')),
        'children_votes': list(Votes.objects.filter(parent__voivodeship__isnull=False)
                               .order_by('parent__voivodeship__id', 'candidate__id').values('amount')),
        'is_authenticated': request.user.is_authenticated(),
        'username': request.user.username
    })


def voivodeship_api(request, v_id):
    v = get_object_or_404(Voivodeship, id=v_id)
    children = list(Place.objects.filter(voivodeship=v)
                    .values('district__id').distinct().order_by('district__id'))
    children_ids = [d['district__id'] for d in children]
    return JsonResponse({
        'type': 'voivodeship',
        'title': str(v),
        'breadcrumb': [[('Polska', reverse('country_api'))], v.name],
        'results_title': 'województwie',
        'children_title': 'okręgach',
        'stats_here': results_to_dict(Results.objects.get(voivodeship=v)),
        'results_here': votes_qs_to_dict(Votes.objects.filter(parent__voivodeship=v)),
        'candidates': list(Candidate.objects.all().order_by('id').values('first_name', 'last_name')),
        'children': children,
        'children_stats': list(Results.objects.filter(district__id__in=children_ids).order_by('district__id')
                               .values('eligible_voters', 'issued_ballots', 'spoilt_ballots')),
        'children_votes': list(Votes.objects.filter(parent__district__id__in=children_ids)
                               .order_by('parent__district__id', 'candidate__id').values('amount')),
        'is_authenticated': request.user.is_authenticated(),
        'username': request.user.username
    })


def district_api(request, d_id):
    d = get_object_or_404(District, id=d_id)
    children = list(Place.objects.filter(district=d)
                    .values('municipality__id', 'municipality__name').distinct().order_by('municipality__id'))
    children_ids = [m['municipality__id'] for m in children]
    return JsonResponse({
        'type': 'district',
        'title': str(d),
        'breadcrumb': [
            [('Polska', reverse('country_api'))],
            generate_breadcrumb_voivodeships(Place.objects.filter(district=d)),
            'okręg nr {}'.format(d_id)
        ],
        'results_title': 'okręgu',
        'children_title': 'gminach',
        'stats_here': results_to_dict(Results.objects.get(district=d)),
        'results_here': votes_qs_to_dict(Votes.objects.filter(parent__district=d)),
        'candidates': list(Candidate.objects.all().order_by('id').values('first_name', 'last_name')),
        'children': children,
        'children_stats': list(Results.objects.filter(municipality__id__in=children_ids)
                               .order_by('municipality__id')
                               .values('eligible_voters', 'issued_ballots', 'spoilt_ballots')),
        'children_votes': list(Votes.objects.filter(parent__municipality__id__in=children_ids)
                               .order_by('parent__municipality__id', 'candidate__id').values('amount')),
        'is_authenticated': request.user.is_authenticated(),
        'username': request.user.username
    })


def municipality_api(request, m_id):
    m = get_object_or_404(Municipality, id=m_id)
    return JsonResponse({
        'type': 'municipality',
        'title': str(m),
        'breadcrumb': [
            [('Polska', reverse('country_api'))],
            generate_breadcrumb_voivodeships(Place.objects.filter(municipality=m)),
            generate_breadcrumb_districts(Place.objects.filter(municipality=m)),
            m.name
        ],
        'results_title': 'gminie',
        'children_title': 'okręgach',
        'stats_here': results_to_dict(Results.objects.get(municipality=m)),
        'results_here': votes_qs_to_dict(Votes.objects.filter(parent__municipality=m)),
        'candidates': list(Candidate.objects.all().order_by('id').values('first_name', 'last_name')),
        'children': list(Place.objects.filter(municipality=m).order_by('number').values('number', 'address', 'id')),
        'children_stats': list(Results.objects.filter(place__municipality=m).order_by('place__number')
                               .values('eligible_voters', 'issued_ballots', 'spoilt_ballots')),
        'children_votes': list(Votes.objects.filter(parent__place__municipality=m)
                               .order_by('parent__place__number', 'candidate__id').values('amount')),
        'is_authenticated': request.user.is_authenticated(),
        'username': request.user.username
    })


def place(request, p_id):
    render(request, "")
    # p = get_object_or_404(Place, id=p_id)
    #
    # if request.method == 'POST' and 'results_form' in request.POST and request.user.is_authenticated:
    #     results_form = PlaceEditForm(request.POST, place=p)
    #     if results_form.is_valid():
    #         p.eligible_voters = int(results_form.cleaned_data['eligible_voters'])
    #         p.issued_ballots = int(results_form.cleaned_data['issued_ballots'])
    #         p.spoilt_ballots = int(results_form.cleaned_data['spoilt_ballots'])
    #         p.save()
    #         for c in Candidate.objects.all():
    #             v = Votes.objects.get(candidate=c, place=p)
    #             v.amount = results_form.cleaned_data['candidate_{}'.format(c.id)]
    #             v.save()
    #         return redirect(reverse_municipality(p.municipality.id))
    # else:
    #     results_form = PlaceEditForm(place=p)
    #
    # if request.method == 'POST' and 'file_form' in request.POST:
    #     file_form = ProtocolUploadForm(request.POST, request.FILES)
    #     if file_form.is_valid():
    #         instance = ProtocolFile(place=p, file=request.FILES['file'])
    #         instance.save()
    #         p.next_protocol_number += 1
    #         p.save()
    #         return redirect(reverse(place, args=[p_id]))
    # else:
    #     file_form = ProtocolUploadForm()
    #
    # if request.user.is_authenticated:
    #     results_here, stats_here = None, None
    # else:
    #     results_here, stats_here = generate_results_here(Place.objects.filter(id=p_id))
    #
    # return render(request, 'elections/place.html', {
    #     'results_form': results_form,
    #     'file_form': file_form,
    #     'breadcrumb': [
    #         [('Polska', reverse('index'))],
    #         generate_breadcrumb_voivodeships(Place.objects.filter(id=p_id)),
    #         generate_breadcrumb_districts(Place.objects.filter(id=p_id)),
    #         [(p.municipality.name, reverse_municipality(p.municipality.id))],
    #         'Obwód nr {} - {}'.format(p.number, p.address)
    #     ],
    #     'p_id': p_id,
    #     'protocols': [(f.file.url, os.path.basename(f.file.name), reverse('delete_file', args=[f.id]))
    #                   for f in ProtocolFile.objects.filter(place=p)],
    #     'results_here': results_here,
    #     'stats_here': stats_here
    # })


def delete_file(request, f_id):
    f = get_object_or_404(ProtocolFile, id=f_id)
    p = f.place
    if request.user.is_authenticated:
        f.file.delete()
        f.delete()
    return redirect(reverse('place', args=[p.id]))


def search_api(request):
    q = request.GET.get('q')
    if not q:
        return HttpResponseBadRequest()
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    results = []
    for m in Municipality.objects.filter(name__icontains=q):
        results.append(('{} ({}) - {} - {}'.format(
            m.name,
            m.id,
            ', '.join([x[0] for x in generate_breadcrumb_districts(Place.objects.filter(municipality=m))]),
            ', '.join([x[0] for x in generate_breadcrumb_voivodeships(Place.objects.filter(municipality=m))]),
        ), reverse_municipality(m.id)))
    return JsonResponse({
        'type': 'search_results',
        'query': q,
        'search_results': sorted(results, key=lambda x: locale.strxfrm(x[0]))
    })


@csrf_exempt
def login_api(request):
    success = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                success = True
        return JsonResponse({
            'success': success,
            'is_authenticated': request.user.is_authenticated(),
            'username': request.user.username
        })
    return HttpResponseBadRequest()


@csrf_exempt
def logout_api(request):
    logout(request)
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated(),
        'username': request.user.username
    })
