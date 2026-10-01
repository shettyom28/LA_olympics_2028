# Olympics 2028 — Web Application (EEN1037 Group Project)

A full-stack web application for managing and browsing the Los Angeles 2028 Olympic Games.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite, TanStack Query, React Router |
| Backend | Django 5 + Django REST Framework, PostgreSQL |
| Microservice | Python (Google Gemini AI chatbot) via Redis pub/sub |
| Infrastructure | Docker Compose — PostgreSQL, Redis, MinIO, Mailpit |

---

## Quick Start

> Requires Docker and Docker Compose.

```bash
docker compose up --build
```

On first run the database is automatically migrated and seeded with demo data. No extra steps needed.

To wipe all data and start fresh:

```bash
docker compose down -v
docker compose up --build
```

---

## Service URLs

| Service | URL |
|---|---|
| **Frontend** | http://localhost:8080 |
| **Backend API** | http://localhost:8081/api/v1/ |
| **API Docs (Swagger)** | http://localhost:8081/api/v1/docs/ |
| **Django Admin** | http://localhost:8081/admin/ |
| **Mailpit (email UI)** | http://localhost:8025 |
| **MinIO Console** | http://localhost:9001 |

---

## Demo Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Superuser (Django admin access) |
| `staff1` | `staff123` | Staff (access to Staff Dashboard) |
| `spectator1` | `spectator123` | Spectator |

---

## Frontend Pages

| Route | Description | Auth |
|---|---|---|
| `/` | Landing page — hero slider, upcoming events, athletes preview, ticket pricing, medal leaderboard | Public |
| `/schedule` | Event schedule filterable by sport, venue, date | Public |
| `/event/:id` | Event detail — sport, venue, date/time, capacity, results, booking button | Public / Yes (book) |
| `/leaderboard` | Medal table by country — sortable by Gold, Silver, Bronze, Total | Public |
| `/athletes` | Athlete grid — searchable by name/country, filterable by sport | Public |
| `/athlete/:id` | Athlete profile — sport, country, bio | Public |
| `/venues` | Venue cards — name, location, capacity, event count, OpenStreetMap link | Public |
| `/my-tickets` | All tickets booked by the logged-in user | Required |
| `/profile/:username` | User profile — stats, saved events, followed athletes, booked tickets | Public / Yes (own profile) |
| `/admin` | Staff Dashboard — Events, Results, Accommodations, Sports, Venues management | Staff only |
| `/register` | Create account — username, email, password, role, country | Public |
| `/login` | Sign in | Public |
| `/forgot-password` | Request password reset email | Public |
| `/reset-password/:uid/:token` | Set new password via email link | Public |

---

## Backend API Endpoints

Base URL: `http://localhost:8081/api/v1/`

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
| GET | `events/` | List all events (filter: `?sport=`, `?date=`, `?venue=`) |
| GET | `events/<id>/` | Event detail + results |
| GET | `leaderboard/` | Medal counts per country |
| GET | `athletes/` | List all athletes |
| GET | `athletes/<id>/profile/` | Single athlete public profile |
| GET | `sports/` | List all sports |
| GET | `venues/` | List all venues |
| GET | `profiles/<username>/` | User profile |

### Authenticated users

| Method | Endpoint | Description |
|---|---|---|
| GET | `tickets/` | List my tickets |
| POST | `tickets/book/` | Book a ticket — body: `{ "event_id": <id> }` |
| GET | `favourites/` | List my favourites |
| POST | `favourites/` | Add favourite — body: `{ "event": <id> }` or `{ "athlete": <id> }` |
| DELETE | `favourites/<id>/` | Remove a favourite |
| GET | `example-messages/` | List my chatbot messages |
| POST | `example-messages/` | Send chatbot message — body: `{ "content": "..." }` |

### Staff only

| Method | Endpoint | Description |
|---|---|---|
| POST | `events/` | Create event |
| DELETE | `events/<id>/` | Delete event |
| POST | `results/` | Record a result with medal |
| DELETE | `results/<id>/` | Delete a result |
| POST | `sports/` | Add a sport |
| POST | `venues/` | Add a venue |
| GET | `accommodations/` | List accommodations |
| POST | `accommodations/` | Create accommodation |
| POST | `accommodations/<id>/assign/` | Assign athlete to accommodation — body: `{ "athlete_id": <id> }` |

Full interactive docs: http://localhost:8081/api/v1/docs/

---

## Docker Services

| Service | Description |
|---|---|
| `app-frontend` | React app served by Nginx — port **8080** |
| `app-backend` | Django + Gunicorn — port **8081** |
| `app-microservice` | Python worker — Gemini AI chatbot via Redis |
| `app-task-worker` | Background task worker |
| `app-task-scheduler` | Periodic task scheduler |
| `app-redis-subscriber` | Redis subscriber for real-time updates |
| `db` | PostgreSQL 17 |
| `redis` | Redis 7 |
| `mailpit` | SMTP catch-all + web UI — port **8025** |
| `minio` | S3-compatible object storage — console port **9001** |

---

## Gemini AI Chatbot

The chatbot requires a Google Gemini API key. Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your-key-here
```

Without the key the chatbot returns a fallback message — the rest of the app works normally.
