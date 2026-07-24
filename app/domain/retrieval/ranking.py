import abc

from app.domain.retrieval.models import RetrievalContext, RetrievalResultItem


class IRankingStrategy(abc.ABC):
    """Abstraction for ranking strategies used by the Retrieval Engine."""

    @abc.abstractmethod
    def rank(self, context: RetrievalContext, items: list[RetrievalResultItem]) -> list[RetrievalResultItem]:
        """Rank and merge a heterogeneous list of retrieval items."""
        pass


class ReciprocalRankFusionStrategy(IRankingStrategy):
    """
    Implements Reciprocal Rank Fusion (RRF) to merge results from different sources.
    Score = 1 / (k + rank)
    """

    def __init__(self, k: int = 60):
        self.k = k

    def rank(self, context: RetrievalContext, items: list[RetrievalResultItem]) -> list[RetrievalResultItem]:
        # Group items by source to calculate their source-specific rank
        source_groups = {}
        for item in items:
            source_groups.setdefault(item.source, []).append(item)

        # Sort each group by initial relevance score descending
        for source, group_items in source_groups.items():
            group_items.sort(key=lambda x: x.relevance_score, reverse=True)

        # Calculate RRF score for each entity
        rrf_scores = {}
        merged_items = {}

        for source, group_items in source_groups.items():
            for rank, item in enumerate(group_items, start=1):
                # RRF Score formula
                score = 1.0 / (self.k + rank)

                if item.entity_id in rrf_scores:
                    rrf_scores[item.entity_id] += score
                    # For provenance, merge the chains and update confidence
                    existing_item = merged_items[item.entity_id]
                    existing_item.provenance_chain.extend([p for p in item.provenance_chain if p not in existing_item.provenance_chain])
                    # Take the max confidence if multiple sources agree
                    existing_item.confidence = max(existing_item.confidence, item.confidence)
                else:
                    rrf_scores[item.entity_id] = score
                    merged_items[item.entity_id] = item

        # Apply the new normalized RRF scores and sort
        final_list = []
        for entity_id, item in merged_items.items():
            item.relevance_score = rrf_scores[entity_id]
            final_list.append(item)

        final_list.sort(key=lambda x: x.relevance_score, reverse=True)
        return final_list[:context.limit]
