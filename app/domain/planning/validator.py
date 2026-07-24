from abc import ABC, abstractmethod

from app.domain.planning.models import Plan


class IPlanValidator(ABC):
    """
    Validates plans for correctness, consistency, and graph integrity.
    """

    @abstractmethod
    def validate_plan(self, plan: Plan) -> list[str]:
        """
        Validates the given plan.
        Returns a list of error messages if invalid, or an empty list if valid.
        """
        pass
