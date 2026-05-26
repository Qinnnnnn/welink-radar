"""Jinja2 template rendering for WeLink Radar.

Uses jinja2.Environment directly (instead of Starlette's Jinja2Templates)
to avoid a cache bug in Jinja2 3.1.6 with the Starlette wrapper.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class Templates:
    """Minimal template renderer compatible with FastAPI route signatures."""

    def TemplateResponse(
        self, name: str, context: dict, status_code: int = 200
    ) -> HTMLResponse:
        template = _jinja_env.get_template(name)
        return HTMLResponse(template.render(**context), status_code=status_code)


templates = Templates()
