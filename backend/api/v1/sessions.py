from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit.api import AccessToken, VideoGrants
from backend.config import settings

router = APIRouter(tags=["sessions"])

class TokenRequest(BaseModel):
    room_name: str
    participant_name: str
    participant_identity: str

class TokenResponse(BaseModel):
    token: str

@router.post("/livekit-token", response_model=TokenResponse)
async def create_livekit_token(request: TokenRequest):
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="LiveKit credentials are not configured")

    try:
        token = (
            AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(request.participant_identity)
            .with_name(request.participant_name)
            .with_grants(VideoGrants(room_join=True, room=request.room_name))
            .to_jwt()
        )
        return TokenResponse(token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
