"""
Permission management and scoping for all classes.
"""
from enum import Enum

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic.log import logger

from mitblr_club_api.models.exceptions import ClubTeamNotFoundException
from mitblr_club_api.models.internal.team import Team


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
    """
    Check the permissions given to a student within the club teams.

    :param collection: Database collection in which student ID is queried.
    :type collection: AsyncIOMotorCollection
    :param student_id: Mongo ObjectId for thr student in the club teams.
    :type student_id: ObjectId
    :param permission: Permissions to check for the club teams.
    :type permission: Permission

    :raises ClubTeamNotFoundException: When no club team with the given `student_id` exists.

    :return: True if the permissions in the database match the permission parameter; else False.
    :rtype: bool
    """

    club_teams = await collection.find({"student_id": student_id}).to_list(length=5)

    if len(club_teams) == 0:
        raise ClubTeamNotFoundException(
            f"No club team with the student id: {student_id} exists."
        )

    if len(club_teams) != 1:
        logger.warn(
            f"The club team does not refer to a unique student ID. Got {len(club_teams)} number of records."
        )

    for key, value in club_teams[0].items():
        if type(value) is ObjectId:
            club_teams[0][key] = str(value)

    club_team = Team(**club_teams[0])

    match permission:
        case Permission.ALL:
            return all(club_team.permissions.values())

        case _:
            return club_team.permissions[permission.value]
