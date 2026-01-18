from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

# 1. Code Analysis Prompt
analysis_prompt = PromptTemplate(
    input_variables=["code", "format_instructions"],
    template="""You are an expert Python developer. Analyze the following code:

{code}

Check for optimality, readability, and best practices.
You MUST output a valid JSON with the following structure:
{{
    "is_optimal": boolean,
    "issues": [list of strings describing issues found],
    "suggestions": [list of strings describing improvement suggestions]
}}

{format_instructions}
"""
)

# 2. Test Generation Prompt
test_generation_prompt = PromptTemplate(
    input_variables=["code", "format_instructions"],
    template="""You are an expert QA engineer. Generate a comprehensive pytest unit test for the following function:

{code}

Ensure the test covers edge cases and normal execution.
You MUST output a valid JSON with the following structure:
{{
    "test_code": "The complete python code for the test, including imports"
}}

{format_instructions}
"""
)

# 3. Test Explanation Prompt
explanation_prompt = PromptTemplate(
    input_variables=["test_code", "format_instructions"],
    template="""You are a coding instructor. Explain the following pytest code to a beginner:

{test_code}

Break it down step by step essentially teaching what the test does.
You MUST output a valid JSON with the following structure:
{{
    "explanation": "The detailed explanation text"
}}

{format_instructions}
"""
)

# 4. Chat Prompt with Memory
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant for Python developers."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
