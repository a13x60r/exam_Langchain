from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from src.core.llm import get_llm
from src.prompts.prompts import analysis_prompt, test_generation_prompt, explanation_prompt, chat_prompt
from src.core.parsers import analysis_parser, test_generation_parser, explanation_parser
from src.memory.memory import get_session_history
from langchain_core.runnables.history import RunnableWithMessageHistory

llm = get_llm()

# 1. Code Analysis Chain
analysis_chain = (
    analysis_prompt 
    | llm 
    | analysis_parser
)

# 2. Test Generation Chain
test_generation_chain = (
    test_generation_prompt 
    | llm 
    | test_generation_parser
)

# 3. Test Explanation Chain
explanation_chain = (
    explanation_prompt 
    | llm 
    | explanation_parser
)

# 4. Chat Chain with History
chat_chain = RunnableWithMessageHistory(
    chat_prompt | llm,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)
