"""Daemon/status check route — checks welink-cli and nga availability."""

from fastapi import APIRouter
from clients.welink import check_cli, get_auth_status
from clients.nga import check_nga

router = APIRouter(prefix="/api/daemon", tags=["daemon"])


@router.get("")
async def daemon_status():
    """Return tool availability and auth status."""
    welink_ok = await check_cli()
    nga_ok = await check_nga()
    auth = await get_auth_status()

    return {
        "ok": True,
        "welink_cli": {
            "available": welink_ok,
            "authenticated": auth.get("authenticated", False),
        },
        "nga": {
            "available": nga_ok,
        },
        "mode": "mock" if not welink_ok else "live",
    }
