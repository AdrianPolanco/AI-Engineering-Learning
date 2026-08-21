# Proyecto RAG — Arquitectura y Estructura

## Estructura completa

```text
ai-rag/
│
├── pyproject.toml
├── poetry.lock
├── docker-compose.yml
├── .env
├── .gitignore
│
├── documents/
│   ├── handbook.md
│   ├── policies.md
│   └── benefits.md
│
├── labs/
│   ├── lab_3_1_faiss.py
│   ├── lab_3_2_semantic_search.py
│   └── lab_3_3_rag.py
│
├── src/
│   │
│   ├── domain/
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── search_result.py
│   │   └── rag_response.py
│   │
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   └── embedding_service.py
│   │
│   ├── vector_store/
│   │   ├── vector_store.py
│   │   └── qdrant_vector_store.py
│   │
│   ├── retrieval/
│   │   └── semantic_search_engine.py
│   │
│   ├── generation/
│   │   ├── prompt_builder.py
│   │   └── llm_client.py
│   │
│   └── rag/
│       └── rag_service.py
│
└── main.py
```

Ahora archivo por archivo.

---

## Archivos del proyecto

### 1. `pyproject.toml`

#### ¿Qué representa?

La **definición del proyecto Python**.

Es equivalente, conceptualmente, al lugar donde defines las dependencias y configuración base de un proyecto .NET.

#### Contendrá

* versión de Python;
* dependencias;
* versión de las librerías;
* configuración de Poetry;
* metadata del proyecto.

Por ejemplo, conceptualmente:

```text
Python:
3.12.x

Dependencies:
sentence-transformers
torch
transformers
numpy
faiss-cpu
qdrant-client
python-dotenv
```

#### NO debe contener

* lógica de negocio;
* configuración específica de Qdrant;
* código de RAG.

---

### 2. `poetry.lock`

#### ¿Qué representa?

El **snapshot exacto del árbol de dependencias**.

`pyproject.toml` dice:

> "Quiero estas versiones."

`poetry.lock` dice:

> "Estas fueron exactamente las versiones y dependencias resueltas."

Es importante para reproducibilidad.

#### Responsabilidad

Garantizar que:

```text
tu máquina
   +
otra máquina
   +
CI
```

puedan instalar esencialmente el mismo conjunto de dependencias.

#### Tú no deberías editarlo manualmente.

---

### 3. `docker-compose.yml`

#### ¿Qué representa?

La definición de la infraestructura externa.

En nuestro caso:

```text
Qdrant
```

#### Contendrá conceptualmente

```text
Service:
    qdrant

Image:
    qdrant/qdrant:v1.18.3

Ports:
    6333
    6334

Volume:
    qdrant_storage
```

#### Responsabilidad

Poder hacer:

```text
docker compose up
```

y obtener:

```text
Qdrant funcionando
```

#### NO debe contener

* Python;
* embeddings;
* lógica de retrieval;
* configuración de `SemanticSearchEngine`.

---

### 4. `.env`

#### ¿Qué representa?

Configuración externa al código.

Por ejemplo:

```text
QDRANT_URL
QDRANT_COLLECTION
LLM_API_KEY
LLM_ENDPOINT
```

#### Responsabilidad

Evitar hardcodear configuración y secretos.

#### NO debe contener

* código;
* documentos;
* embeddings;
* lógica de aplicación.

Y obviamente no debe terminar en Git. Para eso existe `.gitignore`, porque aparentemente seguimos teniendo que recordarle a los humanos que las API keys no son decoración pública.

---

### 5. `documents/`

No contiene Python.

Es nuestra **fuente documental de entrada**.

```text
documents/
├── handbook.md
├── policies.md
└── benefits.md
```

Representan documentos que nuestro sistema debe conocer.

#### Flujo

```text
documents/
     ↓
DocumentLoader
```

#### Importante

Los archivos originales **no son chunks**.

Son documentos completos.

---

### 6. `main.py`

#### ¿Qué representa?

El **entry point de la aplicación**.

Es donde arrancamos el sistema.

Conceptualmente podría hacer:

```text
configuración
     ↓
crear dependencias
     ↓
crear servicios
     ↓
ejecutar ingestion
     ↓
ejecutar una query
     ↓
mostrar resultado
```

#### Responsabilidad

**Composición y ejecución.**

Es decir, conectar las piezas.

#### NO debe hacer

No debería contener:

```text
lectura de Markdown
chunking
embeddings
queries a Qdrant
construcción de prompts
llamadas HTTP al LLM
```

Si `main.py` empieza a hacer eso, hemos vuelto al pantano.

---

### 7. `domain/document.py`

#### ¿Qué representa?

Nuestro concepto de **documento**.

Conceptualmente:

```text
Document
├── id
├── text
└── metadata
```

Por ejemplo:

```text
id:
employee-handbook

text:
todo el contenido del documento

metadata:
{
    source: "employee-handbook.md"
}
```

#### Responsabilidad

Representar un documento dentro de nuestra aplicación.

#### NO sabe

* de archivos;
* de embeddings;
* de Qdrant;
* de LLMs.

Es simplemente un modelo de dominio.

---

### 8. `domain/chunk.py`

#### ¿Qué representa?

Una **unidad recuperable** de un documento.

```text
Chunk
├── id
├── document_id
├── text
├── index
└── metadata
```

Por ejemplo:

```text
Document:
employee-handbook

Chunks:

employee-handbook-0
employee-handbook-1
employee-handbook-2
employee-handbook-3
```

#### Responsabilidad

Representar una sección del documento que puede convertirse en embedding y almacenarse en Qdrant.

#### NO sabe

* cómo se divide un documento;
* cómo se genera el embedding;
* cómo se busca.

---

### 9. `domain/search_result.py`

#### ¿Qué representa?

El resultado de una búsqueda semántica.

Conceptualmente:

```text
SearchResult
├── chunk
├── score
└── metadata
```

Por ejemplo:

```text
Chunk:
employee-handbook-17

Score:
0.89
```

#### Responsabilidad

Representar el resultado de retrieval independientemente de Qdrant.

Esto es importante.

No queremos que nuestra aplicación diga:

```text
QdrantScoredPoint
```

por todas partes.

Queremos:

```text
SearchResult
```

Porque mañana podríamos usar otro vector store.

---

### 10. `domain/rag_response.py`

#### ¿Qué representa?

La respuesta completa de nuestro sistema RAG.

```text
RAGResponse
├── answer
└── sources
```

Por ejemplo:

```text
answer:
"Los empleados tienen 20 días..."

sources:
[
    chunk-17,
    chunk-18
]
```

#### Responsabilidad

Representar el resultado final de RAG.

#### Importante

Las fuentes son parte del resultado.

No queremos simplemente:

```text
string
```

Queremos:

```text
respuesta
+
evidencia recuperada
```

---

### 11. `ingestion/document_loader.py`

#### ¿Qué representa?

La entrada al pipeline de ingestion.

Su trabajo es transformar:

```text
archivo
```

en:

```text
Document
```

Por ejemplo:

```text
handbook.md
     ↓
Document(...)
```

#### Responsabilidades

* localizar documentos;
* leerlos;
* interpretar `.md` y `.txt`;
* crear objetos `Document`;
* asignar metadata básica.

#### NO debe hacer

No debe:

* generar embeddings;
* dividir chunks;
* guardar en Qdrant;
* llamar al LLM.

Su única pregunta es:

> "¿Cómo convierto estos archivos en `Document`?"

---

### 12. `ingestion/chunker.py`

#### ¿Qué representa?

La estrategia de **document chunking**.

Recibe:

```text
Document
```

y produce:

```text
Chunk[]
```

#### Responsabilidades

* definir tamaño del chunk;
* definir overlap;
* dividir texto;
* generar índices;
* generar IDs de chunks;
* conservar relación con el documento original.

Conceptualmente:

```text
Document
   │
   ├── Chunk 0
   ├── Chunk 1
   ├── Chunk 2
   └── Chunk 3
```

#### Aquí experimentaremos

```text
chunk_size
chunk_overlap
```

#### NO debe hacer

No debe:

* generar embeddings;
* llamar a Qdrant;
* hacer retrieval.

---

### 13. `embeddings/embedding_service.py`

Este es uno de los archivos conceptualmente más importantes.

#### ¿Qué representa?

La abstracción sobre el **modelo de embeddings**.

Internamente:

```text
EmbeddingService
       ↓
SentenceTransformer
       ↓
BGE-M3
```

#### Responsabilidades

Convertir:

```text
text
```

en:

```text
vector
```

Y permitir operaciones como:

```text
embed(text)
embed_many(texts)
```

También puede exponer información del modelo como:

```text
model_name
dimension
```

#### Por ejemplo

```text
"hola"
    ↓
BGE-M3
    ↓
[0.02, -0.14, ...]
```

#### NO debe hacer

Absolutamente no debería:

```text
EmbeddingService
      ↓
Qdrant
```

Su responsabilidad termina cuando tiene el vector.

Esta separación te permitirá cambiar:

```text
BGE-M3
```

por:

```text
otro embedding model
```

sin reescribir el retrieval.

---

### 14. `vector_store/vector_store.py`

#### ¿Qué representa?

La **abstracción del almacenamiento vectorial**.

No implementa Qdrant.

Define conceptualmente qué necesita nuestra aplicación de un Vector Store.

Algo parecido a:

```text
VectorStore
├── create_collection()
├── upsert()
├── search()
└── delete()
```

#### Responsabilidad

Definir el contrato:

> "Esto es lo que mi aplicación espera poder hacer con un vector store."

#### NO debe saber

* HTTP;
* Qdrant;
* Docker;
* cómo funciona el índice HNSW;
* detalles del proveedor.

---

### 15. `vector_store/qdrant_vector_store.py`

#### ¿Qué representa?

La implementación concreta de:

```text
VectorStore
```

utilizando:

```text
Qdrant
```

La cadena será:

```text
Application
     ↓
QdrantVectorStore
     ↓
qdrant-client
     ↓
HTTP
     ↓
Qdrant
```

#### Responsabilidades

Traducir:

```text
upsert()
search()
delete()
create_collection()
```

a operaciones concretas de Qdrant.

Por ejemplo:

```text
Chunk + Embedding
       ↓
Qdrant Point
```

y:

```text
query vector
       ↓
Qdrant search
       ↓
Qdrant result
       ↓
SearchResult
```

#### Aquí vive

La lógica específica de Qdrant.

#### NO debe contener

* chunking;
* lógica de negocio de RAG;
* generación de prompts;
* llamadas al LLM.

---

### 16. `retrieval/semantic_search_engine.py`

Aquí empieza la lógica de retrieval de nuestra aplicación.

#### ¿Qué representa?

Un **motor de búsqueda semántica**.

Tiene:

```text
SemanticSearchEngine
│
├── EmbeddingService
└── VectorStore
```

#### Su trabajo

Recibir:

```text
query
```

hacer:

```text
query
 ↓
embedding
 ↓
vector search
 ↓
SearchResult[]
```

#### Ejemplo conceptual

```text
"¿Cuántos días de vacaciones tengo?"
                  │
                  ▼
          EmbeddingService
                  │
                  ▼
             query vector
                  │
                  ▼
             VectorStore
                  │
                  ▼
        [SearchResult, ...]
```

#### Aquí sí hay lógica de retrieval

Por ejemplo:

* generar embedding de query;
* establecer `top_k`;
* aplicar filtros;
* ordenar/interpretar resultados;
* devolver `SearchResult`.

#### NO debe hacer

No debe:

* cargar documentos;
* dividirlos;
* generar embeddings de documentos;
* construir prompts;
* llamar al LLM.

---

### 17. `generation/prompt_builder.py`

#### ¿Qué representa?

La transformación:

```text
retrieved context
+
question
```

en:

```text
prompt
```

#### Responsabilidades

Construir el prompt que recibirá el modelo.

Por ejemplo conceptualmente:

```text
SYSTEM INSTRUCTIONS

Context:
---------
Chunk 1
Chunk 2
Chunk 3
---------

Question:
...
```

También puede definir reglas como:

```text
Utiliza únicamente el contexto.
Si el contexto no contiene información suficiente,
indica que no tienes información suficiente.
```

#### NO debe

* hacer retrieval;
* llamar al LLM;
* generar embeddings;
* hablar con Qdrant.

---

### 18. `generation/llm_client.py`

#### ¿Qué representa?

La abstracción para hablar con el **modelo generativo**.

```text
LLMClient
     ↓
API / HTTP / SDK
     ↓
LLM
```

#### Responsabilidad

Recibir:

```text
Prompt
```

y devolver:

```text
Generated response
```

Por ejemplo:

```text
generate(prompt)
```

#### Este archivo es especialmente importante arquitectónicamente

El resto de la aplicación debería poder decir:

```text
llm_client.generate(prompt)
```

sin saber:

* qué proveedor usamos;
* qué endpoint;
* qué SDK;
* qué headers;
* cómo autenticamos;
* cómo serializamos HTTP.

#### NO debe saber

Nada sobre:

```text
Qdrant
Chunk
Embedding
SemanticSearchEngine
```

El LLM debería ser una dependencia aislada.

---

### 19. `rag/rag_service.py`

Este es el **orquestador de RAG**.

No necesariamente es el archivo más inteligente. Es el que conecta las piezas.

Tiene:

```text
RAGService
│
├── SemanticSearchEngine
├── PromptBuilder
└── LLMClient
```

#### Flujo

```text
Question
   │
   ▼
SemanticSearchEngine
   │
   ▼
SearchResult[]
   │
   ▼
PromptBuilder
   │
   ▼
Prompt
   │
   ▼
LLMClient
   │
   ▼
Answer
   │
   ▼
RAGResponse
```

#### Responsabilidad

Orquestar:

```text
Retrieval
    +
Augmentation
    +
Generation
```

#### NO debe hacer

No debería saber:

```text
cómo se conecta Qdrant
cómo funciona BGE-M3
cómo se divide un documento
cómo funciona HTTP del proveedor LLM
```

Solo coordina.

---

### 20. `labs/lab_3_1_faiss.py`

Este archivo **no pertenece realmente a la aplicación final**.

Es material experimental.

#### Objetivo

Demostrar:

```text
Embedding
 ↓
Vector
 ↓
FAISS
 ↓
Nearest Neighbors
```

Aquí puedes experimentar libremente con:

* dimensiones;
* `float32`;
* L2;
* inner product;
* cosine;
* normalización;
* `k`;
* diferentes queries;
* distintos índices.

#### ¿Por qué no poner esto en `src/`?

Porque FAISS aquí es una herramienta pedagógica.

Nuestro sistema final usa:

```text
Qdrant
```

No:

```text
FAISS
```

---

### 21. `labs/lab_3_2_semantic_search.py`

También es experimental.

#### Objetivo

Demostrar el pipeline:

```text
Document
 ↓
Chunk
 ↓
Embedding
 ↓
Qdrant
 ↓
Search
```

Aquí utilizaremos progresivamente las clases reales de `src`.

Es el puente entre:

```text
"entiendo FAISS"
```

y:

```text
"tengo un servicio de retrieval"
```

---

### 22. `labs/lab_3_3_rag.py`

Es el laboratorio final.

#### Objetivo

Ejecutar:

```text
Question
 ↓
Retrieval
 ↓
Context
 ↓
Prompt
 ↓
LLM
 ↓
RAGResponse
```

Y experimentar con:

* RAG vs no RAG;
* `top_k`;
* chunk size;
* overlap;
* preguntas sin respuesta;
* metadata filtering.

Aquí ya deberías estar utilizando las piezas de `src`.

---

## Cómo se relacionan los archivos

La relación completa queda:

```text
                        main.py
                           │
                           ▼
                      RAGService
                     /     |      \
                    /      |       \
                   ▼       ▼        ▼
          SemanticSearch  Prompt   LLMClient
                │         Builder      │
                │                      │
          ┌─────┴─────┐                ▼
          ▼           ▼               LLM
   EmbeddingService VectorStore
          │              │
          ▼              ▼
 SentenceTransformer QdrantVectorStore
          │              │
          ▼              ▼
       BGE-M3       qdrant-client
                         │
                         ▼
                       Qdrant
```

Y por otro lado, ingestion:

```text
documents/
    │
    ▼
DocumentLoader
    │
    ▼
Document
    │
    ▼
Chunker
    │
    ▼
Chunk
    │
    ▼
EmbeddingService
    │
    ▼
Embedding
    │
    ▼
QdrantVectorStore
    │
    ▼
Qdrant
```

---

## La regla mental para no mezclar responsabilidades

Puedes memorizarlo así:

```text
DocumentLoader
    "¿De dónde viene el texto?"

Chunker
    "¿Cómo lo divido?"

EmbeddingService
    "¿Cómo convierto texto en vectores?"

VectorStore
    "¿Dónde guardo/busco los vectores?"

SemanticSearchEngine
    "¿Qué contexto es relevante para esta pregunta?"

PromptBuilder
    "¿Cómo presento ese contexto al modelo?"

LLMClient
    "¿Cómo hablo con el modelo?"

RAGService
    "¿Cómo coordino todo el proceso?"
```

Y los modelos de dominio:

```text
Document
    "¿Qué es un documento?"

Chunk
    "¿Qué es una unidad recuperable?"

SearchResult
    "¿Qué encontramos?"

RAGResponse
    "¿Qué respondió el sistema y de dónde salió?"
```

Ese es, en mi opinión, el límite correcto para este módulo. **No necesitas 30 clases para demostrar SOLID, pero tampoco 700 líneas en `main.py` para demostrar que sabes importar `qdrant_client`.** Aquí cada archivo tiene una razón concreta de existir y una frontera clara.
