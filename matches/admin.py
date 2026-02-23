from django.contrib import admin

# Register your models here.
from .models import MatchRequest, Match
admin.site.register(MatchRequest)
admin.site.register(Match)