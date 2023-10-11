"""
Custom exceptions for the API.
"""


class DocumentNotFoundException(BaseException):
    """
    Custom exception when a MongoDB document is not found.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ClubTeamNotFoundException(DocumentNotFoundException):
    """
    Exception raised when a Club Team document is not found.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
