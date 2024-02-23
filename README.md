# chat-search

![CICD](https://github.com/hemslo/chat-search/actions/workflows/cicd.yml/badge.svg)

Chat with custom data, search via natural language.

Demo: Chat about my blog, https://chat-search.hemslo.io/chat/playground

## Usage

### Setup .env

```shell
cp .env.example .env
```

Populate `.env` file with the required environment variables.

| Name                            | Value                                    | Default                            |
|---------------------------------|------------------------------------------|------------------------------------|
| AUTH_TOKEN                      | auto token used for ingest               |                                    |
| CHAT_PROVIDER                   | model provider, `openai` or `ollama`     | `openai`                           |
| DEBUG                           | enable DEBUG, `1` or `0`                 | `0`                                |
| EMBEDDING_DIM                   | embedding dimensions                     | `1536`                             |
| EMBEDDING_PROVIDER              | embedding provider, `openai` or `ollama` | `openai`                           |
| OLLAMA_CHAT_MODEL               | ollama chat model                        | `llama2`                           |
| OLLAMA_EMBEDDING_MODEL          | ollama embedding model                   | `llama2`                           |
| OPENAI_API_KEY                  | openai api key                           |                                    |
| OPENAI_URL                      | ollama url                               | `http://localhost:11434`           |
| OPENAI_CHAT_MODEL               | openai chat model                        | `gpt-3.5-turbo-0125`               |
| OPENAI_EMBEDDING_MODEL          | openai embedding model,                  | `text-embedding-3-small`           |
| REDIS_URL                       | redis url                                | `redis://localhost:6379/`          |
| REPHRASE_PROMPT                 | prompt for rephrase                      | check [config.py](/app/config.py)  |
| RETRIEVAL_QA_CHAT_SYSTEM_PROMPT | prompt for retrieval                     | check [config.py](/app/config.py)  |
| VERBOSE                         | enable verbose, `1` or `0`               | `0`                                |

### Run on host

#### Install dependencies

```shell
pip install poetry==1.7.1
poetry shell
poetry install
```

#### Start dependencies

Start redis

```shell
docker compose -f compose.redis.yaml up
```

(Optional) Start Ollama, follow [Ollama instructions](https://github.com/ollama/ollama)

```shell
ollama serve
ollama pull llama2
```

#### Launch LangServe

```bash
langchain serve
```

Visit http://localhost:8000/

### Run in Docker

(Optional) Start Ollama, follow [Ollama instructions](https://github.com/ollama/ollama).

```shell
ollama serve
ollama pull llama2
```

Start all

```shell
docker compose up --build
```

Visit http://localhost:8000/

## Ingest data

```shell
crawl --sitemap-url $SITEMAP_URL --auth-token $AUTH_TOKEN
```

Check [crawl.yml](.github/workflows/crawl.yml) for web crawling,

Example auto ingest after Github Pages deploy,
[jekyll.yml](https://github.com/hemslo/hemslo.github.io/blob/master/.github/workflows/jekyll.yml).

## Deployment

Check [cicd.yml](.github/workflows/cicd.yml) for Google Cloud Run deployment,
[deploy-to-cloud-run](https://github.com/marketplace/actions/deploy-to-cloud-run).
