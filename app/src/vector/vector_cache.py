import json
import numpy as np
from typing import Dict, List
import os

from constants import CACHE_VERSION
from app.src.utils.logging_manager import LoggingManager

class VectorCache:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.document_hashes: Dict[str, str] = {}
        self.chunks: List[Dict] = []
        self.embeddings: List[np.ndarray] = []
        self.logger = LoggingManager()
    
    def load(self) -> bool:
        try:
            if not os.path.exists(self.cache_file):
                return False
                
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                
            if cache_data.get('version') != CACHE_VERSION:
                self.logger.log_info(f"Invalid cache version. Expected {CACHE_VERSION}, found {cache_data.get('version')}")
                return False
                
            self.document_hashes = cache_data.get('document_hashes', {})
            self.chunks = cache_data.get('chunks', [])
            
            embeddings = cache_data.get('embeddings', [])
            self.embeddings = [np.array(e, dtype=np.float32) for e in embeddings]
            
            self.logger.log_info(f"Loaded cache with {len(self.chunks)} chunks")
            return True
        except Exception as e:
            self.logger.log_error(f"Cache loading failed: {str(e)}")
            return False

    def save(self) -> bool:
        try:
            temp_file = self.cache_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump({
                    'version': CACHE_VERSION,
                    'document_hashes': self.document_hashes,
                    'chunks': self.chunks,
                    'embeddings': [e.tolist() for e in self.embeddings]
                }, f, indent=2)
            
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            os.rename(temp_file, self.cache_file)
            
            self.logger.log_info(f"Saved cache with {len(self.chunks)} chunks")
            return True
        except Exception as e:
            self.logger.log_error(f"Cache saving failed: {str(e)}")
            return False
    
    def clear(self) -> None:
        self.document_hashes = {}
        self.chunks = []
        self.embeddings = []
        self.logger.log_info("Cache cleared")