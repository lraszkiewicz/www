from django.test import TestCase

from .models import *


class EmptyDatabaseTestCase(TestCase):
    def testEmpty(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class MainPageTestCase(TestCase):
    def setUp(self):
        Trainer.objects.create(name='Ash Ketchum')
        Trainer.objects.create(name='Gary Oak')

    def testMainPage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['trainers']), 2)


class TrainerPageTestCase(TestCase):
    def setUp(self):
        trainer = Trainer.objects.create(name='Samuel Oak')
        type1 = PokemonType.objects.create(id=1, name='Bulbasaur', tradeEvolution=None)
        type2 = PokemonType.objects.create(id=2, name='Ivysaur', tradeEvolution=None)
        Pokemon.objects.create(type=type1, trainer=trainer)
        Pokemon.objects.create(type=type2, trainer=trainer)

    def testTrainerPage(self):
        response = self.client.get('/trainer/{}/'.format(Trainer.objects.first().pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pokemons']), 2)
