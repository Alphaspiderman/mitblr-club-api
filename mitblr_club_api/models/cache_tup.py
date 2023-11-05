"""
The name dictionary used for holding the different caches
"""
from datetime import datetime, timedelta
from typing import Optional
from cachetools import TTLCache
from sanic.log import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from mitblr_club_api.models.internal.students import Student
from mitblr_club_api.models.internal.team import Team
from mitblr_club_api.models.internal.events import Event
from mitblr_club_api.models.internal.clubs import Club
from bson import ObjectId


class Cache:
    def __init__(self, db: AsyncIOMotorDatabase, sort_year: int):
        self.db = db
        self.sort_year = sort_year
        # Cache upto 200 Student IDs for 1 hour
        self._student_cache: TTLCache = TTLCache(maxsize=200, ttl=3600)

        # Cache upto 100 Team members and their permissions for 2.5 hours
        self._team_cache: TTLCache = TTLCache(maxsize=100, ttl=2.5 * 3600)

        # Cache for Club objects for 1 hour
        self._club_cache: TTLCache = TTLCache(maxsize=50, ttl=3600)

        # Cache for Event objects for 1 hour
        self._event_cache: TTLCache = TTLCache(maxsize=25, ttl=3600)

    async def get_student(self, student_id: int) -> Optional[Student]:
        """
        Get the student from the cache (by UUID)
        """
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
                student = Student(student_doc)
                self._student_cache[student_id] = student
            else:
                return None
        return student

    async def fetch_student(self, student_id: int) -> Optional[Student]:
        """
        Fetch the student from the database (by UUID) and saves to cache
        """
        student_doc = await self.db["students"].find_one(
            {
                "$or": [
                    {"application_number": student_id},
                    {"registration_number": student_id},
                ]
            }
        )
        if student_doc:
            student = Student(student_doc)
            self._student_cache[student_id] = student
            return student
        return None

    async def get_team(self, team_id: str) -> Optional[Team]:
        """
        Get the team from the cache (by Team ID)
        """
        team = self._team_cache.get(team_id)
        if team:
            logger.debug(f"Cache Hit - Team - {team_id}")
        else:
            team_doc = await self.db["club_teams"].find_one({"_id": ObjectId(team_id)})
            if team_doc:
                logger.debug(f"Cache Miss - Team - {team_id}")
                team = Team(**team_doc)
                self._team_cache[team_id] = team
            else:
                return None
        return team

    async def fetch_team(self, team_id: str) -> Optional[Team]:
        """
        Fetches the team from the database (by Team ID) and saves to cache
        """
        team_doc = await self.db["club_teams"].find_one({"_id": ObjectId(team_id)})
        if team_doc:
            team = Team(**team_doc)
            self._team_cache[team_id] = team
            return team
        return None

    async def get_club(self, club_id: str) -> Optional[Club]:
        """
        Get the club from the cache (by Slug)
        """
        club = self._club_cache.get(club_id)
        if club:
            logger.debug(f"Cache Hit - Club - {club_id}")
        else:
            club_doc = await self.db["clubs"].find_one({"slug": club_id})
            if club_doc:
                logger.debug(f"Cache Miss - Club - {club_id}")
                club = Club(club_doc)
                self._club_cache[club_id] = club
            else:
                return None
        return club
    
    async def fetch_club(self, club_id: str) -> Optional[Club]:
        """
        Fetches the club from the cache (by Slug) and saves to cache
        """
        club_doc = await self.db["clubs"].find_one({"slug": club_id})
        if club_doc:
            club = Club(club_doc)
            self._club_cache[club_id] = club
            return club
        return None

    async def get_event(self, event_id: str, year: int = None) -> Optional[Event]:
        """
        Get the event from the cache (by Slug)
        """
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
                event = Event(event_doc)
                self._event_cache[event_id] = event
            else:
                return None
        return event

    async def fetch_event(self, event_id: str, year: int = None) -> Optional[Event]:
        """
        Fetches the event from the cache (by Slug) and saves to cache
        """
        if year is None:
            year = self.sort_year
        event_doc = await self.db["events"].find_one(
            {"$and": [{"slug": event_id}, {"sort_year": str(year)}]}
        )
        if event_doc:
            event = Event(event_doc)
            self._event_cache[event_id] = event
            return event
        return None

    async def get_event_by_timedelta(self, delta: int = 7) -> Optional[list[Event]]:
        """
        Returns a list of events that occur within a specified timedelta.
        """
        start_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = start_date + timedelta(days=delta)

        data = []

        for event_id, event in self._event_cache.values():
            if start_date <= event.date <= end_date:
                data.append(event)

        if len(data) == 0:
            return None
        return data
