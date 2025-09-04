import os
import time
import re
import hashlib
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

from constants import HASH_CHUNK_SIZE, SEARCH_K, SIMILARITY_THRESHOLD_LOW
from app.src.vector.vector_cache import VectorCache
from app.src.vector.text_chunker import TextChunker
from app.src.utils.logging_manager import LoggingManager
from app.src.llm.embedding_generator import EmbeddingGenerator
from app.src.llm.embedding_generator import APIRequestError, EmbeddingGenerationError

@dataclass
class Chunk:
    text: str
    source: str
    chunk_idx: int

class VectorManager:    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        cache_file: str,
        logger: Optional[LoggingManager] = None,
        chunker: Optional[TextChunker] = None
    ):
        self.embedding_generator = embedding_generator
        self.chunker = chunker or TextChunker()
        self.cache = VectorCache(cache_file)
        self.logger = logger or LoggingManager()
        
        self._dirty_cache = False
        self._nearest_neighbors = NearestNeighbors(n_neighbors=100, metric='cosine')
        self._index_built = False
        
        self._initialize_cache()

    def _initialize_cache(self) -> None:
        if not self.cache.load():
            self.logger.log_info("Cache not found or invalid version, initializing new cache")
            self.cache.clear()
        else:
            self._build_index()

    def _build_index(self) -> None:
        if not self.cache.embeddings:
            self.logger.log_info("No embeddings available for index building")
            return
            
        try:
            embeddings_array = np.vstack(self.cache.embeddings)
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            normalized_embeddings = embeddings_array / norms
            
            self._nearest_neighbors.fit(normalized_embeddings)
            self._index_built = True
            self.logger.log_info(f"Built index for {len(self.cache.embeddings)} normalized embeddings")
        except Exception as e:
            self.logger.log_error(f"Index building failed: {str(e)}")
            import traceback
            self.logger.log_error(traceback.format_exc())
            self._index_built = False

    def _get_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _save_cache(self) -> None:
        if not self._dirty_cache:
            return
            
        try:
            if self.cache.save():
                self._dirty_cache = False
                self._build_index()
        except Exception as e:
            self.logger.log_error(e)

    def _remove_document_chunks(self, doc_id: str) -> None:
        indices_to_remove = [
            i for i, chunk in enumerate(self.cache.chunks)
            if chunk['source'] == doc_id
        ]
        
        for i in sorted(indices_to_remove, reverse=True):
            del self.cache.chunks[i]
            del self.cache.embeddings[i]
        
        if doc_id in self.cache.document_hashes:
            del self.cache.document_hashes[doc_id]
        
        self._dirty_cache = True
        self.logger.log_info(f"Removed all chunks for document: {doc_id}")

    def _process_batch(self, batch: List[Chunk]) -> bool:
        try:
            texts = [chunk.text for chunk in batch]
            embeddings = self.embedding_generator.generate_embeddings_batch(texts)
            
            if not embeddings or len(embeddings) != len(batch):
                self.logger.log_error(Exception("Embedding batch failed - count mismatch"))
                return False
                
            for chunk, embedding in zip(batch, embeddings):
                self.cache.chunks.append({
                    'text': chunk.text,
                    'source': chunk.source,
                    'chunk_idx': chunk.chunk_idx
                })
                self.cache.embeddings.append(np.array(embedding))
            
            self._dirty_cache = True
            return True
            
        except (APIRequestError, EmbeddingGenerationError) as e:
            self.logger.log_error(e)
            return False

    def is_document_processed(self, source: str) -> bool:
        if os.path.exists(source):
            file_hash = self._get_file_hash(source)
            return file_hash in self.cache.document_hashes.values()
        else:
            text_hash = self._get_text_hash(source)
            return text_hash in self.cache.document_hashes.values()

    def add_document(self, text: str, source_path: Optional[str] = None) -> None:
        if not text.strip():
            self.logger.log_error(Exception('Text cannot be empty'))
            return

        doc_id = source_path or f"text_{self._get_text_hash(text)}"
        doc_hash = self._get_file_hash(source_path) if source_path else self._get_text_hash(text)
        
        if doc_id in self.cache.document_hashes:
            if self.cache.document_hashes[doc_id] == doc_hash:
                self.logger.log_info(f'Document unchanged: {doc_id}')
                return
            else:
                self.logger.log_info(f'Document updated: {doc_id}')
                self._remove_document_chunks(doc_id)

        self.logger.log_info(f'Processing document: {doc_id}')
        chunks = self.chunker.chunk_text(text)
        for idx, chunk in enumerate(chunks[:5]):
            self.logger.log_info(f'Chunk {idx+1} (len={len(chunk)}): {repr(chunk)[:200]}')
        self.logger.log_info(f'Total chunks generated: {len(chunks)}')
        
        if not chunks:
            self.logger.log_info(f'No chunks generated for document: {doc_id}')
            return

        batch_size = min(self.embedding_generator.batch_size, 10)
        processed_chunks = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = [
                Chunk(
                    text=chunk,
                    source=doc_id,
                    chunk_idx=i + idx
                )
                for idx, chunk in enumerate(chunks[i:i + batch_size])
            ]
            
            if self._process_batch(batch):
                processed_chunks += len(batch)
                self.logger.log_info(f'Processed {processed_chunks}/{len(chunks)} chunks')
                time.sleep(0.5)

        if processed_chunks == len(chunks):
            self.cache.document_hashes[doc_id] = doc_hash
            self._save_cache()
            self.logger.log_info(f'Successfully processed document: {doc_id} (chunks: {len(chunks)})')
        else:
            self.logger.log_error(Exception(f'Failed to process all chunks for document: {doc_id}'))

    def search(self, query: str, k: int = SEARCH_K, min_similarity: float = SIMILARITY_THRESHOLD_LOW) -> List[Tuple[str, float, str, int]]:
        if not query.strip() or not self.cache.embeddings:
            self.logger.log_info(f"Empty query or no embeddings. Query: '{query}', Embeddings count: {len(self.cache.embeddings)}")
            return []

        query_embedding = self.embedding_generator.generate_embedding(query)
        if query_embedding is None:
            self.logger.log_info("Failed to generate query embedding")
            return []

        try:
            self.logger.log_info(f"Index built: {self._index_built}")
            self.logger.log_info(f"Available embeddings: {len(self.cache.embeddings)}")
            self.logger.log_info(f"Query embedding shape: {np.array(query_embedding).shape}")
            self.logger.log_info(f"First embedding shape: {self.cache.embeddings[0].shape if self.cache.embeddings else 'N/A'}")
            self.logger.log_info(f"K value: {k}, min_similarity: {min_similarity}")
            
            if self._index_built:
                n_neighbors = min(k * 2, len(self.cache.embeddings))
                self.logger.log_info(f"Searching for {n_neighbors} neighbors")
                
                query_norm = np.linalg.norm(query_embedding)
                normalized_query = query_embedding / query_norm
                
                distances, indices = self._nearest_neighbors.kneighbors(
                    [normalized_query], n_neighbors=n_neighbors
                )
                
                self.logger.log_info(f"Raw distances: {distances}")
                self.logger.log_info(f"Raw indices: {indices}")
                
                results = [
                    (self.cache.chunks[i]['text'], 1 - distances[0][idx], 
                    self.cache.chunks[i].get('source', 'Unknown'), 
                    self.cache.chunks[i].get('chunk_idx', 0))
                    for idx, i in enumerate(indices[0])
                    if (1 - distances[0][idx]) >= min_similarity
                ]
                
                self.logger.log_info(f"Filtered results count: {len(results)}")
                return results[:k]
            else:
                self.logger.log_info("Using fallback cosine similarity method")
                query_embedding = np.array(query_embedding).reshape(1, -1)
                embeddings = np.vstack(self.cache.embeddings)
                
                query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
                embeddings_norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
                
                normalized_query = query_embedding / query_norm
                normalized_embeddings = embeddings / embeddings_norm
                
                sims = cosine_similarity(normalized_query, normalized_embeddings)[0]
                
                self.logger.log_info(f"Similarities range: min={sims.min():.3f}, max={sims.max():.3f}, mean={sims.mean():.3f}")
                
                valid_indices = np.where(sims >= min_similarity)[0]
                self.logger.log_info(f"Indices above threshold {min_similarity}: {len(valid_indices)}")
                
                if len(valid_indices) == 0:
                    top_5_indices = np.argsort(sims)[-5:][::-1]
                    for i in top_5_indices:
                        self.logger.log_info(f"Top similarity {i}: {sims[i]:.3f}")
                    return []
                
                top_indices = valid_indices[np.argsort(sims[valid_indices])[-k:][::-1]]
                
                results = [
                    (self.cache.chunks[i]['text'], sims[i], self.cache.chunks[i].get('source', 'Unknown'), self.cache.chunks[i].get('chunk_idx', 0))
                    for i in top_indices
                ]
                
                self.logger.log_info(f"Fallback results count: {len(results)}")
                return results
                
        except Exception as e:
            self.logger.log_error(f"Search error: {str(e)}")
            import traceback
            self.logger.log_error(traceback.format_exc())
            return []

    def search_lexical(self, query: str, k: int = SEARCH_K) -> List[Tuple[str, float, str, int]]:
        if not query.strip() or not self.cache.chunks:
            return []

        tokens = set([t for t in re.findall(r"[A-Za-z0-9]+", query.lower()) if len(t) > 2])
        if not tokens:
            return []

        scored: List[Tuple[float, int]] = []
        for idx, chunk in enumerate(self.cache.chunks):
            text = chunk.get('text', '')
            lower = text.lower()
            score = 0
            for t in tokens:
                if t in lower:
                    score += 1
            score += lower.count('%')

            if score > 0:
                scored.append((float(score), idx))

        if not scored:
            return []

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:k]
        max_score = top[0][0] if top else 1.0
        results: List[Tuple[str, float, str, int]] = []
        for score, i in top:
            pseudo_similarity = min(0.99, (score / (max_score + 1e-6)) * 0.95)
            results.append((self.cache.chunks[i]['text'], pseudo_similarity, self.cache.chunks[i].get('source', 'Unknown'), self.cache.chunks[i].get('chunk_idx', 0)))
        return results

    def get_stats(self) -> Dict[str, int]:
        return {
            'documents': len(self.cache.document_hashes),
            'chunks': len(self.cache.chunks),
            'embeddings': len(self.cache.embeddings),
            'index_built': self._index_built
        }
    


    def close(self) -> None:
        self._save_cache()
        self.logger.log_info("VectorManager shutdown complete")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()