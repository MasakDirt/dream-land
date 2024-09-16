from django.contrib import admin

from dream.models import (
    Emotion,
    Symbol,
    Dream,
    DreamLike,
    DreamDislike,
    Commentary,
    CommentaryLike,
    CommentaryDislike,
)


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ("title", "date_recorded", "user")
    list_filter = ("user", "symbols", "emotions")
    search_fields = ("title", "symbols", "emotions")


@admin.register(DreamLike)
class DreamLikeAdmin(admin.ModelAdmin):
    list_display = ("owner", "dream", "created_time")
    list_filter = ("owner", "dream")
    search_fields = ("owner", "dream")


@admin.register(DreamDislike)
class DreamDislikeAdmin(admin.ModelAdmin):
    list_display = ("owner", "dream", "created_time")
    list_filter = ("owner", "dream")
    search_fields = ("owner", "dream")


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ("content", "owner", "dream", "created_time")
    list_filter = ("owner", "dream")
    search_fields = ("content", "owner", "dream")


@admin.register(CommentaryLike)
class CommentaryLikeAdmin(admin.ModelAdmin):
    list_display = ("owner", "commentary", "created_time")
    list_filter = ("owner", "commentary")
    search_fields = ("owner", "commentary")


@admin.register(CommentaryDislike)
class CommentaryDislikeAdmin(admin.ModelAdmin):
    list_display = ("owner", "commentary", "created_time")
    list_filter = ("owner", "commentary")
    search_fields = ("owner", "commentary")
