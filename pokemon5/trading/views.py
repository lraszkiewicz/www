import json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponse

from .models import *
from .forms import *


def main(request):
    return render(request, 'main.html', {
        'trainers': Trainer.objects.all()
    })


def trainer(request, trainer_pk):
    t = get_object_or_404(Trainer, pk=trainer_pk)
    if request.method == 'POST':
        form = AddPokemonForm(request.POST)
        if form.is_valid():
            Pokemon.objects.create(type=form.cleaned_data['pokemon_type'],
                                   trainer=t)
            return redirect('trainer', trainer_pk=trainer_pk)
    else:
        form = AddPokemonForm()
    return render(request, 'trainer.html', {
        'trainer': t,
        'pokemons': t.pokemon_set.all(),
        'add_pokemon_form': form
    })


@csrf_exempt
@require_POST
def tradeAPI(request):
    if len(request.POST) != 2 or 'pokemon1' not in request.POST or 'pokemon2' not in request.POST:
        return HttpResponseForbidden()

    try:
        pokemon1 = Pokemon.objects.get(pk=request.POST['pokemon1'])
        pokemon2 = Pokemon.objects.get(pk=request.POST['pokemon2'])
    except Pokemon.DoesNotExist:
        return HttpResponseForbidden()

    if pokemon1.trainer == pokemon2.trainer:
        return HttpResponseForbidden()

    response_dict = {
        'evolved1': 0,
        'evolved2': 0
    }

    trainer1 = pokemon1.trainer
    trainer2 = pokemon2.trainer
    pokemon1.trainer = trainer2
    pokemon2.trainer = trainer1

    if pokemon1.type.tradeEvolution:
        pokemon1.type = pokemon1.type.tradeEvolution
        response_dict['evolved1'] = 1
    if pokemon2.type.tradeEvolution:
        pokemon2.type = pokemon2.type.tradeEvolution
        response_dict['evolved2'] = 1

    pokemon1.save()
    pokemon2.save()

    response = HttpResponse(json.dumps(response_dict), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response
