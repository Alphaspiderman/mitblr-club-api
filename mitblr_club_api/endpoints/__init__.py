"""Package for API endpoints."""
from mitblr_club_api.app import appserver

from .students import Students

from .clubs.base import Clubs
from .clubs.core import ClubsCore
from .clubs.events import ClubEvents

from .events.base import Events
from .events.attend import EventsAttend

# Maximum length of queries accepted.
MAX_LENGTH: int = 100

appserver.add_route(
    Students.as_view(), "/students/<uuid:strorempty>", strict_slashes=False
)

appserver.add_route(
    Clubs.as_view(), "/clubs/<club_slug:strorempty>", strict_slashes=False
)

appserver.add_route(
    ClubsCore.as_view(), "/clubs/<club_slug:str>/core", strict_slashes=False
)

appserver.add_route(
    ClubEvents.as_view(),
    "/clubs/<club_slug:str>/events/<event_slug:strorempty>",
    strict_slashes=False,
)

appserver.add_route(
    Events.as_view(), "/events/<event_slug:strorempty>", strict_slashes=False
)

appserver.add_route(
    EventsAttend.as_view(), "/events/<slug:str>/attend/<uuid:int>",
    strict_slashes=False,
)
