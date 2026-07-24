import os

app_dir = r"c:\Users\iamln\project\gemini xprize\bizos\app"

def replace_in_file(filepath, search, replace):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    if search in content:
        content = content.replace(search, replace)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk(app_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)

            # 1. Multi-line import
            search1 = """from app.infrastructure.persistence.postgres.repositories.memory_repository import (
    AbstractMemoryRepository,
)"""
            replace1 = "from app.domain.memory.repository import AbstractMemoryRepository"
            replace_in_file(filepath, search1, replace1)

            # 2. Single-line import
            search2 = "from app.infrastructure.persistence.postgres.repositories.memory_repository import AbstractMemoryRepository"
            replace2 = "from app.domain.memory.repository import AbstractMemoryRepository"
            replace_in_file(filepath, search2, replace2)

            # 3. Vector Repository Multi-line
            search3 = """from app.infrastructure.persistence.postgres.repositories.vector_repository import (
    AbstractVectorRepository,
)"""
            replace3 = "from app.domain.memory.vector_repository import AbstractVectorRepository"
            replace_in_file(filepath, search3, replace3)

            # 4. Vector Repository Single-line
            search4 = "from app.infrastructure.persistence.postgres.repositories.vector_repository import AbstractVectorRepository"
            replace4 = "from app.domain.memory.vector_repository import AbstractVectorRepository"
            replace_in_file(filepath, search4, replace4)
