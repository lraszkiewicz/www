from django.test import TestCase
from .models import Trainer, Pokemon
import json

class RESTTestCase(TestCase):
    def setUp(self):
        t1 = Trainer(license_number="TST0000001", name="Unit Test1")
        t1.save()
        t2 = Trainer(license_number="TST0000002", name="Unit Test2")
        t2.save()
        t3 = Trainer(license_number="TST0000003", name="Unit Test3")
        t3.save()
        Pokemon(pk=42, trainer=t3, name="Test", status=Pokemon.REGENERATING).save()

    def testStatusTrainerNotFound(self):
        response = self.client.get("/rest/status/XXX0000000/")
        self.assertEqual(response.status_code, 404)

    def testStatusEmpty(self):
        response = self.client.get("/rest/status/TST0000001/")
        self.assertEqual(response.status_code, 200)
        pokemons = json.loads(response.content.decode("utf-8"))
        self.assertEqual(pokemons, [])

    def testStatusOnePokemon(self):
        response = self.client.get("/rest/status/TST0000002/")
        self.assertEqual(response.status_code, 200)
        pokemons = json.loads(response.content.decode("utf-8"))
        self.assertEqual(pokemons, [
            {
                "pk": 42,
                "name": "Test",
                "status": Pokemon.REGENERATING
            }
        ])