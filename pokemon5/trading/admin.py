from django.contrib import admin

from .models import *


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


@admin.register(PokemonType)
class PokemonTypeAdmin(admin.ModelAdmin):
    def trade_evolution_name(self, pokemon_type):
        if pokemon_type.tradeEvolution:
            return pokemon_type.tradeEvolution.name
        else:
            return '-'

    search_fields = ['name']
    list_display = ['id', 'name', 'trade_evolution_name']
    ordering = ['id']


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    def pokemon_type_name(self, pokemon):
        return pokemon.type.name

    list_display = ['pokemon_type_name', 'trainer']
