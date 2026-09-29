class GameException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ForbiddenException(Exception):
    """Raised when a request is unauthenticated or lacks the required role."""
