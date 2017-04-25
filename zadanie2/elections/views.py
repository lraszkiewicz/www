import locale

from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from slugify import slugify

from .models import *
from .forms import *


def generate_results_here(place_qs):
    votes_qs = Votes.objects.filter(place__in=place_qs)
    all_votes = votes_qs.aggregate(Sum('amount'))['amount__sum']
    results_here = []
    for c in Candidate.objects.all():
        votes = votes_qs.filter(candidate=c).aggregate(Sum('amount'))['amount__sum']
        results_here.append({
            'name': str(c),
            'votes': votes,
            'result': votes / all_votes,
            'result_percent': 100.0 * votes / all_votes
        })

    stats_here = place_qs.aggregate(
        eligible_voters=Sum('eligible_voters'),
        issued_ballots=Sum('issued_ballots'),
        spoilt_ballots=Sum('spoilt_ballots')
    )
    stats_here['valid_ballots'] = all_votes
    stats_here['casted_ballots'] = stats_here['valid_ballots'] + stats_here['spoilt_ballots']
    stats_here['turnout'] = stats_here['casted_ballots'] / stats_here['eligible_voters']
    stats_here['turnout_percent'] = 100.0 * stats_here['turnout']

    return results_here, stats_here


def generate_child_results(place_qs):
    results, stats = generate_results_here(place_qs)
    return [
        stats['eligible_voters'], stats['issued_ballots'],
        stats['casted_ballots'], stats['valid_ballots'],
        stats['spoilt_ballots']
    ] + [
        x['votes'] for x in results
    ]


def reverse_voivodeship(v_id):
    return reverse('voivodeship', args=[slugify('{}-{}'.format(Voivodeship.objects.get(id=v_id).name, v_id))])


def reverse_municipality(m_id):
    return reverse('municipality', args=[slugify('{}-{}'.format(Municipality.objects.get(id=m_id).name, m_id))])


def generate_breadcrumb_voivodeships(place_qs):
    return [(Voivodeship.objects.get(id=v_id).name, reverse_voivodeship(v_id))
            for v_id, in place_qs.values_list('voivodeship').distinct()]


def generate_breadcrumb_districts(place_qs):
    return [('okręg nr {}'.format(d_id), reverse('district', args=[d_id]))
            for d_id, in place_qs.values_list('district').distinct()]


def index(request):
    results_here, stats_here = generate_results_here(Place.objects.all())
    children_results = []
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    for v in sorted(Voivodeship.objects.all(), key=lambda x: locale.strxfrm(x.name)):
        children_results.append([(v.name, reverse_voivodeship(v.id))]
                                + generate_child_results(Place.objects.filter(voivodeship=v)))
    return render(request, 'elections/index.html', {
        'title': 'Polska',
        'breadcrumb': ['Polska'],
        'candidates': [str(c) for c in Candidate.objects.all()],
        'results_here': results_here,
        'stats_here': stats_here,
        'children_results': children_results,
        'map_data': [(v[0][0], slugify(v[0][0]), v[0][1], v[2] / v[1]) for v in children_results]
    })


def voivodeship(request, v_id):
    v = get_object_or_404(Voivodeship, id=v_id)
    results_here, stats_here = generate_results_here(Place.objects.filter(voivodeship=v))
    districts = sorted(Place.objects.filter(voivodeship=v).values_list('district').distinct())
    children_results = []
    for d_id, in districts:
        d = District.objects.get(id=d_id)
        children_results.append([(str(d), reverse('district', args=[d_id]))]
                                + generate_child_results(Place.objects.filter(district=d)))
    return render(request, 'elections/voivodeship.html', {
        'title': str(v),
        'breadcrumb': [[('Polska', reverse('index'))], v.name],
        'candidates': [str(c) for c in Candidate.objects.all()],
        'results_here': results_here,
        'stats_here': stats_here,
        'children_results': children_results
    })


def district(request, d_id):
    d = get_object_or_404(District, id=d_id)
    results_here, stats_here = generate_results_here(Place.objects.filter(district=d))
    municipalities = Place.objects.filter(district=d).values_list('municipality').distinct()
    children_results = []
    for m_id, in municipalities:
        m = Municipality.objects.get(id=m_id)
        children_results.append([(m.name, reverse_municipality(m_id))]
                                + generate_child_results(Place.objects.filter(municipality=m)))
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    children_results = sorted(children_results, key=lambda x: locale.strxfrm(x[0][0]))
    return render(request, 'elections/district.html', {
        'title': str(d),
        'breadcrumb': [
            [('Polska', reverse('index'))],
            generate_breadcrumb_voivodeships(Place.objects.filter(district=d)),
            'okręg nr {}'.format(d_id)
        ],
        'candidates': [str(c) for c in Candidate.objects.all()],
        'results_here': results_here,
        'stats_here': stats_here,
        'children_results': children_results
    })


def municipality(request, m_id):
    m = get_object_or_404(Municipality, id=m_id)
    results_here, stats_here = generate_results_here(Place.objects.filter(municipality=m))
    children_results = [(([(p.number, p.address, reverse(place, args=[p.id]))])
                         + generate_child_results(Place.objects.filter(id=p.id)))
                        for p in Place.objects.filter(municipality=m)]
    return render(request, 'elections/municipality.html', {
        'title': str(m),
        'breadcrumb': [
            [('Polska', reverse('index'))],
            generate_breadcrumb_voivodeships(Place.objects.filter(municipality=m)),
            generate_breadcrumb_districts(Place.objects.filter(municipality=m)),
            m.name
        ],
        'candidates': [str(c) for c in Candidate.objects.all()],
        'results_here': results_here,
        'stats_here': stats_here,
        'children_results': children_results
    })


def place(request, p_id):
    p = get_object_or_404(Place, id=p_id)

    if request.method == 'POST' and 'results_form' in request.POST:
        results_form = PlaceEditForm(request.POST, place=p)
        if results_form.is_valid():
            p.eligible_voters = int(results_form.cleaned_data['eligible_voters'])
            p.issued_ballots = int(results_form.cleaned_data['issued_ballots'])
            p.spoilt_ballots = int(results_form.cleaned_data['spoilt_ballots'])
            p.save()
            for c in Candidate.objects.all():
                v = Votes.objects.get(candidate=c, place=p)
                v.amount = results_form.cleaned_data['candidate_{}'.format(c.id)]
                v.save()
            return redirect(reverse_municipality(p.municipality.id))
    else:
        results_form = PlaceEditForm(place=p)

    if request.method == 'POST' and 'file_form' in request.POST:
        file_form = ProtocolUploadForm(request.POST, request.FILES)
        if file_form.is_valid():
            instance = ProtocolFile(place=p, file=request.FILES['file'])
            instance.save()
            return redirect(reverse(place, args=[p_id]))
    else:
        file_form = ProtocolUploadForm()

    return render(request, 'elections/place.html', {
        'results_form': results_form,
        'file_form': file_form,
        'breadcrumb': [
            [('Polska', reverse('index'))],
            generate_breadcrumb_voivodeships(Place.objects.filter(id=p_id)),
            generate_breadcrumb_districts(Place.objects.filter(id=p_id)),
            [(p.municipality.name, reverse_municipality(p.municipality.id))],
            'Obwód nr {} - {}'.format(p.number, p.address)
        ],
        'p_id': p_id,
        'protocols': [(f.file.url, os.path.basename(f.file.name), reverse('delete_file', args=[f.id]))
                      for f in ProtocolFile.objects.filter(place=p)]
    })


def delete_file(request, f_id):
    f = get_object_or_404(ProtocolFile, id=f_id)
    p = f.place
    f.file.delete()
    f.delete()
    return redirect(reverse('place', args=[p.id]))


def search(request):
    q = request.GET.get('q')
    if not q:
        return redirect(index)
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    results = []
    for m in Municipality.objects.filter(name__icontains=q):
        results.append(('{} ({}) - {} - {}'.format(
            m.name,
            m.id,
            ', '.join([x[0] for x in generate_breadcrumb_districts(Place.objects.filter(municipality=m))]),
            ', '.join([x[0] for x in generate_breadcrumb_voivodeships(Place.objects.filter(municipality=m))]),
        ), reverse_municipality(m.id)))
    return render(request, 'elections/search.html', {
        'q': q,
        'search_results': sorted(results, key=lambda x: locale.strxfrm(x[0]))
    })


def login(request, *args, **kwargs):
    return LoginView.as_view(**kwargs)(request, *args, **kwargs)
