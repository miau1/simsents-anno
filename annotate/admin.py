from django.contrib import admin

from .models import  Annotator

class AnnotatorAdmin(admin.ModelAdmin):
	fields = ['user', 'lang']

admin.site.register(Annotator, AnnotatorAdmin)

