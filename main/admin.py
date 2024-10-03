from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Profile)
admin.site.register(models.Lesson)
admin.site.register(models.Date)
admin.site.register(models.Mark)
admin.site.register(models.Payment)
admin.site.register(models.History)
