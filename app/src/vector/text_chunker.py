import re
from typing import List
import tiktoken
from constants import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP

class TextChunker:
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP):
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk size")
            
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding('cl100k_base')
        
        self.sentence_endings = re.compile(
            r'(?<!\w\.\w.)'
            r'(?<![A-Z][a-z]\.)'
            r'(?<=\.|\?|\!|;)\s+'
        )
        
        self.section_pattern = re.compile(
            r'\n(\d+\.\s+.*?|\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b)\n'
        )
        
        self.header_footer_patterns = [
            r'©Questel - FAMPAT',
            r'Page \d+',
            r'\d{4}/\d{2}/\d{2}',
            r'Publication numbers',
            r'Current assignees',
            r'Inventors',
            r'Priority data including date',
            r'Family',
            r'IPC - International classification',
            r'CPC - Cooperative classification',
        ]
        
        self.header_footer_regex = re.compile('|'.join(self.header_footer_patterns), re.IGNORECASE)

    def _clean_text(self, text: str) -> str:
        text = self.header_footer_regex.sub('', text)
        
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        text = re.sub(r'\f', '\n', text)
        
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = self.sentence_endings.split(text)
        
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences

    def _create_chunks_from_sentences(self, sentences: List[str]) -> List[str]:
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))
            
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) >= 50:
                    chunks.append(chunk_text)
                
                overlap_sentences = []
                overlap_tokens = 0
                
                for prev_sentence in reversed(current_chunk):
                    prev_tokens = len(self.encoding.encode(prev_sentence))
                    if overlap_tokens + prev_tokens <= self.overlap:
                        overlap_sentences.insert(0, prev_sentence)
                        overlap_tokens += prev_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= 50:
                chunks.append(chunk_text)
        
        return chunks

    def chunk_text(self, text: str) -> List[str]:
        if not text.strip():
            return []

        cleaned_text = self._clean_text(text)
        
        if not cleaned_text:
            return []

        sentences = self._split_into_sentences(cleaned_text)
        
        if not sentences:
            return []

        chunks = self._create_chunks_from_sentences(sentences)
        
        final_chunks = []
        for chunk in chunks:
            chunk = re.sub(r'\s+', ' ', chunk).strip()
            
            if len(chunk) >= 50 and not self._is_noise_chunk(chunk):
                final_chunks.append(chunk)
        
        return final_chunks

    def _is_noise_chunk(self, chunk: str) -> bool:
        words = chunk.split()
        if len(words) < 10:
            return True
        
        special_char_ratio = len(re.findall(r'[^\w\s]', chunk)) / len(chunk)
        if special_char_ratio > 0.4:
            return True
        
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > len(words) * 0.2:
            return True
        
        return False