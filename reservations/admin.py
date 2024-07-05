from django.contrib import admin
from .models import Location, Court, Reservation

admin.site.register(Location)
admin.site.register(Court)
admin.site.register(Reservation)
