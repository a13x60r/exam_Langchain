from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# 1. Code Analysis Parser
class CodeAnalysis(BaseModel):
    is_optimal: bool = Field(description="Whether the code is optimal or not")
    issues: List[str] = Field(description="List of issues found in the code")
    suggestions: List[str] = Field(description="List of suggestions for improvement")

analysis_parser = PydanticOutputParser(pydantic_object=CodeAnalysis)

# 2. Test Generation Parser
class TestGeneration(BaseModel):
    test_code: str = Field(description="The complete python code for the pytest unit test")

test_generation_parser = PydanticOutputParser(pydantic_object=TestGeneration)

# 3. Test Explanation Parser
class TestExplanation(BaseModel):
    explanation: str = Field(description="The detailed educational explanation of the test")

explanation_parser = PydanticOutputParser(pydantic_object=TestExplanation)
