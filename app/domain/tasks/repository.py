from typing import Optional, Dict
from app.domain.workflows.models import Task

class ITaskRepository:
    async def get_task(self, task_id: str) -> Optional[Task]:
        pass
        
    async def save_task(self, task: Task) -> None:
        pass

class InMemoryTaskRepository(ITaskRepository):
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        
    async def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
        
    async def save_task(self, task: Task) -> None:
        self._tasks[task.task_id] = task
