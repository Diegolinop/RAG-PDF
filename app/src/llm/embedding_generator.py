import time
import requests
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.exceptions import APIRequestError, EmbeddingGenerationError
from app.src.utils.logging_manager import LoggingManager
from constants import DEFAULT_TIMEOUT, MAX_RETRY_ATTEMPTS, MIN_REQUEST_INTERVAL

class EmbeddingGenerator:
    def __init__(self, url: str, timeout: int = DEFAULT_TIMEOUT, batch_size: int = 5, model_id: str = 'local-model', logger: Optional[LoggingManager] = None):
        self.url = url.rstrip('/') + '/v1/embeddings' if not url.endswith('/v1/embeddings') else url
        self.timeout = timeout
        self.batch_size = min(batch_size, 10)
        self.last_request_time = 0
        self.min_request_interval = MIN_REQUEST_INTERVAL
        self.model_id = model_id
        self.logger = logger or LoggingManager()

    @retry(
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        retry_error_callback=lambda retry_state: None
    )
    def generate_embeddings_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not texts:
            return None
            
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        payload = {
            'input': texts,
            'model': self.model_id,
            'encoding_format': 'float'
        }
        
        try:
            response = requests.post(
                self.url,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                json=payload,
                timeout=self.timeout * 2 
            )
            
            if response.status_code == 404:
                raise APIRequestError(f"Embedding endpoint not found at {self.url}")
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except ValueError:
                raise APIRequestError(f"API returned invalid JSON: {response.text[:200]}")

            if not isinstance(response_data, dict) or 'data' not in response_data:
                raise EmbeddingGenerationError("Invalid embedding response format")
                
            embeddings = []
            for item in response_data['data']:
                if 'embedding' in item and isinstance(item['embedding'], list):
                    embeddings.append(item['embedding'])
                else:
                    raise EmbeddingGenerationError("Embedding format invalid")
            
            self.last_request_time = time.time()
            return embeddings
            
        except requests.exceptions.Timeout:
            self.logger.log_error(APIRequestError(f"Timeout while connecting to {self.url}"))
            raise APIRequestError("Connection timeout - check if LM Studio is running and responsive")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code >= 500:
                raise APIRequestError(f"Server error ({status_code}): {e.response.text[:200]}")
            elif status_code == 400:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', e.response.text[:200])
                except Exception:
                    error_msg = e.response.text[:200]
                raise APIRequestError(f"Bad request: {error_msg}")
            else:
                raise APIRequestError(f"HTTP error ({status_code}): {e.response.text[:200]}")
        except (APIRequestError, EmbeddingGenerationError):
            raise
        except Exception as e:
            self.logger.log_error(EmbeddingGenerationError(f"Unexpected error: {str(e)}"))
            raise EmbeddingGenerationError(f"Unexpected error: {str(e)}")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        try:
            results = self.generate_embeddings_batch([text])
            return results[0] if results else None
        except (APIRequestError, EmbeddingGenerationError) as e:
            self.logger.log_error(e)
            return None