from contextlib import contextmanager
from typing import Generator, Optional, IO
import os
import json

from app.src.utils.logging_manager import LoggingManager

logger = LoggingManager()

@contextmanager
def managed_file(file_path: str, mode: str = 'r') -> Generator[Optional[IO], None, None]:
    file = None
    try:
        file = open(file_path, mode)
        yield file
    except Exception as e:
        logger.log_error(e, {'file_path': file_path, 'mode': mode})
        yield None
    finally:
        if file is not None:
            file.close()

@contextmanager
def managed_cache(cache_file: str) -> Generator[Optional[dict], None, None]:
    cache_data = {}
    try:
        if os.path.exists(cache_file):
            with managed_file(cache_file, 'r') as f:
                if f:
                    cache_data = json.load(f)
        yield cache_data
    except Exception as e:
        logger.log_error(e, {'cache_file': cache_file})
        yield None