from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_filter = ("username", "email")


admin.site.register(CustomUser, CustomUserAdmin)
