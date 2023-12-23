"""Package for API endpoints."""
from mitblr_club_api.app import appserver

from .students import Students

from .clubs.base import Clubs
from .clubs.core import ClubsCore
from .clubs.events import ClubEvents

from .events.base import Events
from .events.attend import EventsAttend
from .events.register import EventsRegister

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
    EventsAttend.as_view(),
    "/events/<slug:str>/attend/<uuid:int>",
    strict_slashes=False,
)

appserver.add_route(
    EventsRegister.as_view(),
    "/events/<slug:str>/register/<uuid:int>",
    strict_slashes=False,
)
