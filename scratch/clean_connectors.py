import os

def strip_methods(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    methods_to_remove = [
        "def source_id(self)",
        "def source_type(self)",
        "async def authenticate(",
        "async def handle_callback(",
        "async def refresh(",
        "async def health(",
        "async def observe(",
        "def normalize("
    ]
    
    out_lines = []
    skip = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        is_new_method = False
        if line.strip().startswith("def ") or line.strip().startswith("async def "):
            is_new_method = True
            
        if is_new_method:
            skip = False
            for m in methods_to_remove:
                if line.strip().startswith(m):
                    skip = True
                    break
        
        if not skip:
            out_lines.append(line)
            
    content = "".join(out_lines)
    
    # Fix imports and class inheritance
    content = content.replace("BaseConnector, IObservationSource", "BaseConnector")
    content = content.replace("from app.perception.models.observation import (\n    ExternalObservation,\n    ObservationSourceType,\n    UnifiedKnowledgeObject,\n)\n", "")
    content = content.replace("from app.perception.models.observation import ExternalObservation, ObservationSourceType, UnifiedKnowledgeObject", "")
    content = content.replace("ConnectorExecuteRequest,", "")
    content = content.replace("ConnectorResourceType,", "")
    content = content.replace("ConnectorAuthVault", "")
    content = content.replace("from app.domain.shared.context import ExecutionContext", "from app.connectors.sdk.session import ExecutionContext")
    
    # Fix execute signature
    content = content.replace("async def execute(", "async def execute_action(")
    content = content.replace("self, request: ", "self, action: str, params: Dict[str, Any], ")
    content = content.replace("cap = request.capability", "cap = action")
    content = content.replace("p = request.params", "p = params")
    content = content.replace("from app.connectors.sdk.canonical.common import CanonicalAssociation, AssociationType", "from app.connectors.sdk.canonical import CanonicalAssociation, AssociationType")
    content = content.replace("from app.connectors.sdk.canonical.crm import (", "from app.connectors.sdk.canonical import (")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

strip_methods(r"e:\Project\BizOS\app\connectors\builtin\crm\hubspot\connector.py")
strip_methods(r"e:\Project\BizOS\app\connectors\builtin\crm\salesforce\connector.py")
print("Done")
