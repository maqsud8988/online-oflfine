from django.contrib import admin
from . import models


@admin.register(models.TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'status')
    list_display_links = ('id', 'user_id', 'name', 'status')

@admin.register(models.Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'is_busy')
    list_display_links = ('id', 'user_id', 'is_busy')