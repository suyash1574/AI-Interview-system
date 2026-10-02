class AutergoError(Exception):
    pass

class AuthorizationError(AutergoError):
    pass

class StateTransitionError(AutergoError):
    """Raised when an invalid state transition is attempted."""
    pass
