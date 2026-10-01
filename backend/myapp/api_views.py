from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Case, When, IntegerField, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, Athlete, Sport, Event, Message, Result, Country, Ticket, Accommodation, Favourite, Venue
from .permissions import IsStaffUser
from .serializers import (
    AuthUserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    AthleteSerializer,
    AthletePublicSerializer,
    SportSerializer,
    EventSerializer,
    MessageSerializer,
    MessageResultSerializer,
    ResultSerializer,
    MedalCountSerializer,
    TicketSerializer,
    AccommodationSerializer,
    FavouriteSerializer,
    VenueSerializer,
)


# ── Shared pagination ─────────────────────────────────────────────────────────

class StandardPagination(PageNumberPagination):
    """Returns 20 items per page. Override with ?page_size=N (max 100)."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ── Athletes & Sports ─────────────────────────────────────────────────────────

class AthleteListView(APIView):
    """List all athletes (paginated) or register the current user as an athlete."""
    serializer_class = AthleteSerializer

    def get(self, request: Request):
        athletes = Athlete.objects.select_related('user', 'country', 'sport').all()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(athletes, request)
        return paginator.get_paginated_response(AthleteSerializer(page, many=True).data)

    def post(self, request: Request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_403_FORBIDDEN)
        if Athlete.objects.filter(user=request.user).exists():
            return Response({"detail": "Athlete profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AthleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SportListView(APIView):
    """List all available sports (paginated). POST — create (staff only)."""
    serializer_class = SportSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffUser()]
        return [permissions.AllowAny()]

    def get(self, request: Request):
        sports = Sport.objects.all()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(sports, request)
        return paginator.get_paginated_response(SportSerializer(page, many=True).data)

    def post(self, request: Request):
        serializer = SportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VenueListView(APIView):
    """GET /api/v1/venues/ — list all. POST — create (staff only)."""
    serializer_class = VenueSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffUser()]
        return [permissions.AllowAny()]

    def get(self, request: Request):
        venues = Venue.objects.all()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(venues, request)
        return paginator.get_paginated_response(VenueSerializer(page, many=True).data)

    def post(self, request: Request):
        serializer = VenueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ── Task 2: Athlete public profile ────────────────────────────────────────────

class AthletePublicProfileView(APIView):
    """Public profile for a single athlete — no auth required."""
    permission_classes = [permissions.AllowAny]
    serializer_class = AthletePublicSerializer

    def get(self, request: Request, pk: int):
        athlete = get_object_or_404(
            Athlete.objects.select_related('user', 'country', 'sport'), pk=pk
        )
        return Response(AthletePublicSerializer(athlete).data)


# ── Profiles ──────────────────────────────────────────────────────────────────

class UserProfileView(APIView):
    """Retrieve or update a user profile."""
    serializer_class = UserProfileSerializer

    def get(self, request: Request, username: str):
        user = get_object_or_404(User, username=username)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return Response(UserProfileSerializer(profile).data)

    def put(self, request: Request, username: str):
        if not request.user.is_authenticated or request.user.username != username:
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """Register a new user account."""
    serializer_class = RegisterSerializer

    @extend_schema(responses={201: AuthUserSerializer})
    def post(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AuthUserSerializer(user).data, status=status.HTTP_201_CREATED)


# ── Messages / Chatbot ────────────────────────────────────────────────────────

class MessageListView(APIView):
    """List messages for the current user, or create a new message."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request: Request):
        messages = Message.objects.filter(user=request.user).order_by('created_at')
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request: Request):
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)
        message = Message.objects.create(user=request.user, content=content)
        from .service_pub import publish_example_message
        previous = Message.objects.filter(
            user=request.user, bot_response__isnull=False
        ).order_by('created_at').exclude(id=message.id)[:20]
        history = [{'user': m.content, 'bot': m.bot_response} for m in previous]
        publish_example_message(message.id, content, request.user.username, history)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class MessageResultUpdateView(APIView):
    """Update a message with a bot reply from the microservice."""
    serializer_class = MessageResultSerializer

    def post(self, request: Request, message_id: int):
        message = get_object_or_404(Message, id=message_id)
        serializer = MessageResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message.bot_response = serializer.validated_data.get('bot_reply', '')
        message.save()
        return Response(MessageSerializer(message).data)


# ── Events ────────────────────────────────────────────────────────────────────

class EventListView(APIView):
    """List events (paginated) with optional ?sport=, ?date=, ?venue= filters."""
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffUser()]
        return [permissions.AllowAny()]

    def get(self, request: Request):
        qs = Event.objects.select_related('sport', 'venue').prefetch_related('results__athlete__user').all()
        sport_id = request.query_params.get('sport')
        date = request.query_params.get('date')
        venue_id = request.query_params.get('venue')
        if sport_id:
            qs = qs.filter(sport_id=sport_id)
        if date:
            qs = qs.filter(start_time__date=date)
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(EventSerializer(page, many=True).data)

    def post(self, request: Request):
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventDetailView(APIView):
    """Retrieve or delete a single event (DELETE: staff only)."""
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer

    def get(self, request: Request, event_id: int):
        event = get_object_or_404(
            Event.objects.select_related('sport', 'venue').prefetch_related('results__athlete__user'),
            id=event_id
        )
        data = EventSerializer(event).data
        data['results'] = ResultSerializer(event.results.all(), many=True).data
        return Response(data)

    def delete(self, request: Request, event_id: int):
        if not request.user.is_authenticated or not (
            request.user.is_staff or request.user.groups.filter(name='Staff').exists()
        ):
            return Response({"detail": "Staff access required."}, status=status.HTTP_403_FORBIDDEN)
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Results & Leaderboard ─────────────────────────────────────────────────────

class ResultCreateView(APIView):
    """Record a new result (Staff only)."""
    permission_classes = [IsStaffUser]
    serializer_class = ResultSerializer

    def post(self, request: Request):
        serializer = ResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResultDetailView(APIView):
    """Delete a result (staff only)."""
    permission_classes = [IsStaffUser]
    serializer_class = ResultSerializer

    def delete(self, request: Request, result_id: int):
        result = get_object_or_404(Result, id=result_id)
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaderboardView(APIView):
    """List medal counts per country."""
    permission_classes = [permissions.AllowAny]
    serializer_class = MedalCountSerializer

    def get(self, request: Request):
        countries = Country.objects.annotate(
            gold=Count(Case(When(athlete__performances__medal='G', then=1), output_field=IntegerField())),
            silver=Count(Case(When(athlete__performances__medal='S', then=1), output_field=IntegerField())),
            bronze=Count(Case(When(athlete__performances__medal='B', then=1), output_field=IntegerField())),
        ).annotate(
            total=Sum(Case(
                When(athlete__performances__medal__in=['G', 'S', 'B'], then=1),
                default=0,
                output_field=IntegerField()
            ))
        ).order_by('-gold', '-silver', '-bronze', 'name')

        return Response([{
            'country_name': c.name,
            'country_code': c.code,
            'gold': c.gold,
            'silver': c.silver,
            'bronze': c.bronze,
            'total': c.total,
        } for c in countries])


# ── Task 1: Ticket booking ────────────────────────────────────────────────────

class TicketBookingView(APIView):
    """
    GET  /api/v1/tickets/       — List tickets for the logged-in user.
    POST /api/v1/tickets/book/  — Book a ticket (select_for_update prevents double-booking).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer

    def get(self, request: Request):
        tickets = Ticket.objects.filter(user=request.user).select_related('event__sport', 'event__venue')
        paginator = StandardPagination()
        page = paginator.paginate_queryset(tickets, request)
        return paginator.get_paginated_response(TicketSerializer(page, many=True).data)

    def post(self, request: Request):
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({"detail": "event_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            event = get_object_or_404(Event.objects.select_for_update(), id=event_id)
            if Ticket.objects.filter(event=event, user=request.user).exists():
                return Response(
                    {"detail": "You already have a ticket for this event."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Ticket.objects.filter(event=event).count() >= event.ticket_capacity:
                return Response(
                    {"detail": "This event is fully booked."},
                    status=status.HTTP_409_CONFLICT,
                )
            ticket = Ticket.objects.create(event=event, user=request.user)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


# ── Task 2: Accommodation ─────────────────────────────────────────────────────

class AccommodationListView(APIView):
    """
    GET  /api/v1/accommodations/  — List all (public).
    POST /api/v1/accommodations/  — Create (Staff only).
    """
    serializer_class = AccommodationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsStaffUser()]
        return [permissions.AllowAny()]

    def get(self, request: Request):
        qs = Accommodation.objects.prefetch_related('assigned_athletes').all()
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AccommodationSerializer(page, many=True).data)

    def post(self, request: Request):
        serializer = AccommodationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccommodationAssignView(APIView):
    """POST /api/v1/accommodations/<pk>/assign/ — Assign an athlete (Staff only)."""
    permission_classes = [IsStaffUser]
    serializer_class = AccommodationSerializer

    def post(self, request: Request, pk: int):
        accommodation = get_object_or_404(Accommodation, pk=pk)
        athlete_id = request.data.get('athlete_id')
        if not athlete_id:
            return Response({"detail": "athlete_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        athlete = get_object_or_404(Athlete, pk=athlete_id)
        if accommodation.assigned_athletes.count() >= accommodation.capacity:
            return Response(
                {"detail": "Accommodation is at full capacity."},
                status=status.HTTP_409_CONFLICT,
            )
        accommodation.assigned_athletes.add(athlete)
        return Response(AccommodationSerializer(accommodation).data)


# ── Task 3: Favourites ────────────────────────────────────────────────────────

class FavouriteView(APIView):
    """
    GET  /api/v1/favourites/  — List logged-in user's favourites.
    POST /api/v1/favourites/  — Add a favourite { "event": <id>, "athlete": <id> }.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavouriteSerializer

    def get(self, request: Request):
        favourites = Favourite.objects.filter(user=request.user).select_related('event', 'athlete')
        paginator = StandardPagination()
        page = paginator.paginate_queryset(favourites, request)
        return paginator.get_paginated_response(FavouriteSerializer(page, many=True).data)

    def post(self, request: Request):
        serializer = FavouriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        favourite, created = Favourite.objects.get_or_create(
            user=request.user,
            event=serializer.validated_data.get('event'),
            athlete=serializer.validated_data.get('athlete'),
        )
        return Response(FavouriteSerializer(favourite).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class FavouriteDetailView(APIView):
    """DELETE /api/v1/favourites/<pk>/ — Remove a favourite."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request, pk: int):
        favourite = get_object_or_404(Favourite, pk=pk, user=request.user)
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
