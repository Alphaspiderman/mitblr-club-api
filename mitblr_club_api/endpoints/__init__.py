"""Package for API endpoints."""
from mitblr_club_api.app import appserver

# Students
from .students import Students

# Clubs
from .clubs.base import Clubs

# Events
from .events.base import Events
from .events.attend import Events_Attend

# Add Routes for Students
appserver.add_route(
    Students.as_view(), "/students/<uuid:strorempty>", strict_slashes=False
)


# Add Routes for Clubs
appserver.add_route(
    Clubs.as_view(), "/clubs/<club_slug:strorempty>", strict_slashes=False
)

# Add Routes for Events
appserver.add_route(
    Events.as_view(), "/events/<event_slug:strorempty>", strict_slashes=False
)
appserver.add_route(
    Events_Attend.as_view(),
    "/events/<slug:str>/attend/<uuid:int>",
    strict_slashes=False,
)
