from django.contrib import admin
from interview.inventory.models import (
    Inventory,
    InventoryType,
    InventoryLanguage,
    InventoryTag,
)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'language', 'is_active', 'created_at', 'updated_at')
    list_filter = ('type', 'language', 'is_active')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(InventoryType)
class InventoryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(InventoryLanguage)
class InventoryLanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(InventoryTag)
class InventoryTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
