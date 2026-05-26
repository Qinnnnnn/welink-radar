"""Setup wizard routes — initial configuration."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.config import config_status, write_config, ConfigModel
from models.schemas import ConfigModel as ConfigSchema

router = APIRouter(prefix="/api/setup", tags=["setup"])


class SetupPayload(BaseModel):
    myNicknames: list[str] = []
    privacyConfirmed: bool = False
    demoMode: bool = False
    defaultSyncDays: int = 90


@router.get("")
async def get_setup():
    """Return current setup status, config, and environment checks."""
    status = config_status()
    return status


@router.post("")
async def post_setup(payload: SetupPayload):
    """Save configuration and optionally seed demo data."""
    config = write_config({
        "myNicknames": payload.myNicknames,
        "privacyConfirmed": payload.privacyConfirmed,
        "setupCompleted": True,
        "demoMode": payload.demoMode,
        "defaultSyncDays": payload.defaultSyncDays,
    })

    result = {"ok": True, "configured": True, "config": config.model_dump()}

    # Seed demo data if requested
    if payload.demoMode:
        from scripts.seed_demo import seed_demo_data
        seed_demo_data()
        result["demo"] = "seeded"

    return result
