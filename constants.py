from typing import Final

DEFAULT_CHUNK_SIZE: Final[int] = 512
DEFAULT_OVERLAP: Final[int] = 64
HASH_CHUNK_SIZE: Final[int] = 8192
CACHE_VERSION: Final[str] = "1.2"
MAX_RETRY_ATTEMPTS: Final[int] = 3
MIN_REQUEST_INTERVAL: Final[float] = 1.0
DEFAULT_TIMEOUT: Final[int] = 100
MAX_HISTORY_LENGTH: Final[int] = 6
MAX_TOKENS: Final[int] = 1024
TEMPERATURE: Final[float] = 0.5
SEARCH_K: Final[int] = 30
SIMILARITY_THRESHOLD_HIGH: Final[float] = 0.85
SIMILARITY_THRESHOLD_MEDIUM: Final[float] = 0.70
SIMILARITY_THRESHOLD_LOW: Final[float] = 0.10