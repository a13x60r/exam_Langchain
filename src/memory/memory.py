from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Global store for session histories
# Key: session_id, Value: InMemoryChatMessageHistory
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Returns the chat history object for a given session ID.
    If it doesn't exist, a new one is created.
    """
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def get_user_history(session_id: str) -> list:
    """
    Retrieves the raw history for a user as a list of dicts.
    """
    history = get_session_history(session_id)
    return [
        {"role": msg.type, "content": msg.content} 
        for msg in history.messages
    ]
