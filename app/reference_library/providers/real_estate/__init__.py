from app.reference_library.base import BaseReferenceProvider

from .ontology import OntologyPack
from .vocabulary import VocabularyPack
from .objectives import ObjectivesPack
from .kpis import KPIsPack
from .processes import ProcessesPack
from .constraints import ConstraintsPack
from .regulations import RegulationsPack
from .personas import PersonasPack
from .decisions import DecisionsPack
from .actions import ActionsPack
from .capability_definitions import CapabilityDefinitionsPack
from .context_contributors import ContextContributorsPack
from .policies import PoliciesPack
from .state_transitions import StateTransitionsPack
from .events import EventsPack
from .temporal_patterns import TemporalPatternsPack
from .taxonomies import TaxonomiesPack

class Provider(BaseReferenceProvider):
    ontology = OntologyPack
    vocabulary = VocabularyPack
    objectives = ObjectivesPack
    kpis = KPIsPack
    processes = ProcessesPack
    constraints = ConstraintsPack
    regulations = RegulationsPack
    personas = PersonasPack
    decisions = DecisionsPack
    actions = ActionsPack
    capability_definitions = CapabilityDefinitionsPack
    context_contributors = ContextContributorsPack
    policies = PoliciesPack
    state_transitions = StateTransitionsPack
    events = EventsPack
    temporal_patterns = TemporalPatternsPack
    taxonomies = TaxonomiesPack
