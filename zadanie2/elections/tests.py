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
