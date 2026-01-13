from django.contrib import admin
from .models import Gallery, Photo, ClientChoice, ProcessingStage, GalleryAccess, GalleryInvite
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    readonly_fields = ('thumbnail_preview',)
    def thumbnail_preview(self, obj):
        from django.utils.html import mark_safe
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return ""
class ProcessingStageInline(admin.TabularInline):
    model = ProcessingStage
    extra = 1
class GalleryAccessInline(admin.TabularInline):
    model = GalleryAccess
    extra = 1
    autocomplete_fields = ['user']
class GalleryInviteInline(admin.TabularInline):
    model = GalleryInvite
    extra = 0
    readonly_fields = ('token', 'usage_count', 'created_at')
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'photographer', 'is_public', 'created_at', 'expires_at', 'is_active')
    search_fields = ('title', 'photographer__username')
    list_filter = ('created_at', 'photographer', 'is_public', 'is_active')
    inlines = [GalleryAccessInline, GalleryInviteInline, ProcessingStageInline, PhotoInline]
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'gallery', 'sequence_number', 'status')
    list_filter = ('gallery', 'status')
    search_fields = ('gallery__title',)
@admin.register(ClientChoice)
class ClientChoiceAdmin(admin.ModelAdmin):
    list_display = ('photo', 'client', 'is_liked', 'timestamp')
    list_filter = ('is_liked', 'timestamp', 'client')
@admin.register(ProcessingStage)
class ProcessingStageAdmin(admin.ModelAdmin):
    list_display = ('gallery', 'name', 'completed', 'order')
    list_editable = ('completed',)
@admin.register(GalleryAccess)
class GalleryAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'gallery', 'role', 'joined_at')
    list_filter = ('role', 'gallery')
@admin.register(GalleryInvite)
class GalleryInviteAdmin(admin.ModelAdmin):
    list_display = ('gallery', 'role', 'usage_count', 'usage_limit', 'created_at')
    list_filter = ('role', 'gallery')