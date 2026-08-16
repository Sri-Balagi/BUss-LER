"""Microsoft OneNote Connector — Production

Implements full business OneNote workflow via Microsoft Graph:
Notebooks, sections, pages, search, and page manipulation.
"""

from typing import Any, Dict
import structlog
import urllib.parse
import os

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities
from app.domain.shared.context import ExecutionContext
from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.builtin.communication.teams.graph_client import graph_request, graph_paginated

from .manifest import MANIFEST
from .mapper import map_notebook, map_section, map_page, map_page_preview
import app.connectors.builtin.productivity.onenote.webhook  # noqa

logger = structlog.get_logger(__name__)


class OneNoteConnector(BaseConnector):
    """Production Microsoft OneNote Connector with full Graph API coverage."""

    def __init__(self):
        self.oauth_manager = OAuthProviderManager()

    @property
    def connector_id(self) -> str:
        return MANIFEST.connector_id

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id=MANIFEST.connector_id,
            display_name=MANIFEST.display_name,
            version=MANIFEST.version,
            family=MANIFEST.family,
            supports_realtime=True,
            supports_polling=True,
            supported_actions=[
                "health_check", "list_notebooks", "get_notebook", "create_notebook",
                "list_sections", "get_section", "create_section", "list_section_groups",
                "list_pages", "get_page", "get_page_preview", "create_page",
                "update_page", "delete_page", "copy_page", "move_page",
                "search_notebooks", "search_pages", "list_page_tags", "add_page_tag",
                "list_page_attachments", "get_notebook_hierarchy", "disconnect"
            ],
            required_scopes=["Notes.Read", "Notes.ReadWrite"]
        )

    async def _token(self, tenant_id: str) -> str:
        client_id = os.getenv("MICROSOFT_OAUTH_CLIENT_ID", "")
        client_secret = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", "")
        return await self.oauth_manager.get_live_token(
            provider_id="microsoft",
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    async def execute_action(self, action: str, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        logger.info("Executing OneNote action", action=action, tenant=context.tenant_id)
        token = await self._token(context.tenant_id)

        if action == "health_check":
            return self._list_notebooks(token)
        elif action == "list_notebooks":
            return self._list_notebooks(token)
        elif action == "get_notebook":
            return self._get_notebook(token, params["notebook_id"])
        elif action == "create_notebook":
            return self._create_notebook(token, params["display_name"])
        elif action == "list_sections":
            return self._list_sections(token, params["notebook_id"])
        elif action == "get_section":
            return self._get_section(token, params["section_id"])
        elif action == "create_section":
            return self._create_section(token, params["notebook_id"], params["display_name"])
        elif action == "list_section_groups":
            return self._list_section_groups(token, params["notebook_id"])
        elif action == "list_pages":
            return self._list_pages(token, params["section_id"])
        elif action == "get_page":
            return self._get_page(token, params["page_id"])
        elif action == "get_page_preview":
            return self._get_page_preview(token, params["page_id"])
        elif action == "create_page":
            return self._create_page(token, params["section_id"], params["html_content"])
        elif action == "update_page":
            return self._update_page(token, params["page_id"], params["patch_commands"])
        elif action == "delete_page":
            return self._delete_page(token, params["page_id"])
        elif action == "copy_page":
            return self._copy_page(token, params["page_id"], params["target_section_id"])
        elif action == "move_page":
            return self._move_page(token, params["page_id"], params["target_section_id"])
        elif action == "search_notebooks":
            return self._search_notebooks(token, params["query"])
        elif action == "search_pages":
            return self._search_pages(token, params["query"])
        elif action == "list_page_tags":
            return self._list_page_tags(token, params["page_id"])
        elif action == "add_page_tag":
            return self._add_page_tag(token, params["page_id"], params["tag_name"])
        elif action == "list_page_attachments":
            return self._list_page_attachments(token, params["page_id"])
        elif action == "get_notebook_hierarchy":
            return self._get_notebook_hierarchy(token, params.get("notebook_id"))
        elif action == "disconnect":
            await self.oauth_manager.delete_token(self.connector_id, context.tenant_id)
            return {"status": "DISCONNECTED"}
        else:
            raise ValueError(f"Unknown action {action}")

    # --- Internal Implementations ---

    def _list_notebooks(self, token: str) -> Dict[str, Any]:
        raw = graph_paginated(token, "/me/onenote/notebooks")
        return {"notebooks": [map_notebook(n) for n in raw]}

    def _get_notebook(self, token: str, notebook_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/onenote/notebooks/{notebook_id}")
        return map_notebook(raw)

    def _create_notebook(self, token: str, display_name: str) -> Dict[str, Any]:
        raw = graph_request(token, "/me/onenote/notebooks", method="POST", payload={"displayName": display_name})
        return map_notebook(raw)

    def _list_sections(self, token: str, notebook_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/onenote/notebooks/{notebook_id}/sections")
        return {"sections": [map_section(s) for s in raw]}

    def _get_section(self, token: str, section_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/onenote/sections/{section_id}")
        return map_section(raw)

    def _create_section(self, token: str, notebook_id: str, display_name: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/onenote/notebooks/{notebook_id}/sections", method="POST", payload={"displayName": display_name})
        return map_section(raw)

    def _list_section_groups(self, token: str, notebook_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/onenote/notebooks/{notebook_id}/sectionGroups")
        return {"section_groups": [{"id": g["id"], "name": g["displayName"]} for g in raw]}

    def _list_pages(self, token: str, section_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/onenote/sections/{section_id}/pages")
        return {"pages": [map_page(p).model_dump() for p in raw]}

    def _get_page(self, token: str, page_id: str) -> Dict[str, Any]:
        # Get page metadata first
        meta = graph_request(token, f"/me/onenote/pages/{page_id}")
        
        # Then get page content (HTML)
        import urllib.request
        from app.connectors.builtin.communication.teams.graph_client import _build_headers
        url = f"https://graph.microsoft.com/v1.0/me/onenote/pages/{page_id}/content"
        headers = _build_headers(token)
        req = urllib.request.Request(url, headers=headers, method="GET")
        content = ""
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode("utf-8")
        except Exception as e:
            logger.error("Failed to fetch page content", error=str(e))
            
        meta["content_html"] = content
        return map_page(meta).model_dump()

    def _get_page_preview(self, token: str, page_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/onenote/pages/{page_id}/preview")
        return map_page_preview(raw)

    def _create_page(self, token: str, section_id: str, html_content: str) -> Dict[str, Any]:
        # OneNote page creation requires multipart or direct HTML.
        # graph_request sends JSON by default, we need to send HTML.
        import urllib.request
        from app.connectors.builtin.communication.teams.graph_client import _build_headers
        url = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages"
        headers = _build_headers(token)
        headers["Content-Type"] = "text/html"
        
        req = urllib.request.Request(url, data=html_content.encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                import json
                raw = json.loads(resp.read().decode("utf-8"))
                return map_page(raw).model_dump()
        except urllib.error.HTTPError as exc:
            raise ValueError(f"Page creation failed: {exc.read().decode()}")

    def _update_page(self, token: str, page_id: str, patch_commands: list) -> Dict[str, Any]:
        # PATCH /me/onenote/pages/{id}/content requires an array of commands
        # https://docs.microsoft.com/en-us/graph/api/page-update
        
        # We need a custom graph_request for application/json content-type PATCH, 
        # graph_request does this, but the endpoint is /content.
        # Actually it's just graph_request with the list as payload.
        graph_request(token, f"/me/onenote/pages/{page_id}/content", method="PATCH", payload=patch_commands)
        return {"status": "UPDATED"}

    def _delete_page(self, token: str, page_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/onenote/pages/{page_id}", method="DELETE")
        return {"status": "DELETED", "page_id": page_id}

    def _copy_page(self, token: str, page_id: str, target_section_id: str) -> Dict[str, Any]:
        payload = {"groupId": target_section_id}
        graph_request(token, f"/me/onenote/pages/{page_id}/copyToSection", method="POST", payload=payload)
        return {"status": "ACCEPTED"}

    def _move_page(self, token: str, page_id: str, target_section_id: str) -> Dict[str, Any]:
        # Graph API doesn't have a direct 'move', so we have to copy and then delete.
        # Actually, copyToSection with an internal mechanism or we do it manually.
        # Wait, there isn't a moveToSection endpoint. We'll do copy then delete if needed,
        # but let's just do copy and instruct caller. Or we can automate it.
        logger.warning("Move page is not natively supported by Graph API, performing copy instead.")
        self._copy_page(token, page_id, target_section_id)
        # Note: we don't delete automatically to prevent data loss if copy is async and delayed.
        return {"status": "COPIED_PLEASE_DELETE_ORIGINAL"}

    def _search_notebooks(self, token: str, query: str) -> Dict[str, Any]:
        encoded_query = urllib.parse.quote(query)
        raw = graph_paginated(token, f"/me/onenote/notebooks?$filter=contains(displayName,'{encoded_query}')")
        return {"notebooks": [map_notebook(n) for n in raw]}

    def _search_pages(self, token: str, query: str) -> Dict[str, Any]:
        encoded_query = urllib.parse.quote(query)
        # Full text search for pages
        raw = graph_paginated(token, f"/me/onenote/pages?$search=\"{encoded_query}\"")
        return {"pages": [map_page(p).model_dump() for p in raw]}

    def _list_page_tags(self, token: str, page_id: str) -> Dict[str, Any]:
        page = self._get_page(token, page_id)
        return {"tags": page.get("tags", [])}

    def _add_page_tag(self, token: str, page_id: str, tag_name: str) -> Dict[str, Any]:
        # Append a meta tag to the head via PATCH
        commands = [
            {
                "target": "body",
                "action": "append",
                "position": "after",
                "content": f'<p data-tag="{tag_name}">{tag_name}</p>'
            }
        ]
        self._update_page(token, page_id, commands)
        return {"status": "TAG_ADDED"}

    def _list_page_attachments(self, token: str, page_id: str) -> Dict[str, Any]:
        # Graph OneNote doesn't have a direct attachments endpoint. 
        # Attachments are object elements in HTML.
        page = self._get_page(token, page_id)
        import re
        content = page.get("content_html", "")
        # Look for <object data-attachment="filename.pdf" ...>
        attachments = re.findall(r'<object[^>]*data-attachment=["\']([^"\']+)["\']', content)
        return {"attachments": attachments}

    def _get_notebook_hierarchy(self, token: str, notebook_id: str = None) -> Dict[str, Any]:
        # This is expensive. We'll do it for one notebook if provided, else just return notebooks.
        if not notebook_id:
            notebooks = self._list_notebooks(token)["notebooks"]
            if not notebooks:
                return {"notebooks": []}
            notebook_id = notebooks[0]["notebook_id"]
            
        # Fetch sections and pages with expand
        raw = graph_request(token, f"/me/onenote/notebooks/{notebook_id}?$expand=sections($expand=pages)")
        return raw

    async def health_check(self) -> Dict[str, Any]:
        try:
            token = await self._token("default_tenant")
            return self._list_notebooks(token)
        except Exception as e:
            return {"status": "error", "error": str(e)}

