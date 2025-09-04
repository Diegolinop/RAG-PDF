class DocumentProcessingError(Exception):
    """Base exception for document processing errors"""

class EmbeddingGenerationError(DocumentProcessingError):
    """Errors during embedding generation"""

class CacheOperationError(DocumentProcessingError):
    """Errors during cache operations"""

class PDFExtractionError(DocumentProcessingError):
    """Errors during PDF text extraction"""

class APIRequestError(DocumentProcessingError):
    """Errors during API requests"""