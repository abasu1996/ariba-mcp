"""Sourcing Project Management API.

Owner: Pranathi
Prod URL: https://openapi.ariba.com/api/sourcing-project-management/v2/prod

Authentication: OAuth 2.0 Bearer token + apiKey header. These tools use the
Pranathi credential environment variables:
- PRANATHI_CLIENT_ID
- PRANATHI_CLIENT_SECRET
- PRANATHI_API_KEY
- PRANATHI_OAUTH_URL, optional, defaults to https://api.ariba.com

The API also requires user + passwordAdapter query params for user context.
"""

import json
import os
from typing import Any

import httpx
from fastmcp import FastMCP

from ariba_mcp.auth import DirectAuthClient
from ariba_mcp.client import AribaClient
from ariba_mcp.errors import handle_ariba_error

BASE_URL = "https://openapi.ariba.com/api/sourcing-project-management/v2/prod"
DEFAULT_REALM = "BrainBoxDSAPP-T"
DEFAULT_USER = "unnam.pranathi@brainbox.consulting"
DEFAULT_PASSWORD_ADAPTER = "PasswordAdapter1"
DEFAULT_DATE_FILTER = "(createDateFrom gt 1704067200000 and createDateTo lt 1767225600000)"


def _make_auth() -> DirectAuthClient:
    """Create an auth client for the Sourcing Project Management application."""
    return DirectAuthClient(
        client_id=os.getenv("PRANATHI_CLIENT_ID", os.getenv("ARIBA_CLIENT_ID", "")),
        client_secret=os.getenv("PRANATHI_CLIENT_SECRET", os.getenv("ARIBA_CLIENT_SECRET", "")),
        api_key=os.getenv("PRANATHI_API_KEY", os.getenv("ARIBA_API_KEY", "")),
        oauth_url=os.getenv("PRANATHI_OAUTH_URL", os.getenv("ARIBA_OAUTH_URL", "https://api.ariba.com")),
    )


def _realm(realm: str | None) -> str:
    return realm or DEFAULT_REALM


def _date_filter(filter_expr: str | None, from_epoch_ms: int | None, to_epoch_ms: int | None) -> str | None:
    if filter_expr:
        return filter_expr
    if from_epoch_ms is not None and to_epoch_ms is not None:
        return f"(createDateFrom gt {from_epoch_ms} and createDateTo lt {to_epoch_ms})"
    return DEFAULT_DATE_FILTER


def _params(
    client: AribaClient,
    realm: str | None,
    user: str,
    password_adapter: str,
    filter_expr: str | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "realm": _realm(realm),
        "user": user,
        "passwordAdapter": password_adapter,
    }
    if filter_expr:
        params["$filter"] = filter_expr
    if page_token:
        params["pageToken"] = page_token
    return params


async def _get(
    auth: DirectAuthClient,
    path: str,
    params: dict[str, Any],
) -> str:
    headers = await auth.get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"{BASE_URL}/{path.lstrip('/')}",
            headers=headers,
            params=params,
            timeout=60,
        )
        resp.raise_for_status()
    return json.dumps(resp.json(), default=str)


async def _post(
    auth: DirectAuthClient,
    path: str,
    params: dict[str, Any],
    payload: dict[str, Any] | None = None,
) -> str:
    headers = await auth.get_headers()
    headers["Content-Type"] = "application/json"
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"{BASE_URL}/{path.lstrip('/')}",
            headers=headers,
            params=params,
            json=payload or {},
            timeout=60,
        )
        resp.raise_for_status()
    return json.dumps(resp.json(), default=str)


def register(mcp: FastMCP, client: AribaClient) -> None:
    auth = _make_auth()

    @mcp.tool(
        name="ariba_list_sourcing_projects",
        description=(
            "List SAP Ariba sourcing projects. Defaults to realm BrainBoxDSAPP-T, "
            "user unnam.pranathi@brainbox.consulting, passwordAdapter PasswordAdapter1, "
            "and the createDateFrom/createDateTo filter from the provided API URL unless overridden."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_projects(
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        filter_expr: str | None = None,
        from_epoch_ms: int | None = None,
        to_epoch_ms: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """GET /projects."""
        try:
            params = _params(
                client,
                realm,
                user,
                password_adapter,
                _date_filter(filter_expr, from_epoch_ms, to_epoch_ms),
                page_token,
            )
            return await _get(auth, "projects", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project",
        description=(
            "Get a specific SAP Ariba sourcing project by project ID. Defaults to the "
            "BrainBoxDSAPP-T realm and Pranathi user context from the provided API URL."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project(
        project_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """GET /projects/{projectId}."""
        try:
            params = _params(client, realm, user, password_adapter)
            return await _get(auth, f"projects/{project_id}", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_list_sourcing_project_documents",
        description=(
            "List documents for a SAP Ariba sourcing project. Defaults to the "
            "createDateFrom/createDateTo filter from the provided API URL unless overridden."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_project_documents(
        project_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        filter_expr: str | None = None,
        from_epoch_ms: int | None = None,
        to_epoch_ms: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """GET /projects/{projectId}/documents."""
        try:
            params = _params(
                client,
                realm,
                user,
                password_adapter,
                _date_filter(filter_expr, from_epoch_ms, to_epoch_ms),
                page_token,
            )
            return await _get(auth, f"projects/{project_id}/documents", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_get_sourcing_project_team",
        description=(
            "Get a team or project group for a SAP Ariba sourcing project by project ID "
            "and project group/team ID. Supports the optional createDateFrom/createDateTo filter."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_sourcing_project_team(
        project_id: str,
        team_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        filter_expr: str | None = None,
        from_epoch_ms: int | None = None,
        to_epoch_ms: int | None = None,
    ) -> str:
        """GET /projects/{projectId}/teams/{teamId}."""
        try:
            params = _params(
                client,
                realm,
                user,
                password_adapter,
                _date_filter(filter_expr, from_epoch_ms, to_epoch_ms),
            )
            return await _get(auth, f"projects/{project_id}/teams/{team_id}", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_list_sourcing_project_history_records",
        description=(
            "List history records for a SAP Ariba sourcing project. Defaults to the "
            "createDateFrom/createDateTo filter from the provided API URL unless overridden."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_project_history_records(
        project_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        filter_expr: str | None = None,
        from_epoch_ms: int | None = None,
        to_epoch_ms: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """GET /projects/{projectId}/historyRecords."""
        try:
            params = _params(
                client,
                realm,
                user,
                password_adapter,
                _date_filter(filter_expr, from_epoch_ms, to_epoch_ms),
                page_token,
            )
            return await _get(auth, f"projects/{project_id}/historyRecords", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_list_sourcing_project_team_users",
        description=(
            "List users for a SAP Ariba sourcing project team by project ID and "
            "project group/team ID."
            "Ask the user to provide an Unique Name and Password Adapter to pass it as a payload in the POST request body to get the user details in response. Like below:" 
            """[
                {
                    "uniqueName": f"email Address of user",
                    "passwordAdapter": "PasswordAdapter1"
                }
                ]"""
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_project_team_users(
        project_id: str,
        team_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        page_token: str | None = None,
        payload: str | None = None,
    ) -> str:
        """POST /projects/{projectId}/teams/{teamId}/users."""
        try:
            params = _params(client, realm, user, password_adapter, page_token=page_token)
            return await _post(auth, f"projects/{project_id}/teams/{team_id}/users", params,payload=json.loads(payload) if payload else None)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_list_sourcing_project_tasks",
        description=(
            "List tasks for a SAP Ariba sourcing project. Defaults to the "
            "createDateFrom/createDateTo filter from the provided API URL unless overridden."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_sourcing_project_tasks(
        project_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        filter_expr: str | None = None,
        from_epoch_ms: int | None = None,
        to_epoch_ms: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """GET /projects/{projectId}/tasks."""
        try:
            params = _params(
                client,
                realm,
                user,
                password_adapter,
                _date_filter(filter_expr, from_epoch_ms, to_epoch_ms),
                page_token,
            )
            return await _get(auth, f"projects/{project_id}/tasks", params)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_create_sourcing_project",
        description=(
            "Create a new SAP Ariba sourcing project. Pass project_data as a JSON string "
            "with project details and provide user-context parameters."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def create_sourcing_project(
        project_data: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /projects."""
        try:
            payload = json.loads(project_data)
            headers = await auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.post(
                    f"{BASE_URL}/projects",
                    headers=headers,
                    params=_params(client, realm, user, password_adapter),
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_update_sourcing_project",
        description=(
            "Update an existing SAP Ariba sourcing project. Pass project_data as a JSON "
            "string containing the fields to update and provide user-context parameters."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def update_sourcing_project(
        project_id: str,
        project_data: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """PUT /projects/{projectId}."""
        try:
            payload = json.loads(project_data)
            headers = await auth.get_headers()
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as http:
                resp = await http.put(
                    f"{BASE_URL}/projects/{project_id}",
                    headers=headers,
                    params=_params(client, realm, user, password_adapter),
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
            return json.dumps(resp.json(), default=str)
        except Exception as e:
            return handle_ariba_error(e)
