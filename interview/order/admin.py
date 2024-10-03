from django.contrib import admin
from interview.order.models import Order, OrderTag

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'start_date', 'embargo_date', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'start_date', 'embargo_date')
    search_fields = ('inventory__name',)
    ordering = ('-created_at',)

@admin.register(OrderTag)
class OrderTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)