# RAG-PDF Chat
*Um chatbot local e privado que responde perguntas usando seus documentos PDF como única fonte de conhecimento.*

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Leia em Português](https://img.shields.io/badge/Read%20in-English-blue)](README.md)

Esta ferramenta de Geração Aumentada por Recuperação (Retrieval-Augmented Generation) é uma aplicação local que permite interagir com um agente de IA que responde perguntas baseando-se **exclusivamente** no conteúdo dos documentos PDF que você fornecer. Ao fundamentar as respostas da IA no texto que você enviou, a ferramenta minimiza alucinações e garante respostas precisas e específicas ao contexto. Todo o processamento ocorre em seu computador local, garantindo total privacidade dos dados.

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado e configurado:

1.  **Sistema Operacional Windows**
    *   Esta aplicação requer o LM Studio, que atualmente está disponível apenas para Windows

2.  **Python 3.8 ou superior**
    *   Faça o download em [python.org](https://www.python.org/downloads/)
    *   Verifique a instalação: Abra um prompt de comando e execute `python --version`

3.  **LM Studio**
    *   Faça o download e instale a partir do [site oficial do LM Studio](https://lmstudio.ai/)
    *   **Configurações Necessárias**: Após a instalação, abra o LM Studio e habilite o **Modo Desenvolvedor (Developer Mode)** ou **Modo Usuário Avançado (Power User Mode)** nas configurações.

## Instalação & Configuração

### Passo 1: Baixar e Configurar Modelos no LM Studio

1.  **Inicie o LM Studio**
2.  **Baixe os Modelos**:
    *   Na aba "Search" (Busca), encontre e baixe um **Modelo de Linguagem (LLM)** adequado (por exemplo, uma variante do Llama 3 ou Mistral)
    *   Baixe também um **Modelo de Embeddings** (por exemplo, `Qwen3-Embedding-0.6B` ou `embeddinggemma-300m` são escolhas comuns)
3.  **Inicie o Servidor Local**:
    *   Vá até a aba **"Developer"** (Desenvolvedor)
    *   Ative o botão do servidor local ou use (Ctrl + .)

### Passo 2: Configurar o Ambiente RAG

1.  **Execute o script de configuração**:
    *   Dê um duplo clique no arquivo `setup.bat` no diretório do projeto `rag-pdf`
    *   Este script irá:
        *   Criar um ambiente virtual Python
        *   Instalar todas as dependências necessárias (ex.: `fastapi`, `scikit-learn`, `pypdf`)
        *   Criar os diretórios necessários (como `documents/`)
    *   Alternativamente, você pode criar um ambiente virtual manualmente e instalar as dependências a partir do arquivo `requirements.txt`

### Passo 3: Preparar Seus Documentos

1.  Coloque os arquivos PDF com os quais você deseja interagir dentro do diretório `documents/` criado pelo script de configuração

### Passo 4: Iniciar a Aplicação

1.  **Inicie o Servidor do LM Studio**:
    *   Volte para a aba **"Developer"** no LM Studio
    *   Na seção **"Select a model to load"** (Selecione um modelo para carregar), selecione os modelos que você baixou
    *   Certifique-se de que o status do servidor está como **"running"** (executando). Se não estiver, inicie o servidor seguindo as instruções do Passo 1.3 ("Inicie o Servidor Local").

2.  **Inicie a aplicação**:
    *   Dê um duplo clique no arquivo `app.bat`
    *   Aguarde o script processar seus PDFs. Esta etapa lê, segmenta (chunking) e cria vetores de embedding (vector embeddings) para todos os documentos na pasta `documents/`. **O processo pode levar um tempo dependendo da quantidade e do tamanho dos documentos**
    *   Uma vez completo, seu navegador padrão deve abrir automaticamente em `http://127.0.0.1:8888`
    *   Talvez você precise atualizar a página se ela abrir antes do seu servidor estar pronto

## Como Usar

1.  **Interface de Chat**: A interface web será aberta. Digite sua pergunta na caixa de entrada e pressione Enter
2.  **Revisar Respostas**: O agente de IA processará sua consulta, buscará no conteúdo vectorizado dos seus PDFs e gerará uma resposta baseada apenas naquele conteúdo
3.  **Resetar**: Use o botão "Reset Chat" (Resetar Chat) para limpar o histórico da conversa atual

## Solução de Problemas

| Problema | Causa Provável | Solução |
| :--- | :--- | :--- |
| `setup.bat` falha. | Python não instalado ou não está no PATH. | Reinstale o Python, certificando-se de marcar "Adicionar Python ao PATH" durante a instalação. |
| Erro de conexão com o servidor do LM Studio. | O servidor do LM Studio não está em execução. | Vá para a aba "Local Server" (Servidor Local) no LM Studio e clique em "Start Server" (Iniciar Servidor). |
| | Modelo incorreto carregado. | Certifique-se de que tanto um LLM quanto um modelo de Embeddings estão selecionados e carregados na aba "Local Server". |
| Aplicativo falha ao processar PDFs. | Não há PDFs na pasta `documents/`. | Adicione arquivos PDF ao diretório `documents/` e reinicie o `app.bat`. |
| A IA dá respostas genéricas. | A recuperação não encontrou contexto relevante. | Reformule sua pergunta para usar palavras-chave que possam estar nos PDFs. |

## Licença

Este projeto está licenciado sob a **Licença Internacional Creative Commons Attribution-NonCommercial-ShareAlike 4.0** (CC BY-NC-SA 4.0). Isso significa que você é livre para compartilhar e adaptar o material para fins não comerciais, desde que dê o crédito apropriado e licencie quaisquer novas criações sob os mesmos termos.

Consulte o arquivo [LICENSE](LICENSE.md) para obter detalhes completos.