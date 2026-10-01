#!/usr/bin/env python3
"""
Gemini AI Chatbot Microservice.

Receives messages from a REDIS queue.
Sends the message text to Google Gemini AI and posts the response back
to the application via the REST API.

Environment variables:
    REDIS_URL
    API_BASE
    SERVICE_API_TOKEN
    GEMINI_API_KEY
"""

import json
import logging
import os
import time
from typing import Callable

import redis
import requests
from google import genai
from google.genai import types
from opentelemetry import trace
from opentelemetry.propagate import extract as otel_extract_trace_ctx
from opentelemetry.propagate import inject as otel_inject_trace_ctx

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

REDIS_URL   = os.environ["REDIS_URL"]
API_BASE    = os.environ["API_BASE"].rstrip("/")
API_HEADERS = {"Authorization": f"Token {os.environ['SERVICE_API_TOKEN']}"}

# Initialise the Gemini client — reads GEMINI_API_KEY from env automatically
_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not _gemini_api_key:
    logger.warning(
        "GEMINI_API_KEY is not set. The chatbot will not be able to call Gemini AI. "
        "Set GEMINI_API_KEY in your .env file or environment to enable AI responses."
    )
gemini_client = genai.Client()

SYSTEM_PROMPT = """You are the official AI assistant for the Olympics 2028 web application (Los Angeles).

## Pages and navigation

- **Home (/)** — Landing page with a hero image slider, upcoming events preview, featured athletes, a ticket pricing section (Standard $89, Gold $249), and a live medal leaderboard preview.
- **Schedule (/schedule)** — Full event schedule filterable by sport, venue, and date. Each event card shows the sport badge, name, venue, date/time and a heart button to save it as a favourite (login required).
- **Event Detail (/event/:id)** — Event info (sport, venue, date, time, capacity), results table with athlete rankings and medal badges, and a "Book ticket" button (login required). Shows error if already booked or sold out.
- **Leaderboard (/leaderboard)** — Medal table ranking countries by Gold, Silver, Bronze, and Total. Sortable columns.
- **Athletes (/athletes)** — Grid of all athletes, searchable by name or country, filterable by sport. Heart button to follow an athlete (login required).
- **Athlete Profile (/athlete/:id)** — Individual athlete page with sport, country, and bio.
- **Venues (/venues)** — Cards for all competition venues showing name, location, seat capacity, event count, and a link to view on OpenStreetMap. Clicking "X events" opens the Schedule pre-filtered to that venue.
- **My Tickets (/my-tickets)** — Cards for every ticket the logged-in user has booked: sport badge, event name (linked), venue, date, time, and booking date.
- **Profile (/profile/:username)** — Shows role badge (Spectator/Athlete/Staff), member-since date, stats (tickets booked, saved events, following). Own profile also shows: My Tickets section (top 5), Saved Events list (with remove button), Following list (athletes, with unfollow button), and account details.
- **Staff Dashboard (/admin)** — Staff-only panel with a sidebar for: Events (create/delete), Results (record athlete results with medal), Accommodations (create + assign athletes), Sports (add), Venues (add). Accessible via the "Staff" dropdown in the navbar.
- **Register (/register)** — Create account with username, email, password, role, and country.
- **Login (/login)** — Sign in with username and password.
- **Forgot/Reset Password (/forgot-password, /reset-password/:uid/:token)** — Password recovery flow.

## Navbar
- Public: Schedule, Athletes, Leaderboard, Venues, Login, Register.
- Logged in: + Tickets link, username (links to profile), Logout.
- Staff only: + "Staff" dropdown with direct links to each dashboard section.

## User roles
- **Spectator** (default): browse all content, book tickets, save favourite events, follow athletes, use the AI chat.
- **Athlete**: same as Spectator plus own athlete profile (sport, country, bio) shown on the Athletes page.
- **Staff**: all Spectator abilities plus access to the Staff Dashboard to manage events, results, accommodations, sports, and venues.

## Data model
- **Events**: name, sport, venue, start/end time, ticket capacity.
- **Tickets**: one per (user, event) pair — prevents double-booking, checks capacity.
- **Results**: athlete rank, medal (Gold/Silver/Bronze/None), score — linked to an event.
- **Favourites**: a user can favourite an event OR follow an athlete; stored per-user in the database.
- **Accommodations**: housing units with capacity, assigned to athletes by staff.
- **Leaderboard**: aggregated medal counts per country.
- **Athletes**: linked to a user account with sport, country, and bio.
- **Venues**: name, location, seat capacity.

## Your role
- Answer questions about the Olympics 2028, sports, athletes, events, and results.
- Guide users to the right page (e.g. "Go to /schedule to filter events by sport").
- Explain features: booking tickets, saving favourites, viewing the leaderboard, the staff dashboard.
- Provide general knowledge about the Olympic Games, sports rules, and history.
- Be friendly, concise, and enthusiastic about the Olympics.
- If asked about live or real-time data, explain that results are recorded by Staff members via the dashboard.
- Always respond in the same language the user writes in.
"""


def handle_example_message(data: dict) -> None:
    """Message queue handler for "example:messages"

    Receives a user message, sends it to Gemini AI and posts
    the bot reply back to the backend.
    """
    message_id = data["message_id"]
    text       = data.get("text", "")
    username   = data.get("username", "unknown")
    history    = data.get("history", [])
    logger.info("Processing message %s from %s: %s", message_id, username, text)

    # Build conversation history for Gemini
    contents = []
    for turn in history:
        contents.append(types.Content(role="user",  parts=[types.Part(text=turn["user"])]))
        contents.append(types.Content(role="model", parts=[types.Part(text=turn["bot"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=text)]))

    # Call Gemini AI
    try:
        bot_reply = gemini_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        ).text
    except Exception:
        logger.exception("Gemini API error for message %s", message_id)
        bot_reply = "Sorry, I could not process your message right now."

    logger.info("  -> Gemini reply for message %d: %s", message_id, bot_reply[:80])

    # Post reply back to backend
    url      = f"{API_BASE}/api/v1/example-messages/{message_id}/result/"
    payload  = {"bot_reply": bot_reply}
    response = requests.post(url, json=payload, headers=API_HEADERS)
    logger.info("  -> Posted bot reply for message %d (API %s)", message_id, response.status_code)

    redis_publish("example:results", {
        "message_id": message_id,
        "bot_reply":  bot_reply,
        "status":     "processed",
    })


# Register message queue handlers
HANDLERS: dict[str, Callable[[dict], None]] = {
    "example:messages": handle_example_message,
}


def redis_subscribe() -> None:
    """Consume messages from Redis work queues and dispatch to handlers."""
    queues = list(HANDLERS)
    while True:
        try:
            redis_client = redis.from_url(REDIS_URL)
            logger.info("Listening on Redis queues %s ...", queues)
            while True:
                queue, raw = redis_client.brpop(queues, timeout=0)
                queue = queue.decode() if isinstance(queue, bytes) else queue
                try:
                    data    = json.loads(raw)
                    logger.info(f"Redis: received from '{queue}': {data}")
                    otel_ctx = otel_extract_trace_ctx(data)
                    with tracer.start_as_current_span(
                        f"redis_consume:{queue}", context=otel_ctx, kind=trace.SpanKind.CONSUMER
                    ):
                        HANDLERS[queue](data)
                except Exception:
                    logger.exception("Error handling message on %s", queue)
        except Exception:
            logger.exception("Redis connection error, retrying...")
            time.sleep(10)


def redis_publish(queue: str, data: dict) -> None:
    """Publish a message to a Redis work queue."""
    otel_inject_trace_ctx(data)
    redis.from_url(REDIS_URL).lpush(queue, json.dumps(data).encode())
    logger.info("Redis: published to %s: %s", queue, data)


def main():
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(logging.INFO)
    redis_subscribe()


if __name__ == "__main__":
    main()
