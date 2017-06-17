from django.http import HttpResponse
from django.views.decorators.http import require_GET
import json
from .models import Trainer, Pokemon

@require_GET
def status(request, license_number):
    trainer = Trainer.objects.get(license_number=license_number)
    pokemons = trainer.pokemon_set.values("pk", "name", "status")
    pokemons_json = json.dumps(list(pokemons))
    response = HttpResponse(pokemons_json, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response