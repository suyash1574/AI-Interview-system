from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.services.tokens import generate_guest_token

router = APIRouter(prefix="/invitations", tags=["invitations"])

class GenerateTokenRequest(BaseModel):
    candidate_id: str
    interview_id: str

class GenerateTokenResponse(BaseModel):
    token: str

@router.post("/generate", response_model=GenerateTokenResponse)
def generate_token(request: GenerateTokenRequest):
    try:
        token = generate_guest_token(request.candidate_id, request.interview_id)
        return GenerateTokenResponse(token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
