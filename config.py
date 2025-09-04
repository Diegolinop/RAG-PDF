import os
import glob
from dataclasses import dataclass, field
from typing import List

@dataclass
class AppConfig:
    embeddings_url: str = os.getenv('EMBEDDINGS_URL', 'http://127.0.0.1:1234/v1/embeddings')
    completions_url: str = os.getenv('COMPLETIONS_URL', 'http://127.0.0.1:1234/v1/chat/completions')
    cache_file: str = os.getenv('CACHE_FILE', 'cache.json')
    documents_directory: str = os.getenv('DOCUMENTS_DIRECTORY', 'documents')
    document_paths: List[str] = field(init=False)
    embedding_model_id: str = os.getenv('EMBEDDING_MODEL_ID', 'text-embedding-qwen3-embedding-4b')
    completion_model_id: str = os.getenv('COMPLETION_MODEL_ID', 'llama-3.2-3b-instruct')
    chunk_size: int = int(os.getenv('CHUNK_SIZE', '1500'))
    chunk_overlap: int = int(os.getenv('CHUNK_OVERLAP', '50'))
    request_timeout: int = int(os.getenv('REQUEST_TIMEOUT', '60'))
    max_history_length: int = int(os.getenv('MAX_HISTORY_LENGTH', '6'))
    max_tokens: int = int(os.getenv('MAX_TOKENS', '1024'))
    temperature: float = float(os.getenv('TEMPERATURE', '0.4'))
    
    def __post_init__(self):
        self.document_paths = self._discover_documents()
    
    def _discover_documents(self) -> List[str]:
        if not os.path.exists(self.documents_directory):
            os.makedirs(self.documents_directory)
            print(f"Created documents directory: {self.documents_directory}")
            return []
        
        pdf_patterns = [
            os.path.join(self.documents_directory, '*.pdf'),
            os.path.join(self.documents_directory, '**', '*.pdf')
        ]
        
        documents = []
        for pattern in pdf_patterns:
            documents.extend(glob.glob(pattern, recursive=True))
        
        documents = sorted(list(set(documents)))
        
        print(f"Found {len(documents)} PDF documents in {self.documents_directory}")
        return documents
    
    def refresh_documents(self) -> None:
        self.document_paths = self._discover_documents()