import logging
from abc import ABC, abstractmethod


class IBackupProvider(ABC):
    @abstractmethod
    async def create_snapshot(self, resource_id: str) -> str: pass

    @abstractmethod
    async def restore_snapshot(self, resource_id: str, snapshot_id: str): pass

class DisasterRecoveryManager:
    def __init__(self, backup_provider: IBackupProvider):
        self._provider = backup_provider
        self.logger = logging.getLogger("bizos.dr")

    async def backup_repository(self, repo_name: str) -> str:
        self.logger.info(f"Initiating backup for {repo_name}...")
        snapshot_id = await self._provider.create_snapshot(repo_name)
        self.logger.info(f"Backup complete: {snapshot_id}")
        return snapshot_id

    async def restore_repository(self, repo_name: str, snapshot_id: str):
        self.logger.warning(f"Initiating restore for {repo_name} from {snapshot_id}...")
        await self._provider.restore_snapshot(repo_name, snapshot_id)
        self.logger.info(f"Restore complete for {repo_name}.")
