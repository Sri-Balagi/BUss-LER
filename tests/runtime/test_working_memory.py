from app.runtime.session.working_memory import WorkingMemory

def test_working_memory_operations():
    wm = WorkingMemory()
    assert not wm.exists("foo")
    
    wm.put("foo", "bar")
    assert wm.exists("foo")
    assert wm.get("foo") == "bar"
    
    wm.put("num", 42)
    assert set(wm.list_keys()) == {"foo", "num"}
    
    wm.delete("foo")
    assert not wm.exists("foo")
    assert wm.get("foo") is None

def test_working_memory_snapshot():
    wm = WorkingMemory()
    wm.put("a", 1)
    
    snap = wm.snapshot()
    assert snap == {"a": 1}
    
    # Ensure it's a copy
    wm.put("b", 2)
    assert "b" not in snap

def test_working_memory_clear():
    wm = WorkingMemory()
    wm.put("a", 1)
    wm.clear()
    assert len(wm.list_keys()) == 0
