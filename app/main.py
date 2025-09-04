# Veritas: A grounded AI agent for PDFs.
# This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/4.0/

import requests
from config import AppConfig
from app.src.llm.chat import Chat, ChatConfig, LMStudioClient
from app.src.llm.embedding_generator import EmbeddingGenerator
from app.src.document_processing.pdf_formatter import PDFFormatter
from app.src.vector.vector_manager import VectorManager
from app.src.utils.logging_manager import LoggingManager

def get_loaded_models(api_url: str) -> list:
    try:
        resp = requests.get(api_url.replace("/chat/completions", "/models"), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        raise RuntimeError(f"Failed to query LM Studio models: {e}")

def initialize_components(config: AppConfig) -> tuple:
    logging_agent = LoggingManager()
    try:
        # Check loaded models
        models = get_loaded_models(config.completions_url)
        if not models:
            logging_agent.log_error("No models loaded in LM Studio. Please load a model and restart.")
            raise SystemExit("Fatal error: No models loaded in LM Studio.")

        logging_agent.log_info(f"Loaded models: {[m['id'] for m in models]}")
        logging_agent.log_info("Starting application with config:")
        logging_agent.log_info(f"Embeddings URL: {config.embeddings_url}")
        logging_agent.log_info(f"Completions URL: {config.completions_url}")
        logging_agent.log_info(f"Embedding Model ID: {config.embedding_model_id}")
        logging_agent.log_info(f"Completion Model ID: {config.completion_model_id}")
        logging_agent.log_info(f"Documents Directory: {config.documents_directory}\n")
        
        if not config.document_paths:
            logging_agent.log_error(f"No PDF file found in {config.documents_directory}")
            logging_agent.log_info("Please place your documents in the folder and try again.")
        logging_agent.log_info(f"Found {len(config.document_paths)} PDF documents\n")
        
        embedding_generator = EmbeddingGenerator(
            url=config.embeddings_url,
            timeout=config.request_timeout,
            model_id=config.embedding_model_id
        )
        
        test_embedding = embedding_generator.generate_embedding("Connection test...")
        if test_embedding is None:
            raise logging_agent.log_error(RuntimeError("LM Studio is not connected or models weren't successfully loaded (API connection failed)"))
        logging_agent.log_info("Embedding API connection test successful!")
        
        vector_manager = VectorManager(
            embedding_generator=embedding_generator,
            cache_file=config.cache_file,
            logger=logging_agent
        )
        
        cache_stats = vector_manager.get_stats()
        logging_agent.log_info(f"Initial cache: {cache_stats['documents']} docs, {cache_stats['chunks']} chunks")
        
        logging_agent.log_info(f"Processing {len(config.document_paths)} documents...")
        for i, path in enumerate(config.document_paths):
            try:
                if vector_manager.is_document_processed(path):
                    logging_agent.log_info(f'[{i+1}/{len(config.document_paths)}] Document already processed: {path}')
                    continue
                    
                logging_agent.log_info(f'[{i+1}/{len(config.document_paths)}] Processing document: {path}')
                extracted_text = PDFFormatter.extract_text(path)
                if not extracted_text or not extracted_text.strip():
                    logging_agent.log_error(Exception("No text extracted"), {"message": f"Unable to extract text from the document: {path}"})
                    continue
                    
                vector_manager.add_document(extracted_text, source_path=path)
            except Exception as e:
                logging_agent.log_error(e, {"message": f"File processing failed: {path}"})
        
        llm_client = LMStudioClient(api_url=config.completions_url)
        chat = Chat(
            vector_manager=vector_manager,
            llm_client=llm_client,
            model_id=config.completion_model_id,
            config=ChatConfig(
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                max_history_length=config.max_history_length
            ),
            logger=logging_agent
        )
        
        logging_agent.log_info("Initialization completed successfully")
        return embedding_generator, vector_manager, chat
        
    except Exception as e:
        logging_agent.log_error(e, {"message": "Initialization failed"})
        raise SystemExit("\n\nFatal initialization error, check the connection to LM Studio or the error messages above.\n") from e