# acces/admin.py

from django.contrib import admin
from .models import President, Club, Local, Demande, Ticket

# Register each model to make it accessible in the admin panel
admin.site.register(President)
admin.site.register(Club)
admin.site.register(Local)
admin.site.register(Demande)
admin.site.register(Ticket)
