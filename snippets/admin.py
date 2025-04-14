from django.contrib import admin
from .models import Snippet, Tag

admin.site.register(Snippet)
admin.site.register(Tag)

