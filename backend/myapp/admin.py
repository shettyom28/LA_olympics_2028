from django.contrib import admin
from .models import Country, Sport, Venue, Athlete, Event, Result, UserProfile, Message

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')
    search_fields = ('name', 'location')

@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'sport')
    list_filter = ('country', 'sport')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'venue', 'start_time', 'ticket_capacity')
    list_filter = ('sport', 'venue', 'start_time')
    search_fields = ('name',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('event', 'athlete', 'medal', 'rank', 'score')
    list_filter = ('medal', 'event__sport', 'event')
    search_fields = ('athlete__user__username', 'event__name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'country')
    list_filter = ('role', 'country')
    search_fields = ('user__username',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'bot_response', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')