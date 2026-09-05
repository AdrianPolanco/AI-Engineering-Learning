from ai_rag.domain.chunk_config import SentenceChunkerConfig 
from ai_rag.ingestion.chunking.strategies.sentence_chunking import SentenceChunkingStrategy
from ai_rag.ingestion.document_loader import DocumentLoader
from ai_rag.ingestion.pre_processors.md_pre_processor import MdPreProcessor

#embedding_service = EmbeddingService('BAAI/bge-m3')

#print(embedding_service.get_model_info())

document_loader = DocumentLoader('documents/01_sistemas_distribuidos.md')
document = document_loader.load('1.0', 'es', 'handbook')

md_pre_processor = MdPreProcessor()
md_processed_document = md_pre_processor.process(document)

# print('-------------------------------------------------------------------------------')
# print('-----------------------------DOCUMENT------------------------------------------')
# print('-------------------------------------------------------------------------------')
# print(document)

# print('--------------------------------------------------------------------------------')
# print('-----------------------------PROCESSED------------------------------------------')
# print('--------------------------------------------------------------------------------')
# print(md_processed_document)

print('--------------------------------------------------------------------------------')
print('-----------------------------CHUNKING------------------------------------------')
print('--------------------------------------------------------------------------------')

sentence_config = SentenceChunkerConfig(5, 2)
sentence_strategy = SentenceChunkingStrategy(sentence_config)
chunks = sentence_strategy.chunk(md_processed_document)
print(chunks)