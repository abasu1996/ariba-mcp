from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ariba_mcp.server import mcp


def _http_path() -> str:
    path = os.getenv("MCP_HTTP_PATH", "/mcp").strip() or "/mcp"
    if not path.startswith("/"):
        return f"/{path}"
    return path


class RootRedirect:
    """Redirect the bare app route to the configured MCP endpoint."""

    def __init__(self, wrapped_app, location: str) -> None:
        self._wrapped_app = wrapped_app
        self._location = location

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http" and scope.get("path") in ("", "/"):
            await send(
                {
                    "type": "http.response.start",
                    "status": 307,
                    "headers": [(b"location", self._location.encode("ascii"))],
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        await self._wrapped_app(scope, receive, send)


_mcp_path = _http_path()
app = RootRedirect(mcp.http_app(path=_mcp_path), _mcp_path)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
