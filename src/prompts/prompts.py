from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder

# 1. Code Analysis Prompt
# 1. Code Analysis Prompt
analysis_prompt = PromptTemplate(
    input_variables=["code", "format_instructions"],
    template="""You are an expert Python developer. Analyze the following code for optimality, readability, and best practices.

{code}

{format_instructions}

IMPORTANT: Receive the code, analyze it internally, but output ONLY the JSON object matching the schema. Do not output any markdown code blocks (like ```json), no headers, and no conversational text. just the raw JSON string.
"""
)

# 2. Test Generation Prompt
test_generation_prompt = PromptTemplate(
    input_variables=["code", "format_instructions"],
    template="""You are an expert QA engineer. Generate a comprehensive pytest unit test for the following function:

{code}

Ensure the test covers edge cases and normal execution.

{format_instructions}

IMPORTANT: Output ONLY the JSON object matching the schema. Do not output any markdown code blocks, no headers, and no conversational text.
"""
)

# 3. Test Explanation Prompt
explanation_prompt = PromptTemplate(
    input_variables=["test_code", "format_instructions"],
    template="""You are a coding instructor. Explain the following pytest code to a beginner:

{test_code}

Break it down step by step essentially teaching what the test does.

{format_instructions}

IMPORTANT: Output ONLY the JSON object. Do not output any markdown code blocks, no headers, and no conversational text.
"""
)

# 4. Chat Prompt with Memory
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant for Python developers."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
