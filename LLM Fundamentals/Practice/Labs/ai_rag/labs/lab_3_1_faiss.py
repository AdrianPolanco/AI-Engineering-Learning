from ai_rag.domain.chunk_config import RecursiveChunkerConfig, SentenceChunkerConfig 
from ai_rag.ingestion.chunking.chunking_rule_provider import ChunkingRuleProvider
from ai_rag.ingestion.chunking.chunking_strategy import ChunkingStrategy
from ai_rag.ingestion.chunking.rule_providers.extension_chunking_rule_provider import ExtensionChunkingRuleProvider
from ai_rag.ingestion.chunking.strategies.recursive_chunking import RecursiveChunkingStrategy
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
print('-----------------------------SENTENCE CHUNKING------------------------------------------')
print('--------------------------------------------------------------------------------')
sentence_config = SentenceChunkerConfig(5, 2)
sentence_strategy = SentenceChunkingStrategy(sentence_config)
sentence_chunks = sentence_strategy.chunk(md_processed_document)
print(sentence_chunks)

print('--------------------------------------------------------------------------------')
print('-----------------------------RECURSIVECHUNKING------------------------------------------')
print('--------------------------------------------------------------------------------')

recursive_config = RecursiveChunkerConfig(5, 2)
recursive_provider = ExtensionChunkingRuleProvider()
recursive_strategy = RecursiveChunkingStrategy(recursive_config, recursive_provider)
recursive_chunks = recursive_strategy.chunk(md_processed_document)
print(recursive_chunks)