from django.contrib import admin

from .models import *


@admin.register(Voivodeship)
class VoivodeshipAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id']
    readonly_fields = ['id']


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    list_display = ['id', 'name']
    readonly_fields = ['id']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['address', 'number', 'voivodeship__name', 'district__id', 'municipality__name', 'municipality__id']
    list_display = ['number', 'address', 'voivodeship', 'district', 'municipality']
    fields = ['number', 'address', 'voivodeship', 'district', 'municipality']


class VotesInline(admin.StackedInline):
    model = Votes
    readonly_fields = ['candidate']


@admin.register(Results)
class ResultsAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(ResultsAdmin, self).get_queryset(request)
        qs = qs.filter(place__isnull=False)
        return qs

    def place_number(self, r):
        return r.place.number

    def place_address(self, r):
        return r.place.address

    def _municipality_id(self, r):
        return r.place.municipality.id

    def municipality_name(self, r):
        return r.place.municipality.name

    def _district_id(self, r):
        return r.place.district.id

    def voivodeship_name(self, r):
        return r.place.voivodeship.name

    place_number.admin_order_field = 'place__number'
    place_address.admin_order_field = 'place__address'
    _municipality_id.admin_order_field = 'place__municipality__id'
    municipality_name.admin_order_field = 'place__municipality__name'
    _district_id.admin_order_field = 'place__district__id'
    voivodeship_name.admin_order_field = 'place__voivodeship__name'

    search_fields = ['place__number', 'place__address', 'place__municipality__id',
                     'place__municipality__name', 'place__district__id', 'place__voivodeship__name']
    list_display = ['place_number', 'place_address', '_municipality_id',
                    'municipality_name', '_district_id', 'voivodeship_name']
    fields = ['eligible_voters', 'issued_ballots', 'spoilt_ballots']
    inlines = [VotesInline]

admin.site.register(ProtocolFile)
