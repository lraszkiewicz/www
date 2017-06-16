from django.contrib import admin

from .models import *


class ResultsAdmin(admin.ModelAdmin):
    fields = ['eligible_voters', 'issued_ballots', 'spoilt_ballots']


class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['address', 'number', 'voivodeship__name', 'district__id', 'municipality__name', 'municipality__id']
    list_display = ['number', 'address', 'voivodeship', 'district', 'municipality']
    fields = ['number', 'address', 'voivodeship', 'district', 'municipality']


admin.site.register(Candidate)
admin.site.register(Voivodeship)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Votes)
admin.site.register(ProtocolFile)
admin.site.register(Results, ResultsAdmin)
