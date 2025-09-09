# Veritas: Um Agente de IA Baseado em PDFs
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/Diegolinop/veritas/pulls)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Read in Portuguese](https://img.shields.io/badge/Leia%20em-Portugu%C3%AAs%20(BR)-blue)](README.pt-br.md)

Veritas é uma aplicação local que permite que você interaja com um agente de IA que responde perguntas **exclusivamente** com base no conteúdo dos documentos PDF que você fornecer. Ao fundamentar as respostas da IA no texto que você fez upload, o Veritas minimiza "alucinações" e garante respostas precisas e específicas ao contexto. Todo o processamento ocorre na sua máquina local, garantindo privacidade total dos dados.

## Funcionalidades

- **100% Local e Privado**: Tudo é executado na sua máquina. Seus documentos e conversas nunca saem do seu computador.
- **Contexto Alimentado por PDFs**: O agente de IA é restrito aos PDFs fornecidos por você, garantindo respostas verificáveis e relevantes.
- **Recuperação Eficiente**: Os documentos são analisados, vetorizados e armazenados em cache para uma busca semântica rápida e precisa.
- **Integração com LM Studio**: Utiliza modelos locais servidos via LM Studio para geração de linguagem e embeddings, oferecendo flexibilidade na escolha do modelo.

## Pré-requisitos

Antes de começar, certifique-se de ter o seguinte instalado e configurado:

1.  **Python 3.8 ou superior**
    *   Faça o download em [python.org](https://www.python.org/downloads/).
    *   Verifique a instalação: Abra um prompt de comando e execute `python --version`.

2.  **LM Studio**
    *   Faça o download e instale a partir do [site oficial do LM Studio](https://lmstudio.ai/).
    *   **Configurações Obrigatórias**: Após a instalação, abra o LM Studio e habilite o **Modo Desenvolvedor (Developer Mode)** ou **Modo Usuário Avançado (Power User Mode)** nas Configurações (Settings).

## Instalação & Setup

### Passo 1: Baixe e Configure Modelos no LM Studio

1.  **Inicie o LM Studio**.
2.  **Baixe os Modelos**:
    *   Na aba "Search" (Busca), encontre e baixe um **Modelo de Linguagem (LLM)** adequado (por exemplo, uma variante de Llama 2 ou Mistral).
    *   Encontre e baixe um **Modelo de Embeddings** (por exemplo, `all-MiniLM-L6-v2` ou `bge-small-en-v1.5` são escolhas comuns).
3.  **Carregue os Modelos para o Servidor**:
    *   Vá para a aba **"Local Server"** (Servidor Local).
    *   Em **"LLM"**, selecione o modelo de linguagem que você baixou.
    *   Em **"Embeddings"**, selecione o modelo de embeddings que você baixou.
    *   **Não inicie o servidor ainda.**

### Passo 2: Configure o Ambiente do Veritas

1.  **Execute o script de setup**:
    *   Clique duas vezes no arquivo `setup.bat` no diretório do projeto Veritas.
    *   Este script irá:
        *   Criar um ambiente virtual do Python.
        *   Instalar todas as dependências necessárias (por exemplo, `fastapi`, `scikit-learn`, `pypdf`).
        *   Criar os diretórios necessários (como `documents/`).

### Passo 3: Prepare Seus Documentos

1.  Coloque os arquivos PDF com os quais você deseja interagar no diretório `documents/` criado pelo script de setup.

### Passo 4: Inicie a Aplicação

1.  **Inicie o Servidor do LM Studio**:
    *   Volte para a aba **"Local Server"** no LM Studio.
    *   Certifique-se de que os modelos corretos estão selecionados.
    *   Clique no botão **"Start Server"** (Iniciar Servidor). Anote o URL do servidor (normalmente `http://localhost:1234/v1`).

2.  **Inicie o Veritas**:
    *   Clique duas vezes no arquivo `app.bat`.
    *   Aguarde o script processar seus PDFs. Esta etapa lê, divide e cria embeddings vetoriais para todos os documentos na pasta `documents/`. **O processo pode levar um tempo dependendo do número e do tamanho dos documentos.**
    *   Uma vez completo, seu navegador padrão deve abrir automaticamente em `http://127.0.0.1:8888`.

## Uso

1.  **Interface de Chat**: A interface web será aberta. Digite sua pergunta na caixa de entrada e pressione Enter.
2.  **Revise as Respostas**: O agente de IA processará sua consulta, pesquisará no conteúdo vetorizado dos seus PDFs e gerará uma resposta baseada exclusivamente naquele conteúdo.
3.  **Resetar**: Use o botão "Reset Chat" (Resetar Chat) para limpar o histórico da conversa atual.

## Solução de Problemas

| Problema | Causa Provável | Solução |
| :--- | :--- | :--- |
| Falha no `setup.bat`. | Python não instalado ou não está no PATH. | Reinstale o Python, certificando-se de marcar "Adicionar Python ao PATH" durante a instalação. |
| Erro de conexão com o servidor do LM Studio. | O servidor do LM Studio não está em execução. | Vá para a aba "Local Server" no LM Studio e clique em "Start Server". |
| | Modelo incorreto carregado. | Certifique-se de que um modelo LLM e um modelo de Embeddings estão selecionados e carregados na aba "Local Server". |
| O aplicativo falha ao processar PDFs. | Não há PDFs na pasta `documents/`. | Adicione arquivos PDF ao diretório `documents/` e reinicie o `app.bat`. |
| A IA dá respostas genéricas. | A recuperação não encontrou contexto relevante. | Reformule sua pergunta para usar palavras-chave que possam estar nos PDFs. |

## Licença

Este projeto está licenciado sob a **Licença Internacional Creative Commons Attribution-NonCommercial-ShareAlike 4.0** (CC BY-NC-SA 4.0). Isso significa que você é livre para compartilhar e adaptar o material para fins não comerciais, desde que dê o crédito apropriado e licencie quaisquer novas criações sob os mesmos termos.

Veja o arquivo [LICENSE](LICENSE.md) para detalhes completos.

## Agradecimentos

- **[LM Studio](https://lmstudio.ai/)**: Por fornecer uma maneira incrivelmente fácil de executar LLMs locais e modelos de embeddings.
- **[FastAPI](https://fastapi.tiangolo.com/)**: Pela estrutura web moderna e de alto desempenho.
- **[Scikit-learn](https://scikit-learn.org/)**: Pela funcionalidade de busca vetorial simples e eficaz.