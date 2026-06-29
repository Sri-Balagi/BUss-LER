import pytest
import asyncio
from uuid import uuid4
import time

from app.runtime.tasks.models import TaskPriority
from app.runtime.tasks.state import TaskState
from app.runtime.policies.sequential import SequentialExecutionPolicy
from app.runtime.policies.parallel import ParallelExecutionPolicy
from app.runtime.retry.strategy import DefaultRetryStrategy
from app.runtime.retry.backoff import FixedDelay

from tests.runtime.certification.test_e2e_certification import e2e_env, create_e2e_task, E2EScheduler

@pytest.mark.anyio
async def test_stress_certification(e2e_env):
    pol_ctx, agent_reg, cap_mgr, cap_reg = e2e_env
    
    # 100+ tasks, each task has capability request
    # To hit 300+ capability requests, some tasks could be simulated to do multiple, or we just enqueue 300 tasks.
    # The requirement is 100+ tasks, 300+ requests. 
    # Let's enqueue 300 tasks to the queue.
    
    TOTAL_TASKS = 300
    
    for i in range(TOTAL_TASKS):
        if i % 2 == 0:
            task = create_e2e_task("fs_read", "read", {"path": f"/test_{i}.txt"})
        else:
            task = create_e2e_task("net_req", "get", {"url": f"http://test/{i}"})
            
        pol_ctx.queue_manager.get_queue(TaskState.READY).enqueue(task)
        
    start_time = time.time()
    
    scheduler = E2EScheduler(
        agent_registry=agent_reg, 
        capability_manager=cap_mgr, 
        context=pol_ctx, 
        policy=ParallelExecutionPolicy(), 
        retry_strategy=DefaultRetryStrategy(default_backoff=FixedDelay(1.0)), 
        poll_interval=0.01
    )
    
    # Wait for all tasks to be consumed
    async def monitor():
        while True:
            if pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == TOTAL_TASKS:
                scheduler.stop()
                break
            await asyncio.sleep(0.1)
            
    await asyncio.gather(scheduler.run(), monitor())
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert pol_ctx.queue_manager.get_queue(TaskState.COMPLETED).size() == TOTAL_TASKS
    print(f"Stress test completed 300 tasks in {duration:.2f} seconds.")
