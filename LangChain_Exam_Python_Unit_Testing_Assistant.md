![](https://assets-datascientest.s3-eu-west-1.amazonaws.com/de/logo_datascientest.png)  

---

 

# LangChain Exam: Python Unit Testing Assistant

 

---

 

## General Instructions

 

The exam aims to develop an intelligent assistant capable of analyzing Python code, automatically generating unit tests with pytest, and explaining these tests in an educational manner.

 

To achieve this, you will need to set up a complete architecture combining several tools:

 
- **LangChain** to manage chains, prompts, parsers, and memory.
- **FastAPI** to expose functionalities through a secure API.
- **Docker** with a **Makefile** to containerize and orchestrate the entire project.
- A user interface with **Streamlit** can be added as a complement, but it remains OPTIONAL.
 

To complete this exam, a [GitHub repository](https://github.com/DataScientest/exam_Langchain) is provided for you. The first step is to clone this repository onto your machine to have the entire expected project structure (folders, configuration files, Makefile, etc.).

 

This repository serves as a skeleton: it provides you with the basic architecture that you will need to complete by implementing the various components (LangChain chains, parsers, memory, API, containerization).

 

```txt
exam_Langchain/                      
├── .env                             # Environment variables (GROQ + LangSmith API keys)
├── .python-version                  # Python version used (here 3.13)
├── pyproject.toml                   # Dependency management and project configuration
├── Makefile                         # Commands to build/up/down the containers
├── docker-compose.yml               # Orchestration of services (auth, main, streamlit)
├── README.md                        # Main documentation of the project
└── src/                             # Source code of the project
    ├── api/                         # Folder grouping API services
    │   ├── authentication/          # Authentication service 
    │   │   ├── Dockerfile.auth      
    │   │   ├── requirements.txt     
    │   │   └── auth.py              # FastAPI code to handle signup, login, me
    │   └── assistant/               # Main service of the LangChain assistant
    │       ├── Dockerfile.main      
    │       ├── requirements.txt     
    │       └── main.py              # FastAPI code for analysis/generation/tests/chat
    ├── core/                        # Core components of LangChain
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

 

The set of instructions described below must be followed by relying on this pre-prepared structure, which you will gradually enrich to achieve a functional assistant.

 

### The LLM (`src/core/llm.py`)

 

The heart of the assistant relies on the language model (LLM), which is responsible for generating and interpreting responses. This file is intended to configure and initialize the chosen model, as well as to provide a fallback solution in case of issues.

 

The implementation must include:

 
- **A main model**: this is the default model used for all requests (for example, a Groq LLaMA 70B model).
- **An API key retrieval**: sensitive identifiers and parameters should be stored in the `.env` file and retrieved in the code via environment variables.
 

This layer of abstraction clearly separates the business logic (strings, prompts, parsers) from the model configuration. Thus, it is easy to switch providers or models without having to modify the entire project.

 

### The Prompts (src/prompts/prompts.py)

 

Prompts play a central role in the architecture, as they define how the model should reason and formulate its responses. They serve as clear and binding instructions to the LLM to ensure that the outputs are actionable.

 

In this exam, you must **set up different prompts** corresponding to the expected functionalities of the assistant:

 
- **Code Analysis Prompt**: Ask the LLM to evaluate a snippet of Python code and determine if it is optimal. The model should identify potential issues (readability, performance, missing best practices) and suggest improvements.
- **Unit Test Generation Prompt**: Based on a given Python function, the assistant should produce a unit test in pytest. The instruction should require the model to respond with structured content, so that the test code can be extracted automatically.
- **Test Explanation Prompt**: A detailed and educational explanation of a unit test. The assistant should act like a teacher and make the test understandable for a student or a beginner developer.
- **Free Conversation Prompt**: Natural discussion with the user. This prompt should be designed to work with conversational memory, integrating the history of exchanges to provide continuity in the dialogue.
 

Each prompt must be constructed in such a way as to always produce a valid JSON response, so that it can be interpreted by parsers.

 

> ⚠️ **Attention**: make sure to properly integrate the placeholder variables (**`{input}`**, **`{format_instructions}`**, etc.) so that the model receives the correct information. For the chat with memory, the use of **`MessagesPlaceholder`** is mandatory to correctly transmit the conversation history to the LLM.

 

### The Parsers (`src/core/parsers.py`)

 

Parsers are a crucial step in the project: they allow converting the raw responses from the model into structured and usable objects. Since the LLM returns text, it is essential to transform these outputs into clear formats (for example, JSON) so that they can be manipulated within the API and memory.

 

Each feature of the assistant is associated with a dedicated parser:

 
- **Code Analysis Parser**: Transform the model's response into an object containing three key pieces of information:   
 
- whether the code is optimal or not
- a list of detected issues
- a list of improvement suggestions
- **Test Generation Parser**: Extract from plain text only the part corresponding to the unit test code in pytest, in a usable and directly executable form.
- **Test Explanation Parser**: Convert the model's output into a clear and educational explanation, in the form of structured text.
 

These parsers must be built with Pydantic, which ensures:

 
- Strict validation of the expected format.
- Easy serialization into dictionaries (`.dict()`) for returning in endpoints.
- Increased robustness against model format errors.
 

### The Chains (`src/core/chains.py`)

 

The LangChain chains are the logical core of the assistant: they orchestrate the flow of information between the prompts, the language model, and the parsers. Each feature relies on a dedicated chain, which clearly defines how the LLM should be solicited and how its output should be utilized.

 

You need to set up several chains:

 
- **Code Analysis Chain**: Uses the analysis prompt, sends the request to the LLM, then parses the response to obtain a structured object containing the evaluation (optimality, issues, suggestions).
- **Unit Test Generation Chain**: Takes a Python function as input and returns a unit test in pytest format.
- **Test Explanation Chain**: Transforms a Python test into a clear and educational explanation intended for a human user.
- **Free Chat Chain**: Allows for open conversation. Unlike the other chains, it does not go through a parser but must integrate memory to ensure continuity in exchanges.
 

Each chain should be built simply and modularly, so that the API can invoke them directly without additional logic.

 

### Memory (`src/memory/memory.py`)

 

The memory must be implemented to handle multiple users in parallel. The idea is to have a global store that associates each **session_id** with a history of type `InMemoryChatMessageHistory`.

 

Two main functions need to be coded:

 
- **`get_session_history(session_id)`** : Returns the session history for a given user. If no session exists yet for this user, a new instance of history must be created automatically.
- **`get_user_history(session_id)`** : Allows retrieving the entire history of the user in the form of a list of dictionaries, with each message containing the role (human or ai) and the content.
 

> ⚠️ Important points to respect:
>  
> - The session_id must be unique per user (for example: the username returned by the JWT).
> - The memory is non-persistent: it will be reset if the application is restarted.
> - This system should be used particularly in the chat chain, with `RunnableWithMessageHistory`, to ensure the continuity of conversations.

 

### The APIs (`src/api/`)

 

The exam is based on two distinct APIs, both developed with FastAPI and running in separate containers:

 

#### The authentication API (`src/api/authentification/`)

 

This API is dedicated to the management of security and users. It must allow:

 
- **Signup**: create a new user and register them in a database (here simulated by an internal structure).
- **Login**: verify the credentials that allow access to other services.
 

Each endpoint must be protected and return clear errors in case of issues (existing user, incorrect credentials). The service has its own Dockerfile and specific dependencies.

 

#### The main API (`src/api/assistant/`)

 

This API is the core of the assistant. It must expose several endpoints to interact with the LangChain chains defined in `src/core/`. The expected functionalities are:

 
- **Analyze Python code (`/analyze`)**: Invokes the analysis chain and returns the evaluation of the code.
- **Generate a unit test (`/generate_test`)**: Calls the generation chain to produce a test in pytest.
- **Explain a test (`/explain_test`)**: Uses the explanation chain to provide an educational version.
- **Execute the full pipeline (`/full_pipeline`)**: This endpoint combines several steps into a single request. The submitted code is first analyzed by the analysis chain.

 
- If the analysis result indicates that the **code is suboptimal**, the pipeline stops immediately and the API returns only the evaluation of the code with the list of detected issues and suggestions for improvement.
- Conversely, if the analysis concludes that the **code is optimal**, then the pipeline automatically proceeds to the following steps: generating a unit test and then providing an educational explanation of the test.
- **Conversational chat (`/chat`)**: Allows free discussion with memory, using `RunnableWithMessageHistory`.
- **History (`/history`)**: Returns all exchanges for a user.
 

> ⚠️ ***POINTS TO CONSIDER*** ⚠️
>  
> - The results of the endpoints **`/analyze`**, **`/generate_test`**, **`/explain_test`** and **`/full_pipeline`** must be **stored in the memory associated with the user**, so that each interaction is kept in their history.
> - The two APIs must run in **separate containers (auth_service and main_service)**.
> - **The main API depends on the authentication API** to verify the identity of users.
> - A rigorous error management is essential: all exceptions must be caught and transformed into explicit HTTP responses.

 

### Tracking and Monitoring with LangSmith

 

To improve the traceability and monitoring of the assistant, it is necessary to integrate LangSmith, the monitoring and debugging platform for LangChain.

 
- Trace all requests sent to the LLM, including their prompt and response.
- Visualize chains and their steps (prompts, parsers, memory) in a graphical interface.
- Debug more easily in case of format issues or model errors.
- Compare multiple versions of prompts or chains to optimize the assistant's performance.
 

To activate LangSmith, you need to configure your environment variables in the `.env` file.

 

### Streamlit Interface

 

In addition to the APIs, you can offer a user interface developed with Streamlit. It makes the assistant much more accessible and pleasant to test, providing direct interaction without going through manual API requests.

 

**Expected Features**

 
- Authentication and Login
- **Analysis**: Enter a snippet of Python code and display the LLM's diagnosis
- **Test Generation**: Provide a Python function and automatically obtain a unit test in pytest.
- **Test Explanation**: Paste a unit test and receive a detailed and educational explanation.
- **Complete Pipeline**: Execute the analysis → generation → explanation all at once.
- **Free Chat**: Chat with the assistant naturally, using conversational memory.
- **History**: View all interactions from the current session.
 

### Deployment with Docker and Makefile

 

The entire project must be fully containerized to ensure a simple, reproducible, and environment-independent setup.

 

**Expected Services**

 
- **auth**: the authentication API, responsible for user management
- **main**: the main API, which exposes the functionalities of LangChain (analysis, test generation, explanation, pipeline, chat, history)
- **streamlit**: the user interface, allowing easy testing of the assistant through a graphical interface.
 

Each service has its own **Dockerfile** and a specific **requirements.txt** file.

 

**Makefile**

 

The Makefile must centralize all the useful commands for the project. The complete deployment of the project should only require a single command:

 

```bash
make
```

 

> ⚠️ POINTS TO CONSIDER ⚠️
>  
> - Ports must be clearly exposed and documented in the README.
> - Ensure that all sensitive variables (API keys, LangSmith configuration, etc.) are properly stored in the `.env` file and loaded by **docker-compose**.

 

### README.md

 

Your project must necessarily include a clear and structured **README.md** file. This document should explain the overall functioning of your assistant, as well as how to deploy and test it.

 
- Steps to configure the `.env` file.
- Main commands of the Makefile (make up, make down, make logs).
- List of available endpoints and ports (auth API and assistant API).
 

**Tests**

 

Instructions to verify that the API is functioning correctly (test scenarios to perform):

 
- Registration
- Login
- Analysis
- Test Generation
- Explanation
- Complete Pipeline
- Chat with Memory
- Display History
 

## Reminders and Tips

 

Before we begin, keep the following points in mind:

 
- **Organization**: Strictly adhere to the provided project structure. Each file has a specific role (LLM, prompts, parsers, memory, API, etc.). Good organization will facilitate debugging and reading your code.
- **Environment Variables**: Never hardcode your keys in the code. Store them in the `.env` file.
- **Prompts**: Always ensure to use placeholders (**`{input}`**, **`{format_instructions}`**, etc.) and, for chat, the **MessagesPlaceholder** to properly manage the history of exchanges.
- **Parsers**: Always enforce a return in JSON format. This ensures that your endpoints will return structured and usable objects.
- **Memory**: Use a unique `session_id` to avoid mixing histories. Remember that memory is in RAM and disappears if you restart your services.
- The authentication API must be separate from the main API.
- **Docker**: Only include what is necessary in your Dockerfiles. Copy only the useful files and expose the correct ports.
- **README**: This file should be written as if a reviewer has no prior knowledge of your project. Clearly indicate how to launch the services and how to test each endpoint.
- **Tests**: Take the time to test all functionalities (auth, analysis, generation, explanation, pipeline, chat, history). Don’t wait until the end to check: test as you go.
 

> ⚠️ TIP ⚠️
>  
> - Create a virtual environment `uv` before you start containerizing your project.
> - As soon as you set up a new chain, immediately create its corresponding endpoint and test it to ensure it works correctly.

 

## Outputs

 

Don't forget to upload your exam in the format of a zip or tar archive, in the **My Exams** tab, after you have completed all the exercises of the module.

 

> ⚠️ **IMPORTANT** ⚠️: Do not send your virtual environment (e.g. .venv or uv) in your submission. If you fail to comply with this instruction, an **automatic repass** of the exam will be assigned to you.

 

Congratulations! If you have reached this point, you have completed the module on LangChain and LLM Experimentation! 🎉.
