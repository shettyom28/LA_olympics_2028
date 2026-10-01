# Backend — Django REST API

## Running with Docker (recommended)

From the project root:

```bash
docker compose up --build
```

The backend starts on port **8081** and automatically:
1. Runs all migrations
2. Seeds demo data if the database is empty
3. Resets demo account passwords (safe to re-run on existing database)
4. Starts Gunicorn with 4 workers

## Running locally (development)

### Requirements

- Python 3.10+
- PostgreSQL running locally (or override `DATABASE_URL` to use SQLite)

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seeddata       # loads demo fixtures and sets account passwords
python manage.py runserver
```

API: http://localhost:8000/api/v1/
Swagger: http://localhost:8000/api/v1/docs/

## Demo accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Superuser |
| `staff1` | `staff123` | Staff |
| `spectator1` | `spectator123` | Spectator |

## Management commands

| Command | Description |
|---|---|
| `migrate` | Apply database migrations |
| `seeddata` | Load fixtures + set demo account passwords |
| `create_service_accounts` | Create/refresh microservice API tokens |
| `db_worker` | Start background task worker |
| `run_periodic_tasks` | Start periodic task scheduler |
| `redis_subscriber` | Start Redis pub/sub subscriber |

## API endpoints

Base URL: `/api/v1/`

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `auth/register/` | Register new account |
| POST | `auth/login/` | Login — returns auth token |
| POST | `auth/logout/` | Logout |
| POST | `auth/password/reset/` | Request password reset email |
| POST | `auth/password/reset/confirm/` | Confirm new password |

### Public

| Method | Endpoint | Description |
|---|---|---|
| GET | `events/` | List events — filter: `?sport=`, `?date=YYYY-MM-DD`, `?venue=` |
| GET | `events/<id>/` | Event detail with results |
| GET | `leaderboard/` | Medal counts per country |
| GET | `athletes/` | List all athletes |
| GET | `athletes/<id>/profile/` | Single athlete profile |
| GET | `sports/` | List all sports |
| GET | `venues/` | List all venues |
| GET | `profiles/<username>/` | User profile |

### Authenticated

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `tickets/` | — | My tickets |
| POST | `tickets/book/` | `{ "event_id": <id> }` | Book a ticket |
| GET | `favourites/` | — | My favourites |
| POST | `favourites/` | `{ "event": <id> }` or `{ "athlete": <id> }` | Add favourite |
| DELETE | `favourites/<id>/` | — | Remove favourite |
| GET | `example-messages/` | — | My chatbot history |
| POST | `example-messages/` | `{ "content": "..." }` | Send chatbot message |

### Staff only

| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `events/` | `{ name, sport, venue, start_time, end_time, ticket_capacity }` | Create event |
| DELETE | `events/<id>/` | — | Delete event |
| POST | `results/` | `{ event, athlete, rank, medal, score }` | Record result |
| DELETE | `results/<id>/` | — | Delete result |
| POST | `sports/` | `{ name }` | Add sport |
| POST | `venues/` | `{ name, location, capacity }` | Add venue |
| GET | `accommodations/` | — | List accommodations |
| POST | `accommodations/` | `{ name, capacity }` | Create accommodation |
| POST | `accommodations/<id>/assign/` | `{ "athlete_id": <id> }` | Assign athlete |

Full interactive docs (Swagger UI): http://localhost:8081/api/v1/docs/

## Models

| Model | Key fields |
|---|---|
| `User` | Django built-in + `UserProfile` (role, country) |
| `Athlete` | user, sport, country, bio |
| `Sport` | name |
| `Venue` | name, location, capacity |
| `Event` | name, sport, venue, start_time, end_time, ticket_capacity |
| `Result` | event, athlete, rank, medal (G/S/B/N), score |
| `Ticket` | user, event, booked_at — unique per (user, event) |
| `Favourite` | user, event (nullable), athlete (nullable) |
| `Accommodation` | name, capacity, assigned_athletes (M2M) |
| `Country` | name, code |
| `Message` | user, content, bot_response (chatbot history) |
