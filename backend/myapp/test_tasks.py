"""
Tests for Task 1, 2, and 3 of the Olympics backend assignment.

Run with:
    python manage.py test myapp.test_tasks
"""

from datetime import datetime, timezone as dt_timezone

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from myapp.models import (
    Accommodation,
    Athlete,
    Country,
    Event,
    Favourite,
    Sport,
    Ticket,
    UserProfile,
    Venue,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_user(username, password="pass1234", role="spectator"):
    # is_staff=True so IsStaffUser permission passes for staff role
    user = User.objects.create_user(
        username=username,
        password=password,
        is_staff=(role == "staff"),
    )
    UserProfile.objects.create(user=user, role=role)
    return user


def auth_client(user):
    """Return an APIClient already authenticated as *user*."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_event(name="100m Sprint", capacity=10):
    sport = Sport.objects.create(name=f"Sport-{name}")
    venue = Venue.objects.create(name=f"Venue-{name}", location="LA", capacity=50000)
    return Event.objects.create(
        name=name,
        sport=sport,
        venue=venue,
        start_time=datetime(2028, 7, 26, 10, 0, tzinfo=dt_timezone.utc),
        end_time=datetime(2028, 7, 26, 12, 0, tzinfo=dt_timezone.utc),
        ticket_capacity=capacity,
    )


def make_athlete(username="athlete1"):
    user = User.objects.create_user(username=username)
    country, _ = Country.objects.get_or_create(code="IRL", defaults={"name": "Ireland"})
    sport = Sport.objects.create(name=f"Sport-{username}")
    return Athlete.objects.create(user=user, country=country, sport=sport, bio="Test bio")


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 1 — Ticket Booking
# ═══════════════════════════════════════════════════════════════════════════════

class TicketBookingTests(TestCase):

    def setUp(self):
        self.spectator = make_user("spectator1")
        self.client = auth_client(self.spectator)
        self.event = make_event("100m Sprint", capacity=2)

    # ── Book successfully ─────────────────────────────────────────────────────

    def test_book_ticket_success(self):
        response = self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event"], self.event.id)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_book_ticket_response_contains_expected_fields(self):
        response = self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertIn("id", response.data)
        self.assertIn("event", response.data)
        self.assertIn("event_name", response.data)
        self.assertIn("booked_at", response.data)

    # ── Auth required ─────────────────────────────────────────────────────────

    def test_book_ticket_requires_auth(self):
        anon = APIClient()
        response = anon.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Validation ────────────────────────────────────────────────────────────

    def test_book_ticket_missing_event_id(self):
        response = self.client.post("/api/v1/tickets/book/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("event_id is required", response.data["detail"])

    def test_book_ticket_invalid_event_id(self):
        response = self.client.post("/api/v1/tickets/book/", {"event_id": 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ── Duplicate booking ─────────────────────────────────────────────────────

    def test_cannot_book_same_event_twice(self):
        self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        response = self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already have a ticket", response.data["detail"])
        # Only one ticket should exist
        self.assertEqual(Ticket.objects.count(), 1)

    # ── Capacity check ────────────────────────────────────────────────────────

    def test_fully_booked_returns_409(self):
        # Fill all 2 spots
        for i in range(self.event.ticket_capacity):
            user = make_user(f"filler{i}")
            auth_client(user).post("/api/v1/tickets/book/", {"event_id": self.event.id})

        # Now our spectator tries to book — should be full
        response = self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("fully booked", response.data["detail"])

    def test_last_available_spot_books_successfully(self):
        # Fill all spots except one
        for i in range(self.event.ticket_capacity - 1):
            user = make_user(f"filler{i}")
            auth_client(user).post("/api/v1/tickets/book/", {"event_id": self.event.id})

        # Last spot should succeed
        response = self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ── List tickets ──────────────────────────────────────────────────────────

    def test_list_tickets_returns_only_own_tickets(self):
        self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})

        # Another user books the same event
        other = make_user("other1")
        event2 = make_event("200m Sprint", capacity=5)
        auth_client(other).post("/api/v1/tickets/book/", {"event_id": event2.id})

        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see spectator1's ticket, not other's
        self.assertEqual(response.data["count"], 1)

    def test_list_tickets_is_paginated(self):
        self.client.post("/api/v1/tickets/book/", {"event_id": self.event.id})
        response = self.client.get("/api/v1/tickets/")
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_list_tickets_requires_auth(self):
        anon = APIClient()
        response = anon.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2 — Accommodation
# ═══════════════════════════════════════════════════════════════════════════════

class AccommodationTests(TestCase):

    def setUp(self):
        self.staff = make_user("staff1", role="staff")
        self.spectator = make_user("spectator2")
        self.staff_client = auth_client(self.staff)
        self.spectator_client = auth_client(self.spectator)
        self.athlete = make_athlete("athlete_acc")

    def _create_accommodation(self, name="Block A", location="LA", capacity=2):
        return self.staff_client.post("/api/v1/accommodations/", {
            "name": name,
            "location": location,
            "capacity": capacity,
        })

    # ── List ──────────────────────────────────────────────────────────────────

    def test_list_accommodations_is_public(self):
        anon = APIClient()
        response = anon.get("/api/v1/accommodations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_accommodations_is_paginated(self):
        response = self.spectator_client.get("/api/v1/accommodations/")
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    # ── Create ────────────────────────────────────────────────────────────────

    def test_staff_can_create_accommodation(self):
        response = self._create_accommodation()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Block A")
        self.assertEqual(response.data["capacity"], 2)

    def test_spectator_cannot_create_accommodation(self):
        response = self.spectator_client.post("/api/v1/accommodations/", {
            "name": "Block B", "location": "LA", "capacity": 3,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anon_cannot_create_accommodation(self):
        anon = APIClient()
        response = anon.post("/api/v1/accommodations/", {
            "name": "Block C", "location": "LA", "capacity": 3,
        })
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_accommodation_response_has_spots_remaining(self):
        response = self._create_accommodation(capacity=5)
        self.assertIn("spots_remaining", response.data)
        self.assertEqual(response.data["spots_remaining"], 5)

    # ── Assign ────────────────────────────────────────────────────────────────

    def test_staff_can_assign_athlete(self):
        self._create_accommodation()
        acc = Accommodation.objects.first()
        response = self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": self.athlete.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(acc.assigned_athletes.count(), 1)

    def test_assign_decreases_spots_remaining(self):
        self._create_accommodation(capacity=3)
        acc = Accommodation.objects.first()
        self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": self.athlete.id},
        )
        response = self.staff_client.get("/api/v1/accommodations/")
        result = next(r for r in response.data["results"] if r["id"] == acc.id)
        self.assertEqual(result["spots_remaining"], 2)

    def test_assign_at_capacity_returns_409(self):
        self._create_accommodation(capacity=1)
        acc = Accommodation.objects.first()
        # Fill the one spot
        self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": self.athlete.id},
        )
        # Try to assign another athlete
        extra = make_athlete("athlete_extra")
        response = self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": extra.id},
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_spectator_cannot_assign_athlete(self):
        self._create_accommodation()
        acc = Accommodation.objects.first()
        response = self.spectator_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": self.athlete.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_missing_athlete_id(self):
        self._create_accommodation()
        acc = Accommodation.objects.first()
        response = self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/", {}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_invalid_athlete_id(self):
        self._create_accommodation()
        acc = Accommodation.objects.first()
        response = self.staff_client.post(
            f"/api/v1/accommodations/{acc.id}/assign/",
            {"athlete_id": 99999},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2 — Athlete Public Profile
# ═══════════════════════════════════════════════════════════════════════════════

class AthletePublicProfileTests(TestCase):

    def setUp(self):
        self.athlete = make_athlete("public_athlete")

    def test_public_profile_no_auth_required(self):
        anon = APIClient()
        response = anon.get(f"/api/v1/athletes/{self.athlete.id}/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_profile_returns_correct_fields(self):
        response = APIClient().get(f"/api/v1/athletes/{self.athlete.id}/profile/")
        self.assertIn("username", response.data)
        self.assertIn("full_name", response.data)
        self.assertIn("country", response.data)
        self.assertIn("sport", response.data)
        self.assertIn("bio", response.data)

    def test_public_profile_correct_data(self):
        response = APIClient().get(f"/api/v1/athletes/{self.athlete.id}/profile/")
        self.assertEqual(response.data["username"], "public_athlete")
        self.assertEqual(response.data["bio"], "Test bio")

    def test_public_profile_nonexistent_athlete_returns_404(self):
        response = APIClient().get("/api/v1/athletes/99999/profile/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2 — Event Filtering
# ═══════════════════════════════════════════════════════════════════════════════

class EventFilteringTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.sport1 = Sport.objects.create(name="Swimming")
        self.sport2 = Sport.objects.create(name="Athletics")
        self.venue1 = Venue.objects.create(name="Aquatics Centre", location="LA", capacity=10000)
        self.venue2 = Venue.objects.create(name="Stadium", location="LA", capacity=80000)

        self.event1 = Event.objects.create(
            name="100m Freestyle",
            sport=self.sport1,
            venue=self.venue1,
            start_time=datetime(2028, 7, 26, 9, 0, tzinfo=dt_timezone.utc),
            end_time=datetime(2028, 7, 26, 10, 0, tzinfo=dt_timezone.utc),
            ticket_capacity=100,
        )
        self.event2 = Event.objects.create(
            name="100m Sprint",
            sport=self.sport2,
            venue=self.venue2,
            start_time=datetime(2028, 7, 27, 10, 0, tzinfo=dt_timezone.utc),
            end_time=datetime(2028, 7, 27, 11, 0, tzinfo=dt_timezone.utc),
            ticket_capacity=100,
        )
        self.event3 = Event.objects.create(
            name="200m Freestyle",
            sport=self.sport1,
            venue=self.venue1,
            start_time=datetime(2028, 7, 26, 14, 0, tzinfo=dt_timezone.utc),
            end_time=datetime(2028, 7, 26, 15, 0, tzinfo=dt_timezone.utc),
            ticket_capacity=100,
        )

    def test_list_all_events_no_filter(self):
        response = self.client.get("/api/v1/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_filter_by_sport(self):
        response = self.client.get(f"/api/v1/events/?sport={self.sport1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        names = [e["name"] for e in response.data["results"]]
        self.assertIn("100m Freestyle", names)
        self.assertIn("200m Freestyle", names)
        self.assertNotIn("100m Sprint", names)

    def test_filter_by_date(self):
        response = self.client.get("/api/v1/events/?date=2028-07-26")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_venue(self):
        response = self.client.get(f"/api/v1/events/?venue={self.venue2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "100m Sprint")

    def test_filter_by_sport_and_date_combined(self):
        response = self.client.get(
            f"/api/v1/events/?sport={self.sport1.id}&date=2028-07-26"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_with_no_results(self):
        response = self.client.get("/api/v1/events/?date=2099-01-01")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_events_list_is_paginated(self):
        response = self.client.get("/api/v1/events/")
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_events_public_no_auth_needed(self):
        response = self.client.get("/api/v1/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 3 — Favourites
# ═══════════════════════════════════════════════════════════════════════════════

class FavouriteTests(TestCase):

    def setUp(self):
        self.user = make_user("fav_user")
        self.client = auth_client(self.user)
        self.event = make_event("Fav Event", capacity=50)
        self.athlete = make_athlete("fav_athlete")

    # ── Auth ──────────────────────────────────────────────────────────────────

    def test_favourites_require_auth(self):
        anon = APIClient()
        response = anon.get("/api/v1/favourites/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_favourite_requires_auth(self):
        anon = APIClient()
        response = anon.post("/api/v1/favourites/", {"event": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Add favourites ────────────────────────────────────────────────────────

    def test_favourite_an_event(self):
        response = self.client.post("/api/v1/favourites/", {"event": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Favourite.objects.count(), 1)

    def test_favourite_an_athlete(self):
        response = self.client.post("/api/v1/favourites/", {"athlete": self.athlete.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Favourite.objects.count(), 1)

    def test_favourite_both_event_and_athlete(self):
        response = self.client.post("/api/v1/favourites/", {
            "event": self.event.id,
            "athlete": self.athlete.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_body_returns_400(self):
        response = self.client.post("/api/v1/favourites/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Duplicate favourites ──────────────────────────────────────────────────

    def test_duplicate_favourite_returns_200_not_201(self):
        self.client.post("/api/v1/favourites/", {"event": self.event.id})
        response = self.client.post("/api/v1/favourites/", {"event": self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Still only one record in the database
        self.assertEqual(Favourite.objects.count(), 1)

    # ── List favourites ───────────────────────────────────────────────────────

    def test_list_favourites_returns_only_own(self):
        self.client.post("/api/v1/favourites/", {"event": self.event.id})

        # Another user adds a different favourite
        other = make_user("other_fav")
        other_event = make_event("Other Event", capacity=10)
        auth_client(other).post("/api/v1/favourites/", {"event": other_event.id})

        response = self.client.get("/api/v1/favourites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_favourites_is_paginated(self):
        self.client.post("/api/v1/favourites/", {"event": self.event.id})
        response = self.client.get("/api/v1/favourites/")
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_list_favourites_empty_initially(self):
        response = self.client.get("/api/v1/favourites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_favourite_response_has_expected_fields(self):
        response = self.client.post("/api/v1/favourites/", {"event": self.event.id})
        self.assertIn("id", response.data)
        self.assertIn("event", response.data)
        self.assertIn("athlete", response.data)
        self.assertIn("created_at", response.data)


# ═══════════════════════════════════════════════════════════════════════════════
# Pagination — general checks on existing list endpoints
# ═══════════════════════════════════════════════════════════════════════════════

class PaginationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_athletes_list_is_paginated(self):
        response = self.client.get("/api/v1/athletes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_sports_list_is_paginated(self):
        response = self.client.get("/api/v1/sports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_page_size_query_param_works(self):
        for i in range(5):
            Sport.objects.create(name=f"Sport {i}")
        response = self.client.get("/api/v1/sports/?page_size=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
