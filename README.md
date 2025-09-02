# Smart Recipe Finder

A FastAPI-based service for searching and managing cooking recipes. Supports two types of search:

1. **Ingredient-based filtering** (include or exclude ingredients when searching).
2. **Smart natural-language search**  
* /search: uses a spaCy-based parser (key-words/difficulty/time) with PostgreSQL full-text index.
* /smart_search: uses GPT-powered parsing with the full-text index (requires an OpenAI API key). If no key is provided, this endpoint will not work.
---

## Features

Search is powered by PostgreSQL full‑text index for efficient querying, ensuring fast ingredient filtering and keyword matching.

* Create, read, update, delete (CRUD) recipes.
* Ingredient-based search with include/exclude filters, plus text search across title, cuisine, and tags.
* Natural-language queries (e.g., "Quick Italian under 30 minutes") interpreted to structured filters.
* Robust testing suite with pytest and pytest-asyncio.
* Docker and Docker Compose support.

---

## Running with Docker

```bash
docker-compose up --build
```

* Brings up PostgreSQL and the FastAPI web app.
* Access the API at: `http://localhost:8000`
* Swagger docs available at: `http://localhost:8000/docs`

###

---

## Running Locally (without Docker)

1. Ensure PostgreSQL is running, install dependencies from `requirements.txt`, install the spaCy model locally:

```bash
python -m spacy download en_core_web_sm
```

and set environment variables in `.env`.

2\. Run migrations:

```bash
alembic upgrade head
```

3. Start the app:

```bash
uvicorn main:app --reload
```

---

## Running Tests

### Locally

```bash
pytest
```

### Inside Docker

Run tests in the `app` service:

```bash
docker-compose exec app pytest
```

---

## Summary

This project delivers:

* Flexible recipe search (text + advanced + smart natural language).
* Used technologies FastAPI, SQLAlchemy async, Alembic, unit-of-work/service layer.
* Dockerized setup with full end-to-end development & testing.
