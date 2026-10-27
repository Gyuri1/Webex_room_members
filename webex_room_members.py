#!/usr/bin/env python3
"""
List the email addresses of all members in a Webex room.

Usage:
  python webex_room_members.py --room-id <ROOM_ID>
  python webex_room_members.py --room-title "My Room Name"
  python webex_room_members.py --list-rooms
"""

import argparse
import os
import sys
import time

import requests

BASE_URL = "https://webexapis.com/v1"


def get_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    return s


def paged_get(session: requests.Session, url: str, params: dict | None = None):
    """Yield items from a paginated Webex API endpoint (follows the 'Link: rel=next' header)."""
    while url:
        resp = session.get(url, params=params, timeout=30)

        # Handle rate limiting
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 5))
            print(f"Rate limited, retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue

        if not resp.ok:
            sys.exit(f"API error {resp.status_code}: {resp.text}")

        yield from resp.json().get("items", [])

        url = resp.links.get("next", {}).get("url")
        params = None  # the 'next' URL already contains the query parameters


def list_rooms(session: requests.Session):
    return list(paged_get(session, f"{BASE_URL}/rooms", {"max": 1000}))


def find_room_id_by_title(session: requests.Session, title: str) -> str:
    matches = [r for r in list_rooms(session) if r.get("title", "").lower() == title.lower()]
    if not matches:
        sys.exit(f"No room found with title: {title}")
    if len(matches) > 1:
        print("Multiple rooms match this title, using the first one:", file=sys.stderr)
        for r in matches:
            print(f"  {r['id']}  {r['title']}", file=sys.stderr)
    return matches[0]["id"]


def get_member_emails(session: requests.Session, room_id: str) -> list[str]:
    members = paged_get(session, f"{BASE_URL}/memberships", {"roomId": room_id, "max": 1000})
    emails = {m["personEmail"] for m in members if m.get("personEmail")}
    return sorted(emails, key=str.lower)


def main():
    parser = argparse.ArgumentParser(description="List member emails of a Webex room.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--room-id", help="Webex room ID")
    group.add_argument("--room-title", help="Exact room title (case-insensitive)")
    group.add_argument("--list-rooms", action="store_true", help="List your rooms and their IDs")
    parser.add_argument("--output", help="Optional output file (one email per line)")
    args = parser.parse_args()

    token = os.getenv("WEBEX_TOKEN")
    if not token:
        sys.exit("Please set the WEBEX_TOKEN environment variable.")

    session = get_session(token)

    if args.list_rooms:
        for r in list_rooms(session):
            print(f"{r['id']}\t{r.get('title', '')}")
        return

    room_id = args.room_id or find_room_id_by_title(session, args.room_title)
    emails = get_member_emails(session, room_id)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(emails) + "\n")
        print(f"{len(emails)} email(s) written to {args.output}")
    else:
        print("\n".join(emails))
        print(f"\nTotal: {len(emails)} member(s)", file=sys.stderr)


if __name__ == "__main__":
    main()