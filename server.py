from typing import Generator
from contextlib import asynccontextmanager
import asyncio
import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
import uvicorn

from config import AppConfig
from app.main import initialize_components
from app.src.utils.logging_manager import LoggingManager
logger = LoggingManager()

# Global flag to track initialization status
INITIALIZED = False
INITIALIZATION_STARTED = False
INITIALIZATION_PROGRESS = 0
INITIALIZATION_MESSAGE = "Starting up..."

@asynccontextmanager
async def lifespan(app: FastAPI):
    global INITIALIZED, INITIALIZATION_STARTED, INITIALIZATION_PROGRESS, INITIALIZATION_MESSAGE
    
    # Startup - start initialization in background thread
    INITIALIZATION_STARTED = True
    logger.log_info("Starting initialization in background thread...")
    
    def initialize_in_background():
        global INITIALIZED, INITIALIZATION_PROGRESS, INITIALIZATION_MESSAGE
        
        try:
            INITIALIZATION_MESSAGE = "Loading configuration..."
            INITIALIZATION_PROGRESS = 10
            time.sleep(0.5)  # Simulate some work
            
            INITIALIZATION_MESSAGE = "Initializing components..."
            INITIALIZATION_PROGRESS = 20
            config = AppConfig()
            
            INITIALIZATION_MESSAGE = "Loading vector cache..."
            INITIALIZATION_PROGRESS = 30
            _, vector_manager, chat = initialize_components(config)
            
            # Store components in app state
            app.state.vector_manager = vector_manager
            app.state.chat = chat
            
            INITIALIZATION_MESSAGE = "Building search index..."
            INITIALIZATION_PROGRESS = 70
            # Force index building by doing a simple search
            try:
                vector_manager.search("test")
            except Exception as e:
                logger.log_error(f"Index building test failed: {str(e)}")
            
            INITIALIZATION_MESSAGE = "Finalizing..."
            INITIALIZATION_PROGRESS = 90
            time.sleep(0.5)  # Simulate finalization
            
            INITIALIZED = True
            INITIALIZATION_PROGRESS = 100
            logger.log_info("Background initialization completed successfully!")
            
        except Exception as e:
            logger.log_error(f"Background initialization failed: {str(e)}")
            INITIALIZATION_MESSAGE = f"Initialization failed: {str(e)}"
    
    # Start initialization in a background thread
    init_thread = threading.Thread(target=initialize_in_background, daemon=True)
    init_thread.start()
    
    yield
    
    # Shutdown
    if INITIALIZED:
        logger.log_info("Saving vector cache...")
        app.state.vector_manager.close()
        stats = app.state.vector_manager.get_stats()
        logger.log_info(f"Final cache: {stats['documents']} docs, {stats['chunks']} chunks")


app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
def root_page() -> str:
    return """
<!doctype html>
<!--AI-generated page because I hate doing front-end.-->
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Veritas</title>
    <style>
      :root {
        --bg: #F4F5F6;
        --text: #39393A;
        --muted: #B4ADA3;
        --primary: #5C95FF;
        --white: #FFFFFF;
      }
      html, body { height: 100%; margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, \"Apple Color Emoji\", \"Segoe UI Emoji\"; }
      body { background: var(--bg); color: var(--text); }
      .page { display: flex; flex-direction: column; height: 100vh; }
      .messages { flex: 1 1 auto; overflow-y: auto; padding: 16px; }
      .empty { height: 100%; display: flex; align-items: center; justify-content: center; color: var(--muted); text-align: center; }
      .bubble { max-width: min(80ch, 80%); border-radius: 16px; padding: 12px 16px; }
      .row { display: flex; margin: 8px 0; }
      .row.user { justify-content: flex-end; }
      .row.assistant { justify-content: flex-start; }
      .bubble.user { background: var(--primary); color: var(--white); margin-left: 48px; }
      .bubble.assistant { background: var(--white); color: var(--text); margin-right: 32px; border: 1px solid rgba(180,173,163,0.1); box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
      .footer { background: var(--white); border-top: 1px solid rgba(180,173,163,0.2); padding: 16px; }
      .toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
      .reset { padding: 8px 12px; font-size: 12px; color: var(--white); background: var(--muted); border-radius: 999px; border: none; cursor: pointer; }
      .hint { font-size: 12px; color: var(--muted); text-align: center; margin-top: 8px; }
      .form { display: flex; gap: 8px; align-items: center; }
      .inputWrap { position: relative; flex: 1 1 auto; }
      .input { width: 93%; padding: 12px 44px 12px 12px; border-radius: 999px; border: 1px solid rgba(180,173,163,0.3); outline: none; background: var(--bg); color: var(--text); }
      .send { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); background: var(--primary); color: var(--white); border-radius: 999px; border: 0; width: 32px; height: 32px; cursor: pointer; }
      .send:disabled { background: var(--muted); cursor: not-allowed; }
      .assistantBadge { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted); margin-bottom: 6px; }
      .assistantBadge .dot { width: 24px; height: 24px; background: var(--primary); border-radius: 999px; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; }
      .pre { white-space: pre-wrap; }
      .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
      }
      .loading-spinner {
        border: 4px solid var(--bg);
        border-top: 4px solid var(--primary);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
      }
      .loading-text {
        margin-top: 16px;
        color: var(--text);
        font-size: 16px;
      }
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      .hidden {
        display: none;
      }
      .init-loading {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--bg);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2000;
      }
      .init-loading-content {
        text-align: center;
        max-width: 400px;
        padding: 20px;
      }
      .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--white);
        border-radius: 4px;
        margin: 20px 0;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        background: var(--primary);
        width: 0%;
        transition: width 0.3s ease;
      }
    </style>
  </head>
  <body>
    <div id="initLoading" class="init-loading">
      <div class="init-loading-content">
        <div style="font-size: 24px; margin-bottom: 16px; font-weight: 500;">VERITAS</div>
        <div class="loading-spinner" style="margin: 0 auto;"></div>
        <div id="initMessage" class="loading-text">Initializing AI system, please wait...</div>
        <div class="progress-bar">
          <div id="progressFill" class="progress-fill"></div>
        </div>
        <div id="initStatus" style="font-size: 14px; color: var(--muted);">Loading embeddings and building index...</div>
        <div style="font-size: 14px; color: var(--muted);">This might take a while</div>
      </div>
    </div>
    
    <div id="loadingOverlay" class="loading-overlay hidden">
      <div style="text-align: center;">
        <div class="loading-spinner"></div>
        <div class="loading-text">Processing your request...</div>
      </div>
    </div>
    
    <div id="appContent" class="page" style="display: none;">
      <div id=\"messages\" class=\"messages\">
        <div id=\"empty\" class=\"empty\"> 
          <div>
            <div style=\"font-size: 18px; margin-bottom: 8px;\">Welcome to Veritas</div>
            <div style=\"font-size: 14px;\">Powered by your local LLM</div>
            <div style=\"font-size: 12px; margin-top: 8px;\">Start a conversation by typing a message below</div>
          </div>
        </div>
      </div>
      <div class=\"footer\">
        <div class=\"toolbar\">
          <button id=\"reset\" class=\"reset\">Reset Chat</button>
          <div style=\"font-size: 12px; color: var(--muted);\">Local Model</div>
        </div>
        <form id=\"form\" class=\"form\">
          <div class=\"inputWrap\">
            <input id=\"input\" class=\"input\" type=\"text\" placeholder=\"Type your message...\" disabled />
            <button id=\"send\" class=\"send\" title=\"Send\" disabled>➤</button>
          </div>
        </form>
        <div class=\"hint\">Press Enter to send your message</div>
      </div>
    </div>
    <script>
      const messagesEl = document.getElementById('messages');
      const inputEl = document.getElementById('input');
      const sendEl = document.getElementById('send');
      const formEl = document.getElementById('form');
      let emptyEl = document.getElementById('empty');
      const resetEl = document.getElementById('reset');
      const loadingOverlay = document.getElementById('loadingOverlay');
      const initLoading = document.getElementById('initLoading');
      const appContent = document.getElementById('appContent');
      const progressFill = document.getElementById('progressFill');
      const initStatus = document.getElementById('initStatus');
      const initMessage = document.getElementById('initMessage');

      // Check initialization status
      let initializationCheckInterval;
      let lastProgress = 0;
      
      function updateProgress(progress, message) {
        progressFill.style.width = progress + '%';
        if (message) {
          initMessage.textContent = message;
        }
        initStatus.textContent = `Progress: ${progress}%`;
      }
      
      function checkInitialization() {
        fetch('/api/health')
          .then(response => response.json())
          .then(data => {
            if (data.initialized) {
              // Fully initialized
              clearInterval(initializationCheckInterval);
              updateProgress(100, 'Initialization complete!');
              
              // Show app content and hide loading
              setTimeout(() => {
                initLoading.style.display = 'none';
                appContent.style.display = 'flex';
                inputEl.disabled = false;
                sendEl.disabled = true;
              }, 500);
            } else if (data.started) {
              // Still initializing, update progress
              if (data.progress !== undefined && data.progress > lastProgress) {
                lastProgress = data.progress;
                updateProgress(data.progress, data.message);
              }
            } else {
              // Not started yet
              initMessage.textContent = 'Waiting for initialization to start...';
            }
          })
          .catch(error => {
            console.error('Error checking initialization status:', error);
            initMessage.textContent = 'Connection error, retrying...';
          });
      }
      
      // Start checking initialization status
      initializationCheckInterval = setInterval(checkInitialization, 1000);
      checkInitialization(); // Initial check

      function showLoading() {
        loadingOverlay.classList.remove('hidden');
      }
      
      function hideLoading() {
        loadingOverlay.classList.add('hidden');
      }

      function setEmptyVisible(visible){ emptyEl.style.display = visible ? 'flex' : 'none'; }
      function createRow(role){ const r = document.createElement('div'); r.className = 'row ' + role; return r; }
      function createBubble(role){ const b = document.createElement('div'); b.className = 'bubble ' + role; return b; }
      function scrollToBottom(){ messagesEl.scrollTop = messagesEl.scrollHeight; }

      function addUserMessage(text){
        setEmptyVisible(false);
        const row = createRow('user');
        const bubble = createBubble('user');
        bubble.textContent = text;
        row.appendChild(bubble);
        messagesEl.appendChild(row);
        scrollToBottom();
      }

      function addAssistantContainer(){
        const row = createRow('assistant');
        const bubble = createBubble('assistant');
        const badge = document.createElement('div');
        badge.className = 'assistantBadge';
        badge.innerHTML = '<span class="dot">AI</span><span>Assistant</span>';
        const content = document.createElement('div');
        content.className = 'pre';
        bubble.appendChild(badge);
        bubble.appendChild(content);
        row.appendChild(bubble);
        messagesEl.appendChild(row);
        scrollToBottom();
        return content;
      }

      inputEl.addEventListener('input', () => {
        sendEl.disabled = inputEl.value.trim().length === 0;
      });

      resetEl.addEventListener('click', async () => { 
        // Clear frontend
        messagesEl.innerHTML = '<div id="empty" class="empty"> <div><div style="font-size: 18px; margin-bottom: 8px;">Welcome to Veritas</div><div style="font-size: 14px;">Powered by your local LLM</div><div style="font-size: 12px; margin-top: 8px;">Start a conversation by typing a message below</div></div></div>'; 
        emptyEl = document.getElementById('empty');
        
        // Clear backend chat history
        try {
          await fetch('/api/reset', { method: 'POST' });
          console.log('Chat history cleared');
        } catch (err) {
          console.error('Failed to clear chat history:', err);
        }
      });

      async function sendMessage() {
        const text = inputEl.value.trim();
        if(!text) return;
        console.log('Sending message:', text);
        inputEl.value = '';
        sendEl.disabled = true;
        addUserMessage(text);
        
        // Show loading overlay
        showLoading();
        
        const assistantContent = addAssistantContainer();
        try {
          const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
          });
          console.log('Response status:', resp.status);
          if (!resp.ok) {
            throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
          }
          
          // Hide loading overlay once we start receiving data
          hideLoading();
          
          const reader = resp.body.getReader();
          const decoder = new TextDecoder();
          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            assistantContent.textContent += decoder.decode(value);
            scrollToBottom();
          }
        } catch (err) {
          console.error('Error:', err);
          // Hide loading overlay on error too
          hideLoading();
          assistantContent.textContent += '[Error] ' + (err?.message || 'Failed to fetch');
        } finally {
          sendEl.disabled = false;
          inputEl.focus();
        }
      }

      formEl.addEventListener('submit', async (e) => {
        e.preventDefault();
        await sendMessage();
      });

      sendEl.addEventListener('click', async (e) => {
        e.preventDefault();
        await sendMessage();
      });
    </script>
  </body>
  </html>
    """

@app.get("/api/health")
async def health_check():
    """Endpoint to check if the application is initialized and ready"""
    global INITIALIZED, INITIALIZATION_STARTED, INITIALIZATION_PROGRESS, INITIALIZATION_MESSAGE
    
    if INITIALIZED:
        return {
            "initialized": True, 
            "started": True, 
            "message": "System is ready",
            "progress": 100
        }
    elif INITIALIZATION_STARTED:
        return {
            "initialized": False, 
            "started": True, 
            "message": INITIALIZATION_MESSAGE,
            "progress": INITIALIZATION_PROGRESS
        }
    else:
        return {
            "initialized": False, 
            "started": False, 
            "message": "Initialization not started yet",
            "progress": 0
        }

@app.post("/api/chat")
async def api_chat(request: Request):
    if not INITIALIZED:
        return JSONResponse(
            {"error": "System not initialized yet. Please wait."},
            status_code=503
        )
    
    data = await request.json()
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return StreamingResponse((chunk for chunk in []), media_type="text/plain")

    def streamer() -> Generator[bytes, None, None]:
        for chunk in request.app.state.chat.stream_chat(user_message):
            if chunk:
                yield chunk.encode("utf-8")

    return StreamingResponse(streamer(), media_type="text/plain")

@app.post("/api/reset")
async def api_reset(request: Request):
    if not INITIALIZED:
        return JSONResponse(
            {"error": "System not initialized yet. Please wait."},
            status_code=503
        )
    
    request.app.state.chat.conversation_history = [{
        'role': 'system',
        'content': request.app.state.chat.config.system_message
    }]
    return {"status": "reset"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)