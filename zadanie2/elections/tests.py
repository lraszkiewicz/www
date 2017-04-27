from bs4 import BeautifulSoup

from django.test import TestCase
from django.contrib.auth.models import User

from .models import *


def search_results(html):
    parsed_html = BeautifulSoup(html, 'lxml')
    return parsed_html\
        .find('div', attrs={'class': 'list-group'})\
        .find_all('a')


class SearchTest(TestCase):
    def setUp(self):
        Municipality(id='123456', name='Abcdef').save()
        Municipality(id='654321', name='Qwerty').save()

    def testSearch(self):
        r = search_results(self.client.get('/wybory/search/?q=abc').content)
        assert(len(r) == 1)
        assert('Abcdef' in r[0].text)
        assert('123456' in r[0]['href'])
        r = search_results(self.client.get('/wybory/search/?q=er').content)
        assert(len(r) == 1)
        assert('Qwerty' in r[0].text)
        assert('654321' in r[0]['href'])
        r = search_results(self.client.get('/wybory/search/?q=E').content)
        assert(len(r) == 2)


class PlaceEditTest(TestCase):
    def setUp(self):
        c = Candidate(first_name='Janusz', last_name='Korwin-Mikke')
        c.save()
        v = Voivodeship(name='mazowieckie')
        v.save()
        d = District(id=1)
        d.save()
        m = Municipality(id='123456', name='Warszawa')
        m.save()
        p = Place(
            number=1,
            address='Banacha 2',
            voivodeship=v,
            district_id=d.id,
            municipality=m,
            eligible_voters=323,
            issued_ballots=300,
            spoilt_ballots=42
        )
        p.save()
        Votes(amount=100, candidate=c, place=p).save()
        User(username='admin', password='admin').save()

    def testEdit(self):
        self.client.force_login(user=User.objects.first())
        c = Candidate.objects.first()
        self.client.post(
            '/wybory/obwod/{}/'.format(Place.objects.first().id),
            {'results_form': '',
             'eligible_voters': 400,
             'issued_ballots': 300,
             'spoilt_ballots': 50,
             'candidate_{}'.format(c.id): 101}
        )
        p = Place.objects.first()
        v = Votes.objects.get(place=p, candidate=c)
        assert(p.eligible_voters == 400)
        assert(p.issued_ballots == 300)
        assert(p.spoilt_ballots == 50)
        assert(v.amount == 101)
        self.client.post(
            '/wybory/obwod/{}/'.format(Place.objects.first().id),
            {'results_form': '',
             'eligible_voters': 400,
             'issued_ballots': 500,
             'spoilt_ballots': 50,
             'candidate_{}'.format(c.id): 101}
        )
        p = Place.objects.first()
        assert(p.issued_ballots != 500)


def results_and_stats(html):
    parsed_html = BeautifulSoup(html, 'lxml')
    results = parsed_html.find_all('table')[0]
    stats = parsed_html.find_all('table')[1]
    results = [int(r.find_all('td')[0].text) for r in results.find_all('tr')]
    stats = [int(r.find('td').text) for r in stats.find_all('tr')[:-1]]
    return results + stats


class ViewTest(TestCase):
    def setUp(self):
        c = Candidate(first_name='Janusz', last_name='Korwin-Mikke')
        c.save()
        v = Voivodeship(name='mazowieckie')
        v.save()
        d = District(id=1)
        d.save()
        m = Municipality(id='123456', name='Warszawa')
        m.save()
        p = Place(
            number=1,
            address='Banacha 2',
            voivodeship=v,
            district_id=d.id,
            municipality=m,
            eligible_voters=323,
            issued_ballots=300,
            spoilt_ballots=42
        )
        p.save()
        Votes(amount=100, candidate=c, place=p).save()
        User(username='admin', password='admin').save()

    def testResults(self):
        v = Voivodeship.objects.first()
        d = District.objects.first()
        m = Municipality.objects.first()
        correct_results_and_stats = [100, 323, 300, 142, 100, 42]
        ras = results_and_stats(self.client.get('/wybory/').content)
        assert(ras == correct_results_and_stats)
        ras = results_and_stats(
            self.client.get('/wybory/wojewodztwo/mazowieckie-{}/'.format(v.id)).content)
        assert(ras == correct_results_and_stats)
        ras = results_and_stats(
            self.client.get('/wybory/okreg/{}/'.format(d.id)).content)
        assert(ras == correct_results_and_stats)
        ras = results_and_stats(
            self.client.get('/wybory/gmina/warszawa-{}/'.format(m.id)).content)
        assert(ras == correct_results_and_stats)
