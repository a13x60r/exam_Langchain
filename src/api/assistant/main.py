from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Any
import requests
import os

from src.core.chains import analysis_chain, test_generation_chain, explanation_chain, chat_chain
from src.memory.memory import get_user_history

app = FastAPI(title="LangChain Assistant API")

# Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")

# --- Dependencies ---
async def verify_token(authorization: str = Header(...)):
    """
    Verifies the token with the auth service.
    Returns the username if valid.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
        
    token = authorization.split(" ")[1]
    
    # Call auth service to verify
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/me", params={"token": token})
        if response.status_code != 200:
             raise HTTPException(status_code=401, detail="Invalid token")
        return response.json()["username"]
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")

# --- Models ---
class CodeInput(BaseModel):
    code: str

class TestExecutionOutput(BaseModel):
    test_code: str
    explanation: Optional[str] = None

class AnalysisOutput(BaseModel):
    is_optimal: bool
    issues: List[str]
    suggestions: List[str]

class ChatInput(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# --- Endpoints ---

@app.post("/analyze", response_model=AnalysisOutput)
async def analyze_code(input: CodeInput, username: str = Depends(verify_token)):
    try:
        result = analysis_chain.invoke({"code": input.code})
        # Format for response
        return AnalysisOutput(
            is_optimal=result.is_optimal,
            issues=result.issues,
            suggestions=result.suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_test")
async def generate_test(input: CodeInput, username: str = Depends(verify_token)):
    try:
        result = test_generation_chain.invoke({"code": input.code})
        return {"test_code": result.test_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain_test")
async def explain_test(input: TestExecutionOutput, username: str = Depends(verify_token)):
    try:
        result = explanation_chain.invoke({"test_code": input.test_code})
        return {"explanation": result.explanation}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/full_pipeline")
async def full_pipeline(input: CodeInput, username: str = Depends(verify_token)):
    try:
        # Step 1: Analyze
        analysis = analysis_chain.invoke({"code": input.code})
        
        response = {
            "analysis": {
                "is_optimal": analysis.is_optimal,
                "issues": analysis.issues,
                "suggestions": analysis.suggestions
            }
        }
        
        if not analysis.is_optimal:
            return response
            
        # Step 2: Generate Test
        test_gen = test_generation_chain.invoke({"code": input.code})
        response["test_code"] = test_gen.test_code
        
        # Step 3: Explain Test
        explanation = explanation_chain.invoke({"test_code": test_gen.test_code})
        response["explanation"] = explanation.explanation
        
        return response
        
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(input: ChatInput, username: str = Depends(verify_token)):
    try:
        # Using session_id = username for this exam
        config = {"configurable": {"session_id": username}}
        
        response = chat_chain.invoke(
            {"input": input.message},
            config=config
        )
        return ChatResponse(response=response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(username: str = Depends(verify_token)):
    return get_user_history(username)
