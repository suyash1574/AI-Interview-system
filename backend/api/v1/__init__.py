from fastapi import APIRouter
from backend.api.v1.invitations import router as invitations_router
from backend.api.v1.sessions import router as sessions_router
from backend.api.v1.jobs import router as jobs_router
from backend.api.v1.drives import router as drives_router
from backend.api.v1.interviews import router as interviews_router
from backend.api.v1.resumes import router as resumes_router
from backend.api.v1.realtime import router as realtime_router
from backend.api.v1.evaluations import router as evaluations_router
from backend.api.v1.reports import router as reports_router
from backend.api.v1.companies import router as companies_router

router = APIRouter()
router.include_router(invitations_router, prefix="/invitations", tags=["Invitations"])
router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
router.include_router(drives_router, prefix="/drives", tags=["Drives"])
router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
router.include_router(realtime_router, prefix="/realtime", tags=["Realtime"])
router.include_router(evaluations_router, prefix="/evaluations", tags=["Evaluations"])
router.include_router(reports_router, prefix="/reports", tags=["Reports"])
router.include_router(companies_router, prefix="/companies", tags=["Companies"])

