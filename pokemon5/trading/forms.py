from django import forms

from .models import *


class PokemonTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class AddPokemonForm(forms.Form):
    pokemon_type = PokemonTypeChoiceField(PokemonType.objects.all())
