# LangChain Assistant Project

This project implements an intelligent assistant capable of analyzing Python code, generating unit tests, and explaining them. It uses LangChain, FastAPI, and Streamlit, containerized with Docker.

## Structure

- **src/api/authentication**: Authentication service (FastAPI).
- **src/api/assistant**: Main assistant service (FastAPI + LangChain).
- **src/core**: Core LangChain logic (LLM, Chains, Parsers).
- **src/prompts**: Prompt templates.
- **src/memory**: Chat memory management.
- **src/app.py**: Streamlit UI.

## Setup

1.  **Environment Variables**:
    Ensure your `.env` file contains the following keys:
    ```env
    GROQ_API_KEY=your_groq_api_key
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=your_langsmith_api_key
    ```

2.  **Build and Run**:
    The project is orchestrated via Docker Compose. Use the Makefile for convenience:
    ```bash
    make up
    ```
    To stop:
    ```bash
    make down
    ```
    To view logs:
    ```bash
    make logs
    ```

## Usage via CLI (Docker)

You can interact with the assistant using the provided CLI script, even from within Docker. This is useful for sending files directly.

### 1. Command Syntax
```bash
python src/cli_client.py --mode <mode> --file <path_to_file>
```
Modes: `analyze`, `generate`, `explain`, `pipeline`

### 2. Running via Docker
To send a local file to the assistant running in Docker, you can use `docker exec` to run the script inside the running `main_service` container.

**Example: Analyze a local file**
Assuming you have a file `my_code.py` in the `src` folder (which is mounted to `/app/src`):

```bash
docker exec -it main_service python src/cli_client.py --mode analyze --file src/my_code.py
```

*Note: Since the volume `./src` is mapped to `/app/src`, any file you place in `src/` locally is visible inside the container.*

## Services & Ports

- **Auth API**: `http://localhost:8000` (Docs: `/docs`)
- **Assistant API**: `http://localhost:8001` (Docs: `/docs`)
- **Streamlit UI**: `http://localhost:8501`

## Verification & Testing

You can verify the system using the Streamlit UI or via API calls.

### Using Streamlit (Recommended)
1. Open [http://localhost:8501](http://localhost:8501).
2. **Signup**: Go to "Signup" tab, create a user (e.g. `test` / `password`).
3. **Login**: Go to "Login" tab, use credentials.
4. **Analyze**: Enter Python code (e.g. `def add(a,b): return a+b`) and click Analyze.
5. **Generate Test**: Enter proper function code and generate a pytest.
6. **Explain Test**: Paste the generated test and get an explanation.
7. **Full Pipeline**: Enter code to run all steps (check, generate, explain) if code is optimal.
8. **Chat**: Chat with the assistant. Check **History** to see saved messages.

### Automated Verification Schema (API)
The APIs support the following actions verified during development:
- `POST /signup` & `POST /login`
- `POST /analyze` (Returns optimization status, issues, suggestions)
- `POST /generate_test` (Returns pytest code)
- `POST /explain_test` (Returns explanation)
- `POST /full_pipeline` (Orchestrates above steps)
- `POST /chat` & `GET /history` (Conversational memory)
