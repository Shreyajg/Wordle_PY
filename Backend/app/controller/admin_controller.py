from datetime import date as Date

from fastapi import APIRouter, Depends, Query

from app.config.dependencies import get_admin_service
from app.config.security_config import require_roles
from app.controller.schemas import AdminResponse, AdminUserResponse
from app.model.enums import Role
from app.service.admin_service import AdminService

router = APIRouter(prefix="/admin", dependencies=[Depends(require_roles(Role.ADMIN))])


@router.get("/daily-report", response_model=AdminResponse)
async def get_daily_report(
    date: Date = Query(...),
    admin_service: AdminService = Depends(get_admin_service),
):
    return await admin_service.get_daily_report(date)


@router.get("/user-report/{playerId}", response_model=AdminUserResponse)
async def get_user_report(
    playerId: str,
    date: Date = Query(...),
    admin_service: AdminService = Depends(get_admin_service),
):
    return await admin_service.get_user_report(playerId, date)
