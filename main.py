"""WeLink Radar — FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path

from core.config import read_config
from core.database import get_db
from core.templates import templates
from core.exceptions import register_exception_handlers

import routes.setup as setup_routes
import routes.stats as stats_routes
import routes.dates as dates_routes
import routes.dbinfo as dbinfo_routes
import routes.sessions as sessions_routes
import routes.group_detail as group_detail_routes
import routes.group_tags as group_tags_routes
import routes.groups as groups_routes
import routes.mentions as mentions_routes
import routes.topics as topics_routes
import routes.links as links_routes
import routes.search as search_routes
import routes.ai_classify as ai_classify_routes
import routes.rescan as rescan_routes
import routes.new_messages as new_messages_routes
import routes.recover as recover_routes
import routes.daemon as daemon_routes

app = FastAPI(
    title="WeLink Radar",
    description="Local-first WeLink group intelligence dashboard",
    version="0.1.0",
)

# Global exception handlers
register_exception_handlers(app)

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ── API Routes ────────────────────────────────────────────────────────────────

app.include_router(setup_routes.router)
app.include_router(stats_routes.router)
app.include_router(dates_routes.router)
app.include_router(dbinfo_routes.router)
app.include_router(sessions_routes.router)
app.include_router(group_detail_routes.router)
app.include_router(group_tags_routes.router)
app.include_router(groups_routes.router)
app.include_router(mentions_routes.router)
app.include_router(topics_routes.router)
app.include_router(links_routes.router)
app.include_router(search_routes.router)
app.include_router(ai_classify_routes.router)
app.include_router(rescan_routes.router)
app.include_router(new_messages_routes.router)
app.include_router(recover_routes.router)
app.include_router(daemon_routes.router)

# ── Page Routes ───────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def page_dashboard(request: Request):
    """Main dashboard page."""
    config = read_config()
    if not config.setupCompleted or not config.privacyConfirmed:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/dashboard.html", {"request": request, "config": config})


@app.get("/setup", response_class=HTMLResponse)
async def page_setup(request: Request):
    """Setup wizard page."""
    return templates.TemplateResponse("pages/setup.html", {"request": request})


@app.get("/groups", response_class=HTMLResponse)
async def page_groups(request: Request):
    """Groups list page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/groups.html", {"request": request, "config": config})


@app.get("/groups/{conv_id}", response_class=HTMLResponse)
async def page_group_detail(request: Request, conv_id: str):
    """Single group detail page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/group_detail.html",
                                       {"request": request, "config": config, "conv_id": conv_id})


@app.get("/classify", response_class=HTMLResponse)
async def page_classify(request: Request):
    """AI classification page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/classify.html", {"request": request, "config": config})


@app.get("/links", response_class=HTMLResponse)
async def page_links(request: Request):
    """Link intelligence page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/links.html", {"request": request, "config": config})


@app.get("/mentions", response_class=HTMLResponse)
async def page_mentions(request: Request):
    """Mentions page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/mentions.html", {"request": request, "config": config})


@app.get("/topics", response_class=HTMLResponse)
async def page_topics(request: Request):
    """Topics radar page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/topics.html", {"request": request, "config": config})


@app.get("/reports/groups/{conv_id}", response_class=HTMLResponse)
async def page_report(request: Request, conv_id: str):
    """Daily group report page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/report.html",
                                       {"request": request, "config": config, "conv_id": conv_id})


@app.get("/signals", response_class=HTMLResponse)
async def page_signals(request: Request):
    """Live signals page."""
    config = read_config()
    if not config.setupCompleted:
        return RedirectResponse(url="/setup")
    return templates.TemplateResponse("pages/signals.html", {"request": request, "config": config})


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    get_db()  # Triggers schema creation and migration

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
