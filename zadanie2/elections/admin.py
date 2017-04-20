from django.contrib import admin

from .models import *

admin.site.register(Candidate)
admin.site.register(Voivodeship)
admin.site.register(District)
admin.site.register(Municipality)
admin.site.register(Place)
admin.site.register(Votes)
