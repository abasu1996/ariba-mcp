"""Sourcing Event Management API.

Owner: Anim
Prod URL: https://openapi.ariba.com/api/sourcing-event/v2/prod

Authentication: OAuth 2.0 Bearer token + apiKey header. These tools use the
event management credential environment variables:
- EVENT_MANAGEMENT_CLIENT_ID
- EVENT_MANAGEMENT_CLIENT_SECRET
- EVENT_MANAGEMENT_API_KEY
- EVENT_MANAGEMENT_OAUTH_URL, optional, defaults to https://api.ariba.com

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

BASE_URL = "https://openapi.ariba.com/api/sourcing-event/v2/prod"
DEFAULT_REALM = "BrainBoxDSAPP-T"
DEFAULT_USER = "unnam.pranathi@brainbox.consulting"
DEFAULT_PASSWORD_ADAPTER = "PasswordAdapter1"


def _make_auth() -> DirectAuthClient:
    """Create an auth client for the Sourcing Event Management application."""
    return DirectAuthClient(
        client_id=os.getenv("EVENT_MANAGEMENT_CLIENT_ID", os.getenv("ARIBA_CLIENT_ID", "")),
        client_secret=os.getenv("EVENT_MANAGEMENT_CLIENT_SECRET", os.getenv("ARIBA_CLIENT_SECRET", "")),
        api_key=os.getenv("EVENT_MANAGEMENT_API_KEY", os.getenv("ARIBA_API_KEY", "")),
        oauth_url=os.getenv("EVENT_MANAGEMENT_OAUTH_URL", os.getenv("ARIBA_OAUTH_URL", "https://api.ariba.com")),
    )


def _params(
    realm: str | None,
    user: str,
    password_adapter: str,
    page_token: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "realm": realm or DEFAULT_REALM,
        "user": user,
        "passwordAdapter": password_adapter,
    }
    if page_token:
        params["pageToken"] = page_token
    return params


async def _request(
    auth: DirectAuthClient,
    method: str,
    path: str,
    params: dict[str, Any],
    payload: Any | None = None,
) -> str:
    headers = await auth.get_headers()
    if payload is not None:
        headers["Content-Type"] = "application/json"

    async with httpx.AsyncClient() as http:
        resp = await http.request(
            method,
            f"{BASE_URL}/{path.lstrip('/')}",
            headers=headers,
            params=params,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()

    if not resp.content:
        return json.dumps({"status": resp.status_code})
    return json.dumps(resp.json(), default=str)


def _json_payload(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"payload must be valid JSON: {e}") from e


def register(mcp: FastMCP, client: AribaClient) -> None:
    auth = _make_auth()

    @mcp.tool(
        name="ariba_event_list_items",
        description=(
            "List items for a SAP Ariba sourcing event. Defaults to realm BrainBoxDSAPP-T "
            "and the Pranathi user context from the spreadsheet."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_event_items(
        event_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        page_token: str | None = None,
    ) -> str:
        """GET /events/{eventId}/items."""
        try:
            return await _request(
                auth,
                "GET",
                f"events/{event_id}/items",
                _params(realm, user, password_adapter, page_token),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_items",
        description=(
            "Add items to a SAP Ariba sourcing event. Pass items_json as the JSON array body "
            "expected by the sourcing-event API."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_event_items(
        event_id: str,
        items_json: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /events/{eventId}/items."""
        try:
            return await _request(
                auth,
                "POST",
                f"events/{event_id}/items",
                _params(realm, user, password_adapter),
                _json_payload(items_json),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_create",
        description=(
            "Create a SAP Ariba sourcing event. Pass event_json as the JSON body, for example "
            "title, templateDocumentInternalId, eventTypeName, and isTest."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def create_event(
        event_json: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /events."""
        try:
            return await _request(
                auth,
                "POST",
                "events",
                _params(realm, user, password_adapter),
                _json_payload(event_json),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_add_supplier_invitations",
        description=(
            "Add supplier invitations to a SAP Ariba sourcing event. Pass suppliers_json as "
            "the JSON array body expected by the sourcing-event API."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def add_supplier_invitations(
        event_id: str,
        suppliers_json: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /events/{eventId}/supplierInvitations."""
        try:
            return await _request(
                auth,
                "POST",
                f"events/{event_id}/supplierInvitations",
                _params(realm, user, password_adapter),
                _json_payload(suppliers_json),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_get_supplier_invitation",
        description=(
            "Get supplier invitation details for a SAP Ariba sourcing event and supplier "
            "unique name."
        ),
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def get_supplier_invitation(
        event_id: str,
        supplier_unique_name: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """GET /events/{eventId}/supplierInvitations/{supplierUniqueName}."""
        try:
            return await _request(
                auth,
                "GET",
                f"events/{event_id}/supplierInvitations/{supplier_unique_name}",
                _params(realm, user, password_adapter),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_list_supplier_bids",
        description="List supplier bids for a SAP Ariba sourcing event.",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
    )
    async def list_supplier_bids(
        event_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
        page_token: str | None = None,
    ) -> str:
        """GET /events/{eventId}/supplierBids."""
        try:
            return await _request(
                auth,
                "GET",
                f"events/{event_id}/supplierBids",
                _params(realm, user, password_adapter, page_token),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_create_job",
        description=(
            "Create a SAP Ariba sourcing-event job. Pass job_json as the JSON body, such as "
            "resourceType EVENT, actionName PUBLISH, and ids.eventId."
        ),
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def create_event_job(
        job_json: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /jobs."""
        try:
            return await _request(
                auth,
                "POST",
                "jobs",
                _params(realm, user, password_adapter),
                _json_payload(job_json),
            )
        except Exception as e:
            return handle_ariba_error(e)

    @mcp.tool(
        name="ariba_event_publish",
        description="Publish a SAP Ariba sourcing event by creating a PUBLISH event job.",
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    async def publish_event(
        event_id: str,
        realm: str | None = None,
        user: str = DEFAULT_USER,
        password_adapter: str = DEFAULT_PASSWORD_ADAPTER,
    ) -> str:
        """POST /jobs with actionName PUBLISH."""
        try:
            payload = {
                "resourceType": "EVENT",
                "actionName": "PUBLISH",
                "ids": {"eventId": event_id},
            }
            return await _request(
                auth,
                "POST",
                "jobs",
                _params(realm, user, password_adapter),
                payload,
            )
        except Exception as e:
            return handle_ariba_error(e)
