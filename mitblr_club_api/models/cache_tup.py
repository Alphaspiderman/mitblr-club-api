"""The name dictionary used for holding the different caches."""

from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from cachetools import TTLCache
from motor.motor_asyncio import AsyncIOMotorDatabase
from sanic.log import logger

from mitblr_club_api.models.cached.clubs import ClubCache
from mitblr_club_api.models.cached.events import EventCache
from mitblr_club_api.models.cached.students import StudentCache
from mitblr_club_api.models.cached.team import TeamCache


class Cache:
    def __init__(self, db: AsyncIOMotorDatabase, sort_year: int):
        self.db = db
        self.sort_year = sort_year

        self._student_cache: TTLCache = TTLCache(maxsize=200, ttl=3600)
        self._team_cache: TTLCache = TTLCache(maxsize=100, ttl=2.5 * 3600)
        self._club_cache: TTLCache = TTLCache(maxsize=100, ttl=3.5 * 3600)
        self._event_cache: TTLCache = TTLCache(maxsize=25, ttl=3.5 * 3600)

        # Note - Club and Events are Cached for 3.5h but refreshed every 3h

    async def get_student(self, student_id: int) -> Optional[StudentCache]:
        """Get the student from the cache (by UUID)."""

        student = self._student_cache.get(student_id)

        if student:
            logger.debug(f"Cache Hit - Student - {student_id}")
        else:
            student_doc = await self.db["students"].find_one(
                {
                    "$or": [
                        {"application_number": student_id},
                        {"registration_number": student_id},
                    ]
                }
            )

            if student_doc:
                logger.debug(f"Cache Miss - Student - {student_id}")
                student = StudentCache(**student_doc)
                self._student_cache[student_id] = student
            else:
                return None

        return student

    async def fetch_student(self, student_id: int) -> Optional[StudentCache]:
        """Fetch the student from the database (by UUID) and saves to cache."""

        student_doc = await self.db["students"].find_one(
            {
                "$or": [
                    {"application_number": student_id},
                    {"registration_number": student_id},
                ]
            }
        )

        if student_doc:
            student = StudentCache(**student_doc)
            self._student_cache[student_id] = student
            return student

        return None

    async def get_team(self, team_id: str) -> Optional[TeamCache]:
        """Get the team from the cache (by Team ID)."""

        team = self._team_cache.get(team_id)

        if team:
            logger.debug(f"Cache Hit - Team - {team_id}")
        else:
            team_doc = await self.db["club_teams"].find_one({"_id": ObjectId(team_id)})

            if team_doc:
                logger.debug(f"Cache Miss - Team - {team_id}")
                team = TeamCache(**team_doc)
                self._team_cache[team_id] = team
            else:
                return None

        return team

    async def fetch_team(self, team_id: str) -> Optional[TeamCache]:
        """Fetches the team from the database (by Team ID) and saves to cache."""

        team_doc = await self.db["club_teams"].find_one({"_id": ObjectId(team_id)})

        if team_doc:
            team = TeamCache(**team_doc)
            self._team_cache[team_id] = team
            return team

        return None

    async def get_club(self, club_id: str) -> Optional[ClubCache]:
        """Get the club from the cache (by Slug)."""

        club = self._club_cache.get(club_id)

        if club:
            logger.debug(f"Cache Hit - Club - {club_id}")
        else:
            club_doc = await self.db["clubs"].find_one({"slug": club_id})

            if club_doc:
                logger.debug(f"Cache Miss - Club - {club_id}")
                club = ClubCache(**club_doc)
                self._club_cache[club_id] = club
            else:
                return None

        return club

    def get_clubs(self) -> list[ClubCache]:
        """Get all clubs from the cache."""

        return list(self._club_cache.values())

    async def fetch_club(self, club_id: str) -> Optional[ClubCache]:
        """Fetches the club from the cache (by Slug) and saves to cache."""

        club_doc = await self.db["clubs"].find_one({"slug": club_id})

        if club_doc:
            club = ClubCache(**club_doc)
            self._club_cache[club_id] = club
            return club

        return None

    async def refresh_clubs(self):
        """Refreshes the cache of clubs."""

        clubs = await self.db["clubs"].find({}).to_list(length=1000)

        for club in clubs:
            self._club_cache[club["slug"]] = ClubCache(**club)

    async def get_event(self, event_id: str, year: int = None) -> Optional[EventCache]:
        """Get the event from the cache (by Slug)."""
        if year is None:
            year = self.sort_year

        event = self._event_cache.get(event_id)

        if event:
            logger.debug(f"Cache Hit - Event - {event_id}")
        else:
            event_doc = await self.db["events"].find_one(
                {"$and": [{"slug": event_id}, {"sort_year": str(year)}]}
            )

            if event_doc:
                logger.debug(f"Cache Miss - Event - {event_id}")
                event = EventCache(**event_doc)
                self._event_cache[event_id] = event
            else:
                return None

        return event

    async def fetch_event(
        self, event_id: str, year: int = None
    ) -> Optional[EventCache]:
        """Fetches the event from the cache (by Slug) and saves to cache."""
        if year is None:
            year = self.sort_year

        event_doc = await self.db["events"].find_one(
            {"$and": [{"slug": event_id}, {"sort_year": str(year)}]}
        )

        if event_doc:
            event = EventCache(**event_doc)
            self._event_cache[event_id] = event
            return event

        return None

    async def refresh_events(self):
        """Refreshes the event cache."""
        year = self.sort_year
        events = await self.db["events"].find({"sort_year": str(year)}).to_list(1000)

        for event_doc in events:
            self._event_cache[event_doc["slug"]] = EventCache(**event_doc)

    async def get_event_by_timedelta(
        self, delta: int = 7
    ) -> Optional[list[EventCache]]:
        """Returns a list of events that occur within a specified timedelta."""

        start_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = start_date + timedelta(days=delta)

        data = []

        for event in self._event_cache.values():
            if start_date <= event.date <= end_date:
                data.append(event)

        return None if len(data) == 0 else data
