from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Profile, Follow


@admin.register(get_user_model())
class MyUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("birth_date", )
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("birth_date",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {"fields": ("birth_date",)}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("bio", "user")
    search_fields = ("user",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed")
