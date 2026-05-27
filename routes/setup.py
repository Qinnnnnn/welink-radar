"""Setup wizard routes — initial configuration."""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from core.config import config_status, write_config

router = APIRouter(prefix="/api/setup", tags=["setup"])


@router.get("")
async def get_setup():
    """Return current setup status, config, and environment checks."""
    status = config_status()
    return status


@router.post("")
async def post_setup(myNicknames: str = Form(default="")):
    """Save configuration and redirect to digest page."""
    nicknames = [n.strip() for n in myNicknames.split(",") if n.strip()] if myNicknames else []

    write_config({
        "myNicknames": nicknames,
        "privacyConfirmed": True,
        "setupCompleted": True,
        "demoMode": False,
    })

    return JSONResponse(
        content={"ok": True},
        headers={"HX-Redirect": "/digest"},
    )
