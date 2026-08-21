# Contracts

## Document - document.py

```json
{
  "id": "employee-handbook",
  "text": "El presente manual establece las políticas y procedimientos aplicables a todos los empleados de la organización...",
  "metadata": {
    "source": "employee-handbook.md",
    "document_type": "handbook",
    "language": "es",
    "version": "1.0",
    "path": "C:/data/employee-handbook.md",
    "extension": "txt"
  }
}
```

## Pre-processed Document - document.py
```json
{
  "text": "El presente manual establece las políticas y procedimientos aplicables a todos los empleados de la organización...",
  "metadata": {
    "document_id": "employee-handbook",
    "document_extension": "txt",
    "document_source": "employee-handbook.md",
    "document_type": "handbook",
    "document_language": "es",
    "document_version": "1.0",
    "document_path": "C:/data/employee-handbook.md"
  }
}
```

## Chunk - chunk.py

```json
{
  "id": "employee-handbook-chunk-0003",
  "document_id": "employee-handbook",
  "text": "Los empleados tienen derecho a veinte días laborables de vacaciones por cada año completo trabajado. Las vacaciones deberán ser solicitadas con al menos quince días de anticipación.",
  "index": 3,
  "metadata": {
    "source": "employee-handbook.md",
    "document_type": "handbook",
    "language": "es"
  }
}
```

## Point - Qdrant

```json
{
  "id": "employee-handbook-chunk-0003",
  "vector": [
    0.0124,
    -0.0831,
    0.2194,
    0.0317
  ],
  "payload": {
    "document_id": "employee-handbook",
    "chunk_id": "employee-handbook-chunk-0003",
    "chunk_index": 3,
    "source": "employee-handbook.md",
    "document_type": "handbook",
    "language": "es",
    "text": "Los empleados tienen derecho a veinte días laborables de vacaciones por cada año completo trabajado. Las vacaciones deberán ser solicitadas con al menos quince días de anticipación."
  }
}
```

```text
                    APPLICATION
                        │
                      Chunk
                        │
                        ▼
                QdrantVectorStore
                        │
                        ▼
                     QDRANT
                        │
                      Point
                 ┌──────┴──────┐
                 │             │
               vector        payload
                 │             │
             embedding      metadata
                              +
                             text
```

## Search Result - search_result.py

```json
{
  "chunk": {
    "id": "employee-handbook-chunk-0003",
    "document_id": "employee-handbook",
    "text": "Los empleados tienen derecho a veinte días laborables de vacaciones por cada año completo trabajado. Las vacaciones deberán ser solicitadas con al menos quince días de anticipación.",
    "index": 3,
    "metadata": {
      "source": "employee-handbook.md",
      "document_type": "handbook",
      "language": "es"
    }
  },
  "score": 0.8924
}
```

## RAG Response - rag_response.py

```json
{
  "answer": "Los empleados tienen derecho a veinte días laborables de vacaciones por cada año completo trabajado. Las vacaciones deben solicitarse con al menos quince días de anticipación.",
  "sources": [
    {
      "chunk_id": "employee-handbook-chunk-0003",
      "document_id": "employee-handbook",
      "source": "employee-handbook.md",
      "score": 0.8924
    }
  ]
}
```
