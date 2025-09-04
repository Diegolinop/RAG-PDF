import logging
from typing import Any, Dict, Optional

class LoggingManager:
    def __init__(self, name: str = 'document_chat'):
        self.logger = logging.getLogger(name)
        self._configure_logger()
    
    def _configure_logger(self) -> None:
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        extra = {'context': context} if context else {}
        self.logger.error(str(error), extra=extra, exc_info=True)

    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        extra = {'context': context} if context else {}
        self.logger.info(message, extra=extra)

    def log_debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        extra = {'context': context} if context else {}
        self.logger.debug(message, extra=extra)