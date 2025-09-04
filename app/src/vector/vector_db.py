from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.src.vector.vector_manager import VectorManager

class VectorDatabase(ABC):
    @abstractmethod
    def add_document(self, text: str, source_path: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[str]:
        pass
    
    @abstractmethod
    def get_stats(self) -> dict:
        pass

class LocalVectorDB(VectorDatabase):
    def __init__(self, vector_manager: VectorManager):
        self.vector_manager = vector_manager

    def add_document(self, text: str, source_path: Optional[str] = None) -> None:
        self.vector_manager.add_document(text, source_path)

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        return self.vector_manager.search(query, k)

    def get_stats(self) -> dict:
        return self.vector_manager.get_stats()