# LangChain Exam: Python Unit Test Assistant

## General Instructions

The objective of the exam is to develop an intelligent assistant capable of analyzing Python code, automatically generating unit tests with pytest, and explaining these tests in an educational manner.

To achieve this, you will need to set up a complete architecture combining several tools:

- **LangChain** to manage chains, prompts, parsers, and memory
- **FastAPI** to expose functionalities through a secure API
- **Docker** with a **Makefile** to containerize and orchestrate the entire project
- A user interface with **Streamlit** can be added as a complement, but it remains OPTIONAL.

To carry out this exam, a [GitHub repository](https://github.com/DataScientest/exam_Langchain) is made available to you. The first step consists of cloning this repository on your machine in order to have the expected project structure (folders, configuration files, Makefile, etc.).

This repository serves as a skeleton: it provides you with the basic architecture that you will have to complete by implementing the various components (LangChain chains, parsers, memory, API, containerization).

```txt
exam_Langchain/                     
├── .env                             # Environment variables (GROQ + LangSmith API keys)
├── .python-version                  # Python version used (here 3.13)
├── pyproject.toml                   # Project dependency management and configuration
├── Makefile                         # Commands to build/up/down the containers
├── docker-compose.yml               # Service orchestration (auth, main, streamlit)
├── README.md                        # Main project documentation
└── src/                             # Project source code
    ├── api/                         # Folder grouping API services
    │   ├── authentification/        # Authentication service
    │   │   ├── Dockerfile.auth      
    │   │   ├── requirements.txt     
    │   │   └── auth.py              # FastAPI code to manage signup, login, me
    │   └── assistant/               # Main LangChain assistant service
    │       ├── Dockerfile.main      
    │       ├── requirements.txt     
    │       └── main.py              # FastAPI code for analysis/generation/tests/chat
    ├── core/                        # Central LangChain components
    │   ├── llm.py                   # Language model configuration (LLM + fallback)
    │   ├── chains.py                # Definition of different chains (analysis, test, etc.)
    │   └── parsers.py               # Pydantic parsers to structure LLM outputs
    ├── memory/                       
    │   └── memory.py                # Functions to manage multi-user history
    ├── prompts/                     
    │   └── prompts.py               # Prompts for analysis, generation, explanation, chat
    ├── Dockerfile.streamlit (optional)   # Dockerfile for the Streamlit user interface
    ├── requirements.txt (optional)       # Dependencies for the Streamlit app
    └── app.py (optional)                  # Streamlit application to interact with the assistant
```

All the instructions described below must be followed by relying on this already prepared structure, which you will gradually enrich to result in a functional assistant.

### The LLM (`src/core/llm.py`)

The heart of the assistant rests on the language model (LLM), which is responsible for generating and interpreting responses. This file's role is to configure and initialize the chosen model, as well as to provide a fallback solution in case of problems.

The implementation must include:

- **A main model**: this is the default model used for all requests (for example a Groq LLaMA 70B model).
- **API key retrieval**: sensitive identifiers and parameters must be stored in the `.env` file and retrieved in the code via environment variables.

This abstraction layer allows strictly separating business logic (chains, prompts, parsers) from the model configuration. Thus, it is easy to change providers or models without having to modify the entire project.

### The Prompts (src/prompts/prompts.py)

Prompts play a central role in the architecture, as they define how the model should reason and formulate its responses. They serve as clear and binding instructions to the LLM to ensure that the outputs are usable.

In this exam, you must **set up different prompts** corresponding to the expected functionalities of the assistant:

- **Code analysis prompt**: Asks the LLM to evaluate a piece of Python code and determine if it is optimal. The model must identify possible problems (readability, performance, missing best practices) and propose improvements.
- **Unit test generation prompt**: From a given Python function, the assistant must produce a unit test in pytest. The instruction must force the model to respond with structured content, in order to be able to extract the test code automatically.
- **Test explanation prompt**: Educational and detailed explanation of a unit test. The assistant must behave like a teacher and make the test understandable for a student or a beginner developer.
- **Free conversation prompt**: Natural discussion with the user. This prompt must be designed to function with conversational memory, by integrating the history of exchanges in order to give continuity to the dialogue.

Each prompt must be built so as to always produce a valid JSON response, in order to be interpretable by the parsers.

> ⚠️ **Attention**: be sure to properly integrate the placeholder variables (**`{input}`**, **`{format_instructions}`**, etc.) so that the model receives the right information. For the chat with memory, the use of **`MessagesPlaceholder`** is mandatory to correctly transmit the conversation history to the LLM.

### The Parsers (`src/core/parsers.py`)

Parsers constitute an essential step of the project: they allow converting the raw responses of the model into structured and usable objects. As the LLM returns text, it is essential to transform these outputs into clear formats (for example JSON) to be able to manipulate them in the API and memory.

Each functionality of the assistant is associated with a dedicated parser:

- **Code analysis parser**: Transform the model's response into an object containing three key pieces of information:
    - optimal code or not
    - a list of detected problems
    - a list of improvement suggestions
- **Test generation parser**: Extract from the raw text only the part corresponding to the unit test code in pytest, in a usable and directly executable form.
- **Test explanation parser**: Convert the model's output into a clear and educational explanation, in the form of structured text.

These parsers must be built with Pydantic, which ensures:

- Strict validation of the expected format.
- Easy serialization into dictionaries (`.dict()`) for return in endpoints.
- Increased robustness against model formatting errors.

### The Chains (`src/core/chains.py`)

LangChain chains constitute the logical heart of the assistant: they orchestrate the flow of information between prompts, the language model, and parsers. Each functionality relies on a dedicated chain, which clearly defines how the LLM should be solicited and how its output should be used.

You must set up several chains:

- **Code analysis chain**: Uses the analysis prompt, sends the request to the LLM, then parses the response to obtain a structured object containing the evaluation (optimality, problems, suggestions).
- **Unit test generation chain**: Takes a Python function as input and returns a unit test in pytest format.
- **Test explanation chain**: Transforms a Python test into a clear and educational explanation intended for a human user.
- **Free chat chain**: Allows free conversation. Unlike the other chains, it does not pass through a parser but must integrate memory to ensure continuity in exchanges.

Each chain must be built in a simple and modular way, so that the API can invoke them directly without additional logic.

### Memory (`src/memory/memory.py`)

Memory must be implemented to manage multiple users in parallel. The idea is to have a global store that associates each **session_id** with a history of type `InMemoryChatMessageHistory`.

Two main functions must be coded:

- **`get_session_history(session_id)`**: Returns the session history for a given user. If no session exists yet for this user, a new history instance must be created automatically.
- **`get_user_history(session_id)`**: Allows retrieving the entire user history as a list of dictionaries, with the role (human or ai) and the content for each message.

> ⚠️ Important points to respect:
>
> - The session_id must be unique per user (example: the username returned by the JWT).
> - The memory is non-persistent: it will be reset if the application is restarted.
> - This system must be used in particular in the chat chain, with `RunnableWithMessageHistory`, to ensure the continuity of conversations.

### The APIs (`src/api/`)

The exam relies on two distinct APIs, both developed with FastAPI and executed in separate containers:

#### The Authentication API (`src/api/authentification/`)

This API is dedicated to security and user management. It must allow:

- **Signup**: create a new user and save them in a database (here simulated by an internal structure).
- **Login**: verify credentials allowing access to other services.

Each endpoint must be protected and return clear errors in case of problems (existing user, incorrect credentials). The service has its own Dockerfile and specific dependencies.

#### The Main API (`src/api/assistant/`)

This API constitutes the heart of the assistant. It must expose several endpoints allowing interaction with the LangChain chains defined in `src/core/`. The expected functionalities are:

- **Analyze Python code (`/analyze`)**: Invokes the analysis chain and returns the code evaluation.
- **Generate a unit test (`/generate_test`)**: Calls the generation chain to produce a pytest test.
- **Explain a test (`/explain_test`)**: Uses the explanation chain to provide an educational version.
- **Execute the full pipeline (`/full_pipeline`)**: This endpoint combines several steps into a single request. The submitted code is first analyzed by the analysis chain.
    - If the analysis result indicates that the **code is non-optimal**, the pipeline stops immediately and the API returns only the code evaluation with the list of detected problems and improvement suggestions.
    - On the other hand, if the analysis concludes that the **code is optimal**, then the pipeline automatically continues the following steps: generation of a unit test then educational explanation of the test.

- **Conversational chat (`/chat`)**: Allows free discussion with memory, using `RunnableWithMessageHistory`.
- **History (`/history`)**: Returns all exchanges for a user.

> ⚠️ ***ATTENTION POINTS*** ⚠️
>
> - The results of the endpoints **`/analyze`**, **`/generate_test`**, **`/explain_test`** and **`/full_pipeline`** must be **recorded in the memory associated with the user**, so that each interaction is kept in their history.
> - The two APIs must run in **distinct containers (auth_service and main_service)**.
> - **The main API depends on the authentication API** to verify user identity.
> - Rigorous error management is essential: all exceptions must be captured and transformed into explicit HTTP responses.

### Tracking and Monitoring with LangSmith

To improve traceability and monitoring of the assistant, it is necessary to integrate LangSmith, the monitoring and debug platform for LangChain.

- Trace all requests sent to the LLM, with their prompt and their response.
- Visualize chains and their steps (prompts, parsers, memory) in a graphic interface.
- Debug more easily in case of format problems or model errors.
- Compare multiple versions of prompts or chains in order to optimize assistant performance.

To activate LangSmith, you must configure your environment variables in the `.env` file.

### Streamlit Interface

In addition to the APIs, you can propose a user interface developed with Streamlit. It makes the assistant much more accessible and pleasant to test, by offering direct interaction without going through manual API requests.

**Expected functionalities**

- Authentication and Login
- **Analysis**: Enter a Python code snippet and display the LLM's diagnostic.
- **Test generation**: Provide a Python function and automatically obtain a unit test in pytest.
- **Test explanation**: Paste a unit test and receive a detailed and educational explanation.
- **Full pipeline**: Execute analysis → generation → explanation in one go.
- **Free chat**: Discuss with the assistant naturally, using conversational memory.
- **History**: Visualize all interactions of the current session.

### Deployment with Docker and Makefile

The entire project must be fully containerized to ensure simple, reproducible setup independent of the development environment.

**Expected services**

- **auth**: the authentication API, responsible for user management
- **main**: the main API, which exposes LangChain functionalities (analysis, test generation, explanation, pipeline, chat, history).
- **streamlit**: the user interface, allowing easy testing of the assistant via a graphical interface.

Each service has its own **Dockerfile** and a specific **requirements.txt** file.

**Makefile**

The Makefile must centralize all commands useful for the project. The full deployment of the project must require only one command:

```bash
make
```

> ⚠️ ATTENTION POINTS ⚠️
>
> - Ports must be clearly exposed and documented in the README.
> - Make sure all sensitive variables (API keys, LangSmith configuration, etc.) are properly stored in the `.env` file and loaded by **docker-compose**.

### README.md

Your project must strictly contain a clear and structured **README.md** file.
This document must explain the global functioning of your assistant, as well as how to deploy and test it.

- Steps to configure `.env`.
- Main Makefile commands (make up, make down, make logs).
- List of available endpoints and ports (auth API and assistant API).

**Tests**

Instructions to verify that the API works correctly (test scenarios to perform):

- signup
- login
- analysis
- test generation
- explanation
- full pipeline
- chat with memory
- history display


## Reminders and Tips

Before starting, keep the following points in mind:

- **Organization**: Scrupulously respect the provided project structure. Each file has a precise role (LLM, prompts, parsers, memory, API, etc.). Good organization will facilitate the correction and reading of your code.
- **Environment variables**: Never put your keys in clear text in the code. Store them in the `.env` file.
- **Prompts**: Always make sure to use placeholders (**`{input}`**, **`{format_instructions}`**, etc.) and, for the chat, the **MessagesPlaceholder** in order to properly manage the exchange history.
- **Parsers**: Always impose a return in JSON format. This ensures that your endpoints will return structured and usable objects.
- **Memory**: Use a unique `session_id` to avoid mixing histories. Don't forget that memory is in RAM and disappears if you restart your services.
- The authentication API must be separated from the main API.
- **Docker**: Only put what is necessary in your Dockerfiles. Copy only useful files and expose the right ports.
- **README**: This file must be written as if a corrector had no prior knowledge of your project. Clearly indicate how to launch services, and how to test each endpoint.
- **Tests**: take the time to test all functionalities (auth, analysis, generation, explanation, pipeline, chat, history). Do not wait for the end to check: test as you go.

> ⚠️ TIP ⚠️
>
> - Create a `uv` virtual environment before starting to containerize your project.
> - As soon as you set up a new chain, immediately create its corresponding endpoint and test it to verify its proper functioning.

## Deliverables

Don't forget to upload your exam in the format of a zip or tar archive, in the **My Exams** tab, after validating all the module exercises.

> ⚠️ **IMPORTANT** ⚠️ : Do not send your virtual environment (e.g. .venv or uv) in your submission. In case of non-compliance with this instruction, an **automatic retake** of the exam will be assigned to you.

Congratulations, if you have reached this point, you have finished the module on LangChain and LLM Experimentation! 🎉.
