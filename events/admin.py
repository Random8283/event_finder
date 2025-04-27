from django.contrib import admin
from .models import Event, Category, Registration

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'campus', 'organizer', 'category')
    list_filter = ('date', 'campus', 'category', 'organizer')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'
    ordering = ('-date', '-time')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'status')
    list_filter = ('status', 'registration_date')
    search_fields = ('event__title', 'user__username')
    date_hierarchy = 'registration_date'
