import jwt
from datetime import datetime, timedelta, timezone
from backend.config import settings
from backend.core.errors import AuthorizationError

def generate_guest_token(candidate_id: str, interview_id: str) -> str:
    payload = {
        "sub": candidate_id,
        "interview_id": interview_id,
        "role": "CANDIDATE",
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, settings.GUEST_SECRET_KEY, algorithm="HS256")
    return token

def verify_guest_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.GUEST_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthorizationError("Guest token expired")
    except jwt.InvalidTokenError:
        raise AuthorizationError("Invalid guest token")
