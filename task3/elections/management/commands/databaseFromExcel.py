import os
import xlrd
import locale

from django.core.management.base import BaseCommand
from django.db.models import Sum

from elections.models import *
from collections import defaultdict


class Command(BaseCommand):
    def handle(self, *args, **options):
        locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

        results_dir = './results'  # for election results

        # generated by zadanie1/voievodeships.py
        voievodeship_of_district = {
            1: 'dolnośląskie', 2: 'dolnośląskie', 3: 'dolnośląskie', 4: 'dolnośląskie', 5: 'kujawsko-pomorskie',
            6: 'kujawsko-pomorskie', 7: 'kujawsko-pomorskie', 8: 'lubelskie', 9: 'lubelskie', 10: 'lubelskie', 11: 'lubelskie',
            12: 'lubelskie', 13: 'lubuskie', 14: 'lubuskie', 15: 'łódzkie', 16: 'łódzkie', 17: 'łódzkie', 18: 'łódzkie',
            19: 'łódzkie', 20: 'małopolskie', 21: 'małopolskie', 22: 'małopolskie', 23: 'małopolskie', 24: 'małopolskie',
            25: 'małopolskie', 26: 'małopolskie', 27: 'małopolskie', 28: 'mazowieckie', 29: 'mazowieckie', 30: 'mazowieckie',
            31: 'mazowieckie', 32: 'mazowieckie', 33: 'mazowieckie', 34: 'mazowieckie', 35: 'mazowieckie', 36: 'mazowieckie',
            37: 'opolskie', 38: 'opolskie', 39: 'podkarpackie', 40: 'podkarpackie', 41: 'podkarpackie', 42: 'podkarpackie',
            43: 'podlaskie', 44: 'podlaskie', 45: 'podlaskie', 46: 'pomorskie', 47: 'pomorskie', 48: 'pomorskie', 49: 'śląskie',
            50: 'śląskie', 51: 'śląskie', 52: 'śląskie', 53: 'śląskie', 54: 'śląskie', 55: 'świętokrzyskie',
            56: 'świętokrzyskie', 57: 'warmińsko-mazurskie', 58: 'warmińsko-mazurskie', 59: 'warmińsko-mazurskie',
            60: 'wielkopolskie', 61: 'wielkopolskie', 62: 'wielkopolskie', 63: 'wielkopolskie', 64: 'wielkopolskie',
            65: 'zachodniopomorskie', 66: 'zachodniopomorskie', 67: 'zachodniopomorskie', 68: 'zachodniopomorskie'
        }

        voievodeships = defaultdict(set)  # województwa
        districts = defaultdict(set)  # okręgi wyborcze
        municipalities = {}  # gminy

        candidates = []
        stats = []

        if os.path.isdir(results_dir):
            for f in os.listdir(results_dir):
                if f.startswith('obw') and f.endswith('.xls'):
                    sheet = xlrd.open_workbook(os.path.join(results_dir, f)).sheet_by_index(0)
                    headers = [cell.value.replace('\n', ' ') for cell in sheet.row(0)]
                    if not candidates:
                        candidates = headers[headers.index('Głosy ważne') + 1:]
                    if not stats:
                        stats = headers[headers.index('Uprawnieni'):headers.index('Głosy ważne')+1]
                    for row in list(sheet.get_rows())[1:]:
                        row = [cell.value for cell in row]
                        for i in range(headers.index('Uprawnieni'), len(headers)):
                            row[i] = int(row[i])
                        row = dict(zip(headers, row))
                        row['Nr okr.'] = int(row['Nr okr.'])
                        row['Nr obw.'] = int(row['Nr obw.'])
                        voievodeships[voievodeship_of_district[row['Nr okr.']]].add(row['Nr okr.'])
                        districts[row['Nr okr.']].add((row['Kod gminy'], row['Gmina']))
                        if not row['Kod gminy'] in municipalities:
                            municipalities[row['Kod gminy']] = (row['Gmina'], [])
                        municipalities[row['Kod gminy']][1].append(row)
        else:
            print('Directory {} does not exist.'.format(results_dir))
            return

        Candidate.objects.all().delete()
        Voivodeship.objects.all().delete()
        District.objects.all().delete()
        Municipality.objects.all().delete()
        Place.objects.all().delete()
        Votes.objects.all().delete()

        candidates2 = [
            ('Dariusz Maciej', 'Grabowski'),
            ('Piotr', 'Ikonowicz'),
            ('Jarosław', 'Kalinowski'),
            ('Janusz', 'Korwin-Mikke'),
            ('Marian', 'Krzaklewski'),
            ('Aleksander', 'Kwaśniewski'),
            ('Andrzej', 'Lepper'),
            ('Jan', 'Łopuszański'),
            ('Andrzej Marian', 'Olechowski'),
            ('Bogdan', 'Pawłowski'),
            ('Lech', 'Wałęsa'),
            ('Tadeusz Adam', 'Wilecki')
        ]

        for c in candidates2:
            Candidate(first_name=c[0], last_name=c[1]).save()

        v_set = set()
        d_set = set()
        m_set = set()
        places = []
        for v in voievodeships:
            v_set.add(v)
            for d in sorted(voievodeships[v]):
                d_set.add(d)
                for m_id, m_name in districts[d]:
                    m_set.add((m_id, m_name))
                    for row in municipalities[m_id][1]:
                        places.append((row, v))

        print('Przetwarzam kandydatów')
        candidate_map = {}
        for c in Candidate.objects.all():
            candidate_map['{} {}'.format(c.first_name, c.last_name.upper())] = c

        print('Tworzę i dodaję województwa')
        Voivodeship.objects.bulk_create([Voivodeship(name=x) for x in sorted(v_set, key=lambda y: locale.strxfrm(y))])
        print('Tworzę i dodaję okręgi')
        District.objects.bulk_create([District(id=x) for x in sorted(d_set)])
        print('Tworzę i dodaję gminy')
        Municipality.objects.bulk_create([Municipality(id=x[0], name=x[1]) for x in sorted(m_set)])

        print('Tworzę obwody')
        place_objects = []
        place_map = {}
        for a in sorted(places, key=lambda x: (x[0]['Kod gminy'], x[0]['Nr obw.'])):
            t = (a[0]['Nr obw.'], District.objects.filter(id=a[0]['Nr okr.']).first(), Municipality.objects.filter(id=a[0]['Kod gminy']).first())
            if t not in place_map:
                place_objects.append(Place(
                    number=a[0]['Nr obw.'],
                    address=a[0]['Adres'],
                    voivodeship=Voivodeship.objects.filter(name=a[1]).first(),
                    district=District.objects.filter(id=a[0]['Nr okr.']).first(),
                    municipality=Municipality.objects.filter(id=a[0]['Kod gminy']).first()
                ))
            place_map[t] = True
        print('Dodaję obwody')
        Place.objects.bulk_create(place_objects)
        print('Tworzę wyniki dla obwodów')
        results_objects = []
        place_map = {}
        for a in sorted(places, key=lambda x: (x[0]['Kod gminy'], x[0]['Nr obw.'])):
            place = Place.objects.get(
                number=a[0]['Nr obw.'],
                municipality=Municipality.objects.get(id=a[0]['Kod gminy']),
                district=District.objects.get(id=a[0]['Nr okr.'])
            )
            t = (a[0]['Nr obw.'], District.objects.filter(id=a[0]['Nr okr.']).first(), Municipality.objects.filter(id=a[0]['Kod gminy']).first())
            if t not in place_map:
                results_objects.append(Results(
                    place=place,
                    eligible_voters=a[0]['Uprawnieni'],
                    issued_ballots=a[0]['Wydane karty'],
                    spoilt_ballots=a[0]['Głosy nieważne']
                ))
            place_map[t] = True
        print('Dodaję wyniki dla obwodów')
        Results.objects.bulk_create(results_objects)
        print('Tworzę głosy dla obwodów')
        vote_objects = []
        votes_map = {}
        it = 0
        places_count = Place.objects.all().count()
        for a in sorted(places, key=lambda x: (x[0]['Kod gminy'], x[0]['Nr obw.'])):
            if it % 250 == 0:
                print('{}/{}'.format(it, places_count))
            it += 1
            for c in candidate_map:
                place = Place.objects.get(
                    number=a[0]['Nr obw.'],
                    municipality=Municipality.objects.filter(id=a[0]['Kod gminy']).first(),
                    district=District.objects.filter(id=a[0]['Nr okr.']).first()
                )
                results = Results.objects.get(place=place)
                t = (place, candidate_map[c])
                if t not in votes_map:
                    vote_objects.append(Votes(
                        amount=a[0][c],
                        candidate=candidate_map[c],
                        parent=results
                    ))
                    votes_map[t] = True
        print('Dodaję głosy dla obwodów')
        Votes.objects.bulk_create(vote_objects)

        print('Tworzę wyniki dla województw, okręgów, gmin')
        results_objects = []
        for v in Voivodeship.objects.all():
            r = Results.objects.filter(place__voivodeship=v).aggregate(
                eli=Sum('eligible_voters'),
                iss=Sum('issued_ballots'),
                spo=Sum('spoilt_ballots')
            )
            results_objects.append(Results(
                voivodeship=v,
                eligible_voters=r['eli'],
                issued_ballots=r['iss'],
                spoilt_ballots=r['spo']
            ))
        for d in District.objects.all():
            r = Results.objects.filter(place__district=d).aggregate(
                eli=Sum('eligible_voters'),
                iss=Sum('issued_ballots'),
                spo=Sum('spoilt_ballots')
            )
            results_objects.append(Results(
                district=d,
                eligible_voters=r['eli'],
                issued_ballots=r['iss'],
                spoilt_ballots=r['spo']
            ))
        for m in Municipality.objects.all():
            r = Results.objects.filter(place__municipality=m).aggregate(
                eli=Sum('eligible_voters'),
                iss=Sum('issued_ballots'),
                spo=Sum('spoilt_ballots')
            )
            results_objects.append(Results(
                municipality=m,
                eligible_voters=r['eli'],
                issued_ballots=r['iss'],
                spoilt_ballots=r['spo']
            ))
        print('Dodaję wyniki dla województw, okręgów, gmin')
        Results.objects.bulk_create(results_objects)
        print('Tworzę głosy dla województw, okręgów, gmin')
        votes_objects = []

        for v in Voivodeship.objects.all():
            for c in Candidate.objects.all():
                agg = Votes.objects.filter(parent__place__voivodeship=v, candidate=c).aggregate(
                    s=Sum('amount')
                )
                votes_objects.append(Votes(
                    amount=agg['s'],
                    candidate=c,
                    parent=Results.objects.get(voivodeship=v)
                ))
        for d in District.objects.all():
            for c in Candidate.objects.all():
                agg = Votes.objects.filter(parent__place__district=d, candidate=c).aggregate(
                    s=Sum('amount')
                )
                votes_objects.append(Votes(
                    amount=agg['s'],
                    candidate=c,
                    parent=Results.objects.get(district=d)
                ))
        for m in Municipality.objects.all():
            for c in Candidate.objects.all():
                agg = Votes.objects.filter(parent__place__municipality=m, candidate=c).aggregate(
                    s=Sum('amount')
                )
                votes_objects.append(Votes(
                    amount=agg['s'],
                    candidate=c,
                    parent=Results.objects.get(municipality=m)
                ))
        print('Dodaję głosy dla województw, okręgów, gmin')
        Votes.objects.bulk_create(votes_objects)

