from ai_rag.domain.chunk import Chunk, ChunkMetadata
from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig
from ai_rag.domain.pre_processed_document import PreProcessedDocument
from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy


class SentenceChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: SentenceChunkerConfig) -> None:
        super().__init__()
        self.__config = config

    def chunk(self, document: PreProcessedDocument) -> list[Chunk]:
        chunks: list[Chunk] = []
        chunk_n = 1
        # [DocumentBlock, DocumentBlock]
        for block in document.text: 
            # DocumentBlock.text
            sentences = [
                f'{sentence.strip()}.' 
                for sentence in block.text.split('.') 
                if sentence.strip()
            ]

            buffer = []
            #overlap_pointer = 0
            overlap_added = False
            for i, sentence in enumerate(sentences):

                if len(buffer) == self.__config.max_sentences:
                    overlap_added, chunk_n = self.__create_chunk(document, chunks, chunk_n, buffer)

                if not overlap_added and i > 0 and i % self.__config.max_sentences == 0:
                    overlap_sentences = sentences[max(0, i - self.__config.overlap_sentences):i]
                    buffer.extend(overlap_sentences)
                    overlap_added = True

                if len(buffer) < self.__config.max_sentences:
                    buffer.append(sentence)
                    continue

                #overlap_pointer = i

        return chunks

    def __create_chunk(self, document, chunks, chunk_n, buffer):
        chunk_id = f'{document.metadata.document_id}-chunk-{chunk_n}'

        chunk_metadata = ChunkMetadata(
                    source=document.metadata.document_source,
                    document_type= document.metadata.document_type,
                    lang=document.metadata.document_lang,
                    version=document.metadata.document_version,
                    path=document.metadata.document_path,
                    extension=document.metadata.document_extension
                )

        chunks.append(Chunk(
                    id=chunk_id, 
                    document_id=document.metadata.document_id,
                    index=chunk_n,
                    text=' '.join(buffer), metadata=chunk_metadata))

        buffer.clear()
        chunk_n += 1
        overlap_added = False
        return overlap_added, chunk_n

            

    def set_config(self, config: RecursiveChunkerConfig | SentenceChunkerConfig):
        if type(config) is not SentenceChunkerConfig:
            raise NotImplementedError(f'This chunking strategy only accepts configs of type {SentenceChunkerConfig.__name__}')
        super().set_config(config)

    def get_config(self) -> SentenceChunkerConfig:
        return self.__config