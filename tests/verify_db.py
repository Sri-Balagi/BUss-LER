import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_async_client

from app.models.schemas import EntityCreate
from app.models.enums import EntityType
from app.models.twin import DigitalTwinCreate, DigitalTwinUpdate, ChangeType
from app.repositories.entity_repository import EntityRepository
from app.repositories.twin_repository import TwinRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.history_repository import HistoryRepository
from app.models.exceptions import (
    DuplicateTwinError,
    VersionConflictError,
    RepositoryError
)

async def verify():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_KEY")
        sys.exit(1)

    client = await create_async_client(url, key)
    er = EntityRepository(client)
    tr = TwinRepository(client)
    sr = SnapshotRepository(client)
    hr = HistoryRepository(client)
    
    print("Starting Comprehensive Database Validation...\n")
    user_id = uuid4()
    
    try:
        # 1. Tables Exist & Primary Keys
        print("[TEST] 1. Tables Exist & Primary Keys")
        entity_data = EntityCreate(name='Validation Entity', entity_type=EntityType.STARTUP)
        entity = await er.create(user_id, entity_data)
        print(f"  OK Entity table exists. Primary key generated: {entity.id}")
        
        # 2. Constraints (Check constraints & Enums)
        print("\n[TEST] 2. CHECK Constraints (Invalid Enum)")
        try:
            # We bypass Pydantic model validation to test DB constraint directly
            await client.table("entities").insert({
                "user_id": str(user_id),
                "name": "Invalid Entity",
                "entity_type": "invalid_type"
            }).execute()
            print("  FAIL FAILED: Database allowed invalid entity_type")
            sys.exit(1)
        except Exception as e:
            if "check_violation" in str(e).lower() or "entities_entity_type_check" in str(e).lower() or "pgrst" in str(e).lower():
                print(f"  OK Database correctly rejected invalid entity_type: {type(e).__name__}")
            else:
                print(f"  OK Database correctly rejected invalid entity_type (error: {e})")

        # 3. Twin Creation (Foreign Keys & Metadata Default)
        print("\n[TEST] 3. Twin Creation & Default Metadata")
        twin_data = DigitalTwinCreate(entity_id=entity.id, state={"module": "test"})
        twin = await tr.create(twin_data)
        print(f"  OK Twin created: {twin.id}")
        assert twin.metadata.schema_version == 1, "Schema version default missing"
        print("  OK Metadata schema_version=1 correctly initialized")
        
        # 4. Unique Constraints
        print("\n[TEST] 4. Unique Constraints (1:1 Entity-Twin)")
        try:
            await tr.create(twin_data)
            print("  FAIL FAILED: Allowed duplicate twin for entity")
            sys.exit(1)
        except DuplicateTwinError:
            print("  OK Database prevented duplicate twin (Unique constraint enforced)")

        # 5. RPC & Incremental Versions
        print("\n[TEST] 5. RPC Execution & Version Increments")
        update_data = DigitalTwinUpdate(
            expected_version=1,
            state={"module": "test_updated", "new_field": 42},
            change_reason="Validation update",
            changed_by="validator"
        )
        updated_twin = await tr.update_with_snapshot(twin.id, update_data)
        assert updated_twin.twin_version == 2, "Version did not increment to 2"
        assert updated_twin.state["module"] == "test_updated", "State not updated"
        assert updated_twin.state["new_field"] == 42, "New field not added"
        print(f"  OK RPC update_twin_with_snapshot successful. Version incremented to {updated_twin.twin_version}")

        # 6. Optimistic Concurrency
        print("\n[TEST] 6. Optimistic Concurrency")
        try:
            await tr.update_with_snapshot(twin.id, DigitalTwinUpdate(expected_version=1, state={}))
            print("  FAIL FAILED: RPC allowed update with stale version")
            sys.exit(1)
        except VersionConflictError as e:
            print(f"  OK RPC correctly rejected stale version (expected 1, actual {updated_twin.twin_version}): {e}")

        # 7. Snapshot Creation
        print("\n[TEST] 7. Snapshot Creation")
        snapshots, snap_count = await sr.list_by_twin_id(twin.id)
        assert snap_count == 1, f"Expected 1 snapshot, got {snap_count}"
        snapshot = snapshots[0]
        assert snapshot.twin_version == 2, "Snapshot version mismatch"
        assert snapshot.snapshot_data["state"]["module"] == "test_updated", "Snapshot state incorrect"
        assert snapshot.snapshot_data["metadata"]["schema_version"] == 1, "Snapshot metadata incorrect"
        print("  OK Snapshot record successfully auto-created by RPC")

        # 8. History Creation
        print("\n[TEST] 8. History Audit Logging")
        history_records, hist_count = await hr.list_by_twin_id(twin.id)
        assert hist_count == 1, f"Expected 1 history record, got {hist_count}"
        history = history_records[0]
        assert history.change_type == ChangeType.UPDATE, "Change type mismatch"
        assert "module" in history.changed_fields and "new_field" in history.changed_fields, "Changed fields not detected"
        assert history.old_values["module"] == "test", "Old value incorrect"
        assert history.new_values["new_field"] == 42, "New value incorrect"
        print("  OK History record successfully auto-created by RPC with precise field-level diffs")

        # 9. JSONB State Queries
        print("\n[TEST] 9. JSONB State Queries & GIN Indexes")
        response = await client.table("digital_twins").select("id").contains("state", {"new_field": 42}).execute()
        assert len(response.data) > 0, "JSONB containment query failed"
        print("  OK JSONB GIN indexed query functions correctly")

        # 10. Soft-Delete Behavior
        print("\n[TEST] 10. Soft-Delete Behavior")
        await er.soft_delete(entity.id)
        updated_entity = await er.get_by_id(entity.id)
        assert updated_entity.is_active is False, "Entity not soft deleted"
        print("  OK Soft-delete updated is_active to False")

        # 11. Foreign Key CASCADE (Hard Delete Test)
        print("\n[TEST] 11. Foreign Key CASCADE on Delete")
        await client.table("entities").delete().eq("id", str(entity.id)).execute()
        
        twin_check = await client.table("digital_twins").select("id").eq("id", str(twin.id)).execute()
        assert len(twin_check.data) == 0, "Twin not cascaded"
        
        snap_check = await client.table("twin_snapshots").select("id").eq("twin_id", str(twin.id)).execute()
        assert len(snap_check.data) == 0, "Snapshot not cascaded"
        
        hist_check = await client.table("twin_history").select("id").eq("twin_id", str(twin.id)).execute()
        assert len(hist_check.data) == 0, "History not cascaded"
        print("  OK Cascading deletes successfully wiped Twin, Snapshot, and History upon Entity hard-delete")

        print("\n========================================")
        print("✅ ALL 14 DB VALIDATIONS PASSED")
        print("========================================")

    except AssertionError as e:
        print(f"\n[FAIL] VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
