from django.db import models
from django.contrib.auth.models import User

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    flag_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.name} ({self.code})"

class Sport(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = [('staff', 'Staff'), ('athlete', 'Athlete'), ('spectator', 'Spectator')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='spectator')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Athlete(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_profile')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Event(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    ticket_capacity = models.IntegerField(default=0)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.sport.name})"

class Result(models.Model):
    MEDAL_CHOICES = [('G', 'Gold'), ('S', 'Silver'), ('B', 'Bronze'), ('N', 'None')]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='results')
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='performances', db_index=True)
    medal = models.CharField(max_length=1, choices=MEDAL_CHOICES, default='N')
    score = models.CharField(max_length=50, blank=True)
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'athlete')
        ordering = ['rank']

    def __str__(self):
        return f"{self.athlete} - {self.event.name} - {self.medal}"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    bot_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


# ── Task 1 ────────────────────────────────────────────────────────────────────

class Ticket(models.Model):
    """A ticket booking for a specific event by a user."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.event.name}"


# ── Task 2 ────────────────────────────────────────────────────────────────────

class Accommodation(models.Model):
    """Accommodation unit that can be assigned to athletes."""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField(default=0)
    assigned_athletes = models.ManyToManyField(
        Athlete, blank=True, related_name='accommodations'
    )

    def __str__(self):
        return f"{self.name} ({self.location})"


# ── Task 3 ────────────────────────────────────────────────────────────────────

class Favourite(models.Model):
    """A user can favourite an event or an athlete."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, blank=True, related_name='favourited_by'
    )
    athlete = models.ForeignKey(
        Athlete, on_delete=models.CASCADE, null=True, blank=True, related_name='favourited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate favourites for the same (user, event, athlete) combo
        unique_together = ('user', 'event', 'athlete')

    def __str__(self):
        target = self.event or self.athlete
        return f"{self.user.username} ♥ {target}"