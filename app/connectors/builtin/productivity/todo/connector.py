"""Microsoft To Do Connector — Production

Implements full business To Do workflow via Microsoft Graph:
Lists, tasks, checklists, categories, recurrence, and linked resources.
"""

from typing import Any, Dict, List
import structlog
import os

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities
from app.domain.shared.context import ExecutionContext
from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.builtin.communication.teams.graph_client import graph_request, graph_paginated

from .manifest import MANIFEST
from .mapper import map_task, map_task_list, map_checklist_item, map_linked_resource
import app.connectors.builtin.productivity.todo.webhook  # noqa

logger = structlog.get_logger(__name__)


class TodoConnector(BaseConnector):
    """Production Microsoft To Do Connector with full Graph API coverage."""

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
            supports_realtime=False,
            supports_polling=True,
            supported_actions=[
                "health_check", "list_todo_lists", "get_todo_list", "create_todo_list",
                "update_todo_list", "delete_todo_list", "list_tasks", "get_task",
                "create_task", "update_task", "complete_task", "delete_task",
                "list_checklist_items", "add_checklist_item", "complete_checklist_item",
                "delete_checklist_item", "list_linked_resources", "add_linked_resource",
                "delete_linked_resource", "list_task_attachments", "add_task_attachment",
                "delete_task_attachment", "disconnect"
            ],
            required_scopes=["Tasks.Read", "Tasks.ReadWrite"]
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
        logger.info("Executing To Do action", action=action, tenant=context.tenant_id)
        token = await self._token(context.tenant_id)

        if action == "health_check":
            return self._list_todo_lists(token)
        elif action == "list_todo_lists":
            return self._list_todo_lists(token)
        elif action == "get_todo_list":
            return self._get_todo_list(token, params["list_id"])
        elif action == "create_todo_list":
            return self._create_todo_list(token, params["display_name"])
        elif action == "update_todo_list":
            return self._update_todo_list(token, params["list_id"], params["display_name"])
        elif action == "delete_todo_list":
            return self._delete_todo_list(token, params["list_id"])
        elif action == "list_tasks":
            return self._list_tasks(token, params["list_id"])
        elif action == "get_task":
            return self._get_task(token, params["list_id"], params["task_id"])
        elif action == "create_task":
            return self._create_task(token, params["list_id"], params)
        elif action == "update_task":
            return self._update_task(token, params["list_id"], params["task_id"], params)
        elif action == "complete_task":
            return self._complete_task(token, params["list_id"], params["task_id"])
        elif action == "delete_task":
            return self._delete_task(token, params["list_id"], params["task_id"])
        elif action == "list_checklist_items":
            return self._list_checklist_items(token, params["list_id"], params["task_id"])
        elif action == "add_checklist_item":
            return self._add_checklist_item(token, params["list_id"], params["task_id"], params["display_name"])
        elif action == "complete_checklist_item":
            return self._complete_checklist_item(token, params["list_id"], params["task_id"], params["item_id"])
        elif action == "delete_checklist_item":
            return self._delete_checklist_item(token, params["list_id"], params["task_id"], params["item_id"])
        elif action == "list_linked_resources":
            return self._list_linked_resources(token, params["list_id"], params["task_id"])
        elif action == "add_linked_resource":
            return self._add_linked_resource(token, params["list_id"], params["task_id"], params)
        elif action == "delete_linked_resource":
            return self._delete_linked_resource(token, params["list_id"], params["task_id"], params["resource_id"])
        elif action == "list_task_attachments":
            return self._list_task_attachments(token, params["list_id"], params["task_id"])
        elif action == "add_task_attachment":
            return self._add_task_attachment(token, params["list_id"], params["task_id"], params["name"], params["content_bytes"])
        elif action == "delete_task_attachment":
            return self._delete_task_attachment(token, params["list_id"], params["task_id"], params["attachment_id"])
        elif action == "disconnect":
            await self.oauth_manager.delete_token(self.connector_id, context.tenant_id)
            return {"status": "DISCONNECTED"}
        else:
            raise ValueError(f"Unknown action {action}")

    # --- Internal Implementations ---

    def _list_todo_lists(self, token: str) -> Dict[str, Any]:
        raw = graph_paginated(token, "/me/todo/lists")
        return {"lists": [map_task_list(lst) for lst in raw]}

    def _get_todo_list(self, token: str, list_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}")
        return map_task_list(raw)

    def _create_todo_list(self, token: str, display_name: str) -> Dict[str, Any]:
        raw = graph_request(token, "/me/todo/lists", method="POST", payload={"displayName": display_name})
        return map_task_list(raw)

    def _update_todo_list(self, token: str, list_id: str, display_name: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}", method="PATCH", payload={"displayName": display_name})
        return map_task_list(raw)

    def _delete_todo_list(self, token: str, list_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/todo/lists/{list_id}", method="DELETE")
        return {"status": "DELETED", "list_id": list_id}

    def _list_tasks(self, token: str, list_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/todo/lists/{list_id}/tasks")
        return {"tasks": [map_task(t, list_id).model_dump() for t in raw]}

    def _get_task(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}")
        return map_task(raw, list_id).model_dump()

    def _create_task(self, token: str, list_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"title": params["title"]}
        if "body" in params:
            payload["body"] = {"content": params["body"], "contentType": "text"}
        if "importance" in params:
            payload["importance"] = params["importance"]
        if "due_date" in params:
            payload["dueDateTime"] = {"dateTime": params["due_date"], "timeZone": "UTC"}
        if "reminder_at" in params:
            payload["isReminderOn"] = True
            payload["reminderDateTime"] = {"dateTime": params["reminder_at"], "timeZone": "UTC"}
        if "categories" in params:
            payload["categories"] = params["categories"]
        if "recurrence" in params:
            payload["recurrence"] = params["recurrence"]

        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks", method="POST", payload=payload)
        return map_task(raw, list_id).model_dump()

    def _update_task(self, token: str, list_id: str, task_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {}
        if "title" in params:
            payload["title"] = params["title"]
        if "body" in params:
            payload["body"] = {"content": params["body"], "contentType": "text"}
        if "importance" in params:
            payload["importance"] = params["importance"]
        if "due_date" in params:
            payload["dueDateTime"] = {"dateTime": params["due_date"], "timeZone": "UTC"}
        if "categories" in params:
            payload["categories"] = params["categories"]
        
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}", method="PATCH", payload=payload)
        return map_task(raw, list_id).model_dump()

    def _complete_task(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}", method="PATCH", payload={"status": "completed"})
        return map_task(raw, list_id).model_dump()

    def _delete_task(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}", method="DELETE")
        return {"status": "DELETED", "task_id": task_id}

    def _list_checklist_items(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/checklistItems")
        return {"checklist_items": [map_checklist_item(i) for i in raw]}

    def _add_checklist_item(self, token: str, list_id: str, task_id: str, display_name: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/checklistItems", method="POST", payload={"displayName": display_name})
        return map_checklist_item(raw)

    def _complete_checklist_item(self, token: str, list_id: str, task_id: str, item_id: str) -> Dict[str, Any]:
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/checklistItems/{item_id}", method="PATCH", payload={"isChecked": True})
        return map_checklist_item(raw)

    def _delete_checklist_item(self, token: str, list_id: str, task_id: str, item_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/checklistItems/{item_id}", method="DELETE")
        return {"status": "DELETED"}

    def _list_linked_resources(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/linkedResources")
        return {"linked_resources": [map_linked_resource(i) for i in raw]}

    def _add_linked_resource(self, token: str, list_id: str, task_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "webUrl": params["web_url"],
            "applicationName": params["application_name"],
            "displayName": params["display_name"]
        }
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/linkedResources", method="POST", payload=payload)
        return map_linked_resource(raw)

    def _delete_linked_resource(self, token: str, list_id: str, task_id: str, resource_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/linkedResources/{resource_id}", method="DELETE")
        return {"status": "DELETED"}

    def _list_task_attachments(self, token: str, list_id: str, task_id: str) -> Dict[str, Any]:
        raw = graph_paginated(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/attachments")
        return {"attachments": [{"id": a["id"], "name": a["name"], "size": a["size"]} for a in raw]}

    def _add_task_attachment(self, token: str, list_id: str, task_id: str, name: str, content_bytes: bytes) -> Dict[str, Any]:
        import base64
        b64_content = base64.b64encode(content_bytes).decode("utf-8")
        payload = {
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": name,
            "contentBytes": b64_content
        }
        raw = graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/attachments", method="POST", payload=payload)
        return {"id": raw["id"], "name": raw["name"], "size": raw["size"]}

    def _delete_task_attachment(self, token: str, list_id: str, task_id: str, attachment_id: str) -> Dict[str, Any]:
        graph_request(token, f"/me/todo/lists/{list_id}/tasks/{task_id}/attachments/{attachment_id}", method="DELETE")
        return {"status": "DELETED"}

    async def health_check(self) -> Dict[str, Any]:
        try:
            token = await self._token("default_tenant")
            return self._list_todo_lists(token)
        except Exception as e:
            return {"status": "error", "error": str(e)}

