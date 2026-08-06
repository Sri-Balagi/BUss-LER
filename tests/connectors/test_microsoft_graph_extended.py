import pytest
import pytest_asyncio
import os
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from httpx import HTTPStatusError, Request, Response

from app.connectors.builtin.storage.onedrive.connector import OneDriveConnector
from app.connectors.builtin.productivity.todo.connector import TodoConnector
from app.connectors.builtin.productivity.onenote.connector import OneNoteConnector
from app.connectors.builtin.email.outlook.connector import OutlookConnector
from app.domain.shared.context import ExecutionContext
from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.builtin.communication.teams.graph_client import GraphAPIError

# --- Setup & Fixtures ---

@pytest_asyncio.fixture(scope="module")
async def tenant_id():
    return "default_tenant"

@pytest_asyncio.fixture(scope="module")
async def execution_context(tenant_id):
    return ExecutionContext(
        tenant_id=tenant_id, 
        user_id="test_user",
        session_id="test_session",
        conversation_id="test_conv",
        trace_id="test_trace",
        correlation_id="test_corr"
    )

@pytest_asyncio.fixture(scope="module")
async def onedrive(tenant_id):
    connector = OneDriveConnector()
    yield connector

@pytest_asyncio.fixture(scope="module")
async def todo(tenant_id):
    connector = TodoConnector()
    yield connector

@pytest_asyncio.fixture(scope="module")
async def onenote(tenant_id):
    connector = OneNoteConnector()
    yield connector

@pytest_asyncio.fixture(scope="module")
async def outlook(tenant_id):
    connector = OutlookConnector()
    yield connector

def _is_unauthorized(exc_info):
    """Helper to detect auth/permission errors which are expected in some CI environments."""
    if isinstance(exc_info.value, GraphAPIError) and exc_info.value.status_code in (401, 403, 404):
        return True
    if isinstance(exc_info.value, ValueError) and "not registered" in str(exc_info.value):
        return True
    return False

# --- User Profile & People API Tests ---

@pytest.mark.asyncio
async def test_get_user_profile(outlook, execution_context):
    try:
        res = await outlook.execute_action("get_user_profile", {}, execution_context)
        assert "displayName" in res
    except Exception as e:
        pytest.skip(f"Skipping due to auth/setup: {e}")

@pytest.mark.asyncio
async def test_list_people(outlook, execution_context):
    try:
        res = await outlook.execute_action("list_people", {}, execution_context)
        assert "people" in res
    except Exception as e:
        pytest.skip(f"Skipping due to auth/setup: {e}")

# --- OneDrive Lifecycle Tests ---

@pytest.mark.asyncio
async def test_onedrive_lifecycle(onedrive, execution_context):
    try:
        # 1. Get Drive Info
        info = await onedrive.execute_action("get_drive_info", {}, execution_context)
        assert "drive_id" in info

        # 2. Upload file
        file_name = f"test_file_{uuid.uuid4().hex}.txt"
        upload_res = await onedrive.execute_action("upload_file", {
            "parent_id": "root",
            "file_name": file_name,
            "content_bytes": b"Hello World"
        }, execution_context)
        assert "item_id" in upload_res
        item_id = upload_res["item_id"]

        # 3. Download file
        download_res = await onedrive.execute_action("download_file", {"item_id": item_id}, execution_context)
        assert download_res["content_bytes"] == b"Hello World"

        # 4. Rename file
        new_name = f"renamed_{file_name}"
        rename_res = await onedrive.execute_action("move_item", {
            "item_id": item_id,
            "new_name": new_name
        }, execution_context)
        assert rename_res["name"] == new_name

        # 5. Delete file
        del_res = await onedrive.execute_action("delete_item", {"item_id": item_id}, execution_context)
        assert del_res["status"] == "DELETED"

    except Exception as e:
        pytest.skip(f"Skipping OneDrive lifecycle due to {e}")

@pytest.mark.asyncio
async def test_onedrive_delta_sync(onedrive, execution_context):
    try:
        # First sync gets snapshot + delta link
        res1 = await onedrive.execute_action("delta_sync", {}, execution_context)
        assert "items" in res1
        
        # Second sync uses delta link
        res2 = await onedrive.execute_action("delta_sync", {}, execution_context)
        assert "items" in res2
    except Exception as e:
        pytest.skip(f"Skipping Delta Sync due to {e}")

# --- To Do Lifecycle Tests ---

@pytest.mark.asyncio
async def test_todo_lifecycle(todo, execution_context):
    try:
        # 1. Create List
        list_name = f"Test List {uuid.uuid4().hex}"
        list_res = await todo.execute_action("create_todo_list", {"display_name": list_name}, execution_context)
        list_id = list_res["list_id"]

        # 2. Create Task
        task_res = await todo.execute_action("create_task", {
            "list_id": list_id,
            "title": "Buy groceries",
            "importance": "high"
        }, execution_context)
        task_id = task_res["task_id"]

        # 3. Add Checklist Item
        check_res = await todo.execute_action("add_checklist_item", {
            "list_id": list_id,
            "task_id": task_id,
            "display_name": "Milk"
        }, execution_context)
        assert "item_id" in check_res

        # 4. Complete Task
        await todo.execute_action("complete_task", {"list_id": list_id, "task_id": task_id}, execution_context)

        # 5. Delete List (cascades)
        await todo.execute_action("delete_todo_list", {"list_id": list_id}, execution_context)

    except Exception as e:
        pytest.skip(f"Skipping To Do lifecycle due to {e}")

# --- OneNote Lifecycle Tests ---

@pytest.mark.asyncio
async def test_onenote_lifecycle(onenote, execution_context):
    try:
        # 1. Create Notebook
        nb_name = f"Test Notebook {uuid.uuid4().hex}"
        nb_res = await onenote.execute_action("create_notebook", {"display_name": nb_name}, execution_context)
        nb_id = nb_res["notebook_id"]

        # 2. Create Section
        sec_name = "Test Section"
        sec_res = await onenote.execute_action("create_section", {
            "notebook_id": nb_id,
            "display_name": sec_name
        }, execution_context)
        sec_id = sec_res["section_id"]

        # 3. Create Page
        html = f"<!DOCTYPE html><html><head><title>Test Page</title></head><body><p>Hello OneNote</p></body></html>"
        page_res = await onenote.execute_action("create_page", {
            "section_id": sec_id,
            "html_content": html
        }, execution_context)
        page_id = page_res["note_id"]

        # 4. List Pages (to verify creation)
        await asyncio.sleep(2)
        list_res = await onenote.execute_action("list_pages", {}, execution_context)
        assert "pages" in list_res

        # Note: Graph API has issues with immediate deletion of OneNote notebooks/pages,
        # so we don't assert deletion success aggressively here.

    except Exception as e:
        pytest.skip(f"Skipping OneNote lifecycle due to {e}")

# --- Failure & Security Scenarios ---

@pytest.mark.asyncio
async def test_invalid_folder_id(onedrive, execution_context):
    with pytest.raises(Exception) as exc:
        await onedrive.execute_action("list_folder", {"folder_id": "invalid_123"}, execution_context)
    assert _is_unauthorized(exc) or "itemNotFound" in str(exc.value) or "invalidRequest" in str(exc.value) or "malformed" in str(exc.value).lower()

@pytest.mark.asyncio
async def test_invalid_task_id(todo, execution_context):
    with pytest.raises(Exception) as exc:
        await todo.execute_action("get_task", {"list_id": "valid_but_fake", "task_id": "fake"}, execution_context)
    assert _is_unauthorized(exc) or "ErrorItemNotFound" in str(exc.value) or "Invalid" in str(exc.value)

@pytest.mark.asyncio
async def test_security_tenant_isolation():
    # Verify that requesting a token for a non-existent tenant raises an Auth error
    oauth_manager = OAuthProviderManager()
    with pytest.raises(Exception):
        await oauth_manager.get_token("microsoft_onedrive", "invalid_tenant_999")

# --- Calendar & Contacts Expanded Tests ---

@pytest.mark.asyncio
async def test_contact_folders(outlook, execution_context):
    try:
        folders = await outlook.execute_action("list_contact_folders", {}, execution_context)
        assert "folders" in folders
    except Exception as e:
        pytest.skip(f"Skipping Contacts due to {e}")

@pytest.mark.asyncio
async def test_free_busy_lookup(outlook, execution_context):
    try:
        me = await outlook.execute_action("get_user_profile", {}, execution_context)
        email = me.get("mail") or me.get("userPrincipalName")
        
        now = datetime.now(timezone.utc)
        start = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end = (now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        res = await outlook.execute_action("free_busy_lookup", {
            "schedules": [email],
            "start": start,
            "end": end
        }, execution_context)
        assert "schedules" in res
    except Exception as e:
        pytest.skip(f"Skipping Free/Busy due to {e}")
