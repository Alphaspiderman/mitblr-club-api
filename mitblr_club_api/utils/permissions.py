"""Permission management and scoping for all classes."""
from enum import Enum

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic.log import logger

from mitblr_club_api.models.club_teams import ClubTeam
from mitblr_club_api.utils.exceptions import ClubTeamNotFoundException

# Maximum length of queries accepted.
MAX_LENGTH: int = 100


class Permission(Enum):
    """All permissions within the database as enum strings and all permissions."""

    CREATE_EVENT = "create_event"
    MODIFY_EVENT = "modify_event"
    DELETE_EVENT = "delete_event"
    GET_EVENT = "get_event"
    MARK_ATTENDANCE = "mark_attendance"
    MODIFY_ATTENDANCE = "modify_attendance"
    ALL = "all"


async def check_permission(
    collection: AsyncIOMotorCollection, student_id: ObjectId, permission: Permission
) -> bool:
    """Check the permissions given to a student within the club teams.

    Args:
        collection (AsyncIOMotorCollection): Database collection in which student ID is queried.
        student_id (ObjectId): Mongo ObjectId for the student in the Club Teams.
        permission (Permission): Permissions to check on the Club Teams.

    Raises:
        ClubTeamNotFoundException: When no Club Team with the given student_id exists.

    Returns:
        True if the permissions in the database match the permission parameter; else False.
    """

    club_teams = await collection.find({"student_id": student_id}).to_list(MAX_LENGTH)

    if len(club_teams) == 0:
        raise ClubTeamNotFoundException(f"No club team with the student id: {student_id} exists.")

    if len(club_teams) != 1:
        logger.warn(
            f"The club team does not refer to a unique student ID. Got {len(club_teams)} number of records."
        )

    for key, value in club_teams[0].items():
        if type(value) is ObjectId:
            club_teams[0][key] = str(value)

    club_team = ClubTeam(**club_teams[0])

    match permission:
        case Permission.ALL:
            return all(club_team.permissions.values())

        case _:
            return club_team.permissions[permission.value]
