from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import api_views

app_name = 'api'
urlpatterns = [
    # Documentation & Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='docs'),

    # Authentication
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/register/', api_views.RegisterView.as_view(), name='register'),

    # Athletes & Sports
    path('athletes/', api_views.AthleteListView.as_view(), name='athlete-list'),
    path('athletes/<int:pk>/profile/', api_views.AthletePublicProfileView.as_view(), name='athlete-public-profile'),
    path('sports/', api_views.SportListView.as_view(), name='sport-list'),
    path('venues/', api_views.VenueListView.as_view(), name='venue-list'),

    # Events
    path('events/', api_views.EventListView.as_view(), name='event-list'),
    path('events/<int:event_id>/', api_views.EventDetailView.as_view(), name='event-detail'),

    # Results & Leaderboard
    path('results/', api_views.ResultCreateView.as_view(), name='result-create'),
    path('results/<int:result_id>/', api_views.ResultDetailView.as_view(), name='result-detail'),
    path('leaderboard/', api_views.LeaderboardView.as_view(), name='leaderboard'),

    # Profiles
    path('profiles/<str:username>/', api_views.UserProfileView.as_view(), name='user-profile'),

    # Chatbot messages
    path('example-messages/', api_views.MessageListView.as_view(), name='message-list'),
    path('example-messages/<int:message_id>/result/', api_views.MessageResultUpdateView.as_view(), name='message-result'),

    # Task 1: Ticket booking
    path('tickets/', api_views.TicketBookingView.as_view(), name='ticket-list'),
    path('tickets/book/', api_views.TicketBookingView.as_view(), name='ticket-book'),

    # Task 2: Accommodation
    path('accommodations/', api_views.AccommodationListView.as_view(), name='accommodation-list'),
    path('accommodations/<int:pk>/assign/', api_views.AccommodationAssignView.as_view(), name='accommodation-assign'),

    # Task 3: Favourites
    path('favourites/', api_views.FavouriteView.as_view(), name='favourites'),
    path('favourites/<int:pk>/', api_views.FavouriteDetailView.as_view(), name='favourite-detail'),
]
