from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Athlete, Sport, Country, Event, Result, Message, Ticket, Accommodation, Favourite, Venue


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, default='')
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('staff', 'Staff'), ('athlete', 'Athlete'), ('spectator', 'Spectator')], default='spectator')
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate_username(self, value: str):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def create(self, validated_data: dict):
        role = validated_data.pop('role', 'spectator')
        country = validated_data.pop('country', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        UserProfile.objects.create(user=user, role=role, country=country)
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name=role.capitalize())
        user.groups.add(group)
        return user


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


class AthleteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = Athlete
        fields = ['id', 'username', 'full_name', 'country', 'country_name', 'sport', 'sport_name', 'bio']


class AthletePublicSerializer(serializers.ModelSerializer):
    """Trimmed, public-safe athlete profile."""
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    country = serializers.CharField(source='country.name', read_only=True)
    sport = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = Athlete
        fields = ['id', 'username', 'full_name', 'country', 'sport', 'bio']


class EventSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    athletes_preview = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_athletes_preview(self, obj):
        return [
            r.athlete.user.get_full_name() or r.athlete.user.username
            for r in obj.results.select_related('athlete__user').all()[:4]
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'date_joined', 'role', 'country', 'country_name']


class MessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'username', 'content', 'bot_response', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class MessageResultSerializer(serializers.Serializer):
    bot_reply = serializers.CharField(required=False, allow_blank=True, default='')


class ResultSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.user.username', read_only=True)
    sport_name = serializers.CharField(source='event.sport.name', read_only=True)

    class Meta:
        model = Result
        fields = '__all__'


class MedalCountSerializer(serializers.Serializer):
    country_name = serializers.CharField()
    country_code = serializers.CharField()
    gold = serializers.IntegerField()
    silver = serializers.IntegerField()
    bronze = serializers.IntegerField()
    total = serializers.IntegerField()


# ── Task 1 ────────────────────────────────────────────────────────────────────

class TicketSerializer(serializers.ModelSerializer):
    event_name       = serializers.CharField(source='event.name',            read_only=True)
    event_sport      = serializers.CharField(source='event.sport.name',      read_only=True)
    event_venue      = serializers.CharField(source='event.venue.name',      read_only=True)
    event_start_time = serializers.DateTimeField(source='event.start_time',  read_only=True)
    event_end_time   = serializers.DateTimeField(source='event.end_time',    read_only=True)
    username         = serializers.CharField(source='user.username',         read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'event_name', 'event_sport', 'event_venue',
                  'event_start_time', 'event_end_time', 'user', 'username', 'booked_at']
        read_only_fields = ['id', 'user', 'booked_at']


# ── Task 2 ────────────────────────────────────────────────────────────────────

class AccommodationSerializer(serializers.ModelSerializer):
    assigned_athletes = AthleteSerializer(many=True, read_only=True)
    assigned_athlete_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Athlete.objects.all(),
        source='assigned_athletes',
        write_only=True,
        required=False,
    )
    spots_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = [
            'id', 'name', 'location', 'capacity',
            'assigned_athletes', 'assigned_athlete_ids', 'spots_remaining',
        ]

    def get_spots_remaining(self, obj):
        return obj.capacity - obj.assigned_athletes.count()


# ── Task 3 ────────────────────────────────────────────────────────────────────

class FavouriteSerializer(serializers.ModelSerializer):
    event_name       = serializers.CharField(source='event.name',            read_only=True)
    event_sport      = serializers.CharField(source='event.sport.name',      read_only=True)
    event_venue      = serializers.CharField(source='event.venue.name',      read_only=True)
    event_start_time = serializers.DateTimeField(source='event.start_time',  read_only=True)
    athlete_name     = serializers.CharField(source='athlete.user.username', read_only=True)
    athlete_sport    = serializers.CharField(source='athlete.sport.name',    read_only=True)

    class Meta:
        model = Favourite
        fields = ['id', 'event', 'athlete', 'created_at',
                  'event_name', 'event_sport', 'event_venue', 'event_start_time',
                  'athlete_name', 'athlete_sport']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if not attrs.get('event') and not attrs.get('athlete'):
            raise serializers.ValidationError("Provide at least one of: event, athlete.")
        return attrs
