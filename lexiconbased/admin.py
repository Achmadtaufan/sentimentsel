from django.contrib import admin
from lexiconbased.models import *

# Register your models here.
class ResultAdmin(admin.ModelAdmin):
    list_display = ['sentiment', 'classification']
    list_filter = ()
    search_fields = ['sentiment']
    list_per_page = 25

admin.site.register(Result, ResultAdmin)