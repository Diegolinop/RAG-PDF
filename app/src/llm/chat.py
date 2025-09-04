import re
import os
import json
import time
import hashlib
from typing import Generator, List, Dict, Optional
from dataclasses import dataclass
import requests

from constants import DEFAULT_TIMEOUT, MAX_HISTORY_LENGTH, MAX_TOKENS, TEMPERATURE
from app.src.vector.vector_manager import VectorManager
from app.src.utils.logging_manager import LoggingManager

class LLMClient:
    def stream_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float, 
        max_tokens: int
    ) -> Generator[str, None, None]:
        raise NotImplementedError

class LMStudioClient(LLMClient):
    def __init__(self, api_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.api_url = api_url
        self.timeout = timeout
        
    def stream_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str, 
        temperature: float, 
        max_tokens: int
    ) -> Generator[str, None, None]:
        payload = {
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'model': model,
            'stream': True,
        }

        try:
            with requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=self.timeout,
                stream=True
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data:'):
                            data = decoded_line[5:].strip()
                            if data != '[DONE]':
                                try:
                                    chunk = json.loads(data)
                                    if 'choices' in chunk and chunk['choices']:
                                        delta = chunk['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            yield delta['content']
                                except json.JSONDecodeError:
                                    continue
        except requests.exceptions.RequestException as e:
            yield f'\nERROR: Connection failed. Reason: {str(e)}'
        except Exception as e:
            yield f'\nERROR: Unexpected error. Reason: {str(e)}'

@dataclass
class ChatConfig:
    system_message = (
        "You are a competent analyst.\n"

        "When answering questions:\n"
        "1. Always consult the available documents first.\n"
        "2. Use the provided context snippets to answer questions thoroughly.\n"
        "3. If the context contains relevant information, use it confidently—even if it's not a perfect match.\n"
        "4. Connect related concepts across different snippets when possible.\n"
        "5. If you find partial information, acknowledge what was found and what might be missing.\n"
        "6. Avoid saying 'I didn't find anything' unless you have actually searched and found no relevant snippets.\n"
        "7. ALWAYS cite specific sources when referencing information from context snippets.\n"
        "8. Use the format 'as per patent [PATENT_NAME]' or 'according to [PATENT_NAME]' when citing information.\n"

        "Provide detailed answers while staying within the limit of {MAX_TOKENS} tokens.\n"
        "ONLY answer the question if the necessary information is contained within the provided context.\n"
        "If the context does not contain information needed to answer the question, DO NOT provide an answer."
    )
    temperature: float = TEMPERATURE
    max_tokens: int = MAX_TOKENS
    max_history_length: int = MAX_HISTORY_LENGTH

class Chat:
    def __init__(
        self,
        vector_manager: VectorManager,
        llm_client: LLMClient,
        model_id: str,
        config: ChatConfig = ChatConfig(),
        logger: Optional[LoggingManager] = None
    ):
        self.vector_manager = vector_manager
        self.llm_client = llm_client
        self.model_id = model_id
        self.config = config
        self.logger = logger or LoggingManager()
        self.conversation_history = [{
            'role': 'system',
            'content': config.system_message
        }]
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def stream_chat(self, user_input: str):
        self.logger.log_info(f"Processing user input (stream): {user_input[:100]}...")

        context_chunks = self.vector_manager.search(user_input)
        self.logger.log_info(f"Found {len(context_chunks)} context chunks (vector)")
        if not context_chunks:
            self.logger.log_info("Trying lexical fallback...")
            context_chunks = self.vector_manager.search_lexical(user_input)

        if context_chunks:
            context = self._build_context_from_chunks(context_chunks, user_input)
        else:
            context = "No relevant context found"

        augmented_input = f'Relevant Context:{context}\n\nUser Question: {user_input}\n'
        self._add_to_history('user', augmented_input)

        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        self.last_request_time = time.time()

        full_response_parts = []
        try:
            for chunk in self.llm_client.stream_response(
                messages=self.conversation_history,
                model=self.model_id,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            ):
                full_response_parts.append(chunk)
                yield chunk

            full = ''.join(full_response_parts)
            self._add_to_history('assistant', full)
            self._trim_history()
        except (requests.exceptions.RequestException, Exception) as e:
            self.logger.log_error(e)
            yield f"\nERROR: {str(e)}"

    def _build_context_from_chunks(self, context_chunks, user_input: str) -> str:
        document_ids = [pid.upper() for pid in re.findall(r'(CN\d+[A-Z]?)', user_input, re.IGNORECASE)]

        if document_ids:
            prioritized = [c for c in context_chunks if any(pid in c[2].upper() for pid in document_ids)]
            remainder = [c for c in context_chunks if c not in prioritized]
            ordered = prioritized + remainder
        else:
            ordered = context_chunks

        seen = set()
        deduped = []
        for text, similarity, source, chunk_idx in ordered:
            key = (text[:200], source)
            if key in seen:
                continue
            seen.add(key)
            deduped.append((text, similarity, source, chunk_idx))

        max_chars = 12000
        per_chunk_limit = 700
        max_chunks = 12

        query_tokens = set(t.lower() for t in re.findall(r'[A-Za-z0-9]+', user_input) if len(t) > 3)

        parts = []
        used = 0
        for text, similarity, source, chunk_idx in deduped:
            excerpt = self._extract_relevant_excerpt(text, query_tokens, per_chunk_limit)
            if not excerpt:
                excerpt = text[:per_chunk_limit]

            clean_source = self._clean_source_name(source)
            confidence_level = "HIGH" if similarity >= 0.85 else "MEDIUM" if similarity >= 0.70 else "LOW"
            part = f'[{clean_source}, Section {chunk_idx + 1} - Confidence {confidence_level} ({similarity:.2f})]: {excerpt}'

            if used + len(part) > max_chars:
                break
            parts.append(part)
            used += len(part) + 2
            if len(parts) >= max_chunks:
                break

        return '\n\n'.join(parts)

    def _extract_relevant_excerpt(self, text: str, query_tokens: set, limit: int) -> str:
        sentences = re.split(r'(?<=[\.!?;])\s+', text)
        scored = []
        for s in sentences:
            lower = s.lower()
            score = 0
            for t in query_tokens:
                if t in lower:
                    score += 1
            score += lower.count('%')
            if score > 0:
                scored.append((score, s))

        if not scored:
            return ''

        scored.sort(key=lambda x: x[0], reverse=True)
        excerpt = ''
        for _, s in scored:
            if len(excerpt) + len(s) + 1 > limit:
                break
            excerpt = (excerpt + ' ' + s).strip()
        return excerpt[:limit]
    
    def _clean_source_name(self, source: str) -> str:
        if os.path.sep in source:
            source = os.path.basename(source)
        
        for ext in ['.pdf', '.txt', '.doc', '.docx']:
            if source.endswith(ext):
                source = source[:-len(ext)]
        
        return source
    
    def _add_to_history(self, role: str, content: str) -> None:
        self.conversation_history.append({'role': role, 'content': content})
    
    def _trim_history(self) -> None:
        max_history = self.config.max_history_length
        if len(self.conversation_history) > max_history + 1:
            system_message = self.conversation_history[0]
            recent_messages = self.conversation_history[-max_history:]
            self.conversation_history = [system_message] + recent_messages