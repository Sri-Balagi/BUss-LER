```mermaid
graph TD
    subgraph "Service Layer"
        Service[Business Service]
    end

    subgraph "Repository Interfaces (Abstractions)"
        AbstractMeta[AbstractMemoryRepository]
        AbstractVec[AbstractVectorRepository]
    end

    subgraph "Concrete Repositories"
        SupabaseRepo[SupabaseMemoryRepository]
        QdrantRepo[QdrantVectorRepository]
    end

    subgraph "Data Sources"
        Supabase[(PostgreSQL / Supabase)]
        Qdrant[(Qdrant Cloud)]
    end

    Service --> AbstractMeta
    Service --> AbstractVec

    AbstractMeta <|-- SupabaseRepo
    AbstractVec <|-- QdrantRepo

    SupabaseRepo --> Supabase
    QdrantRepo --> Qdrant
```
