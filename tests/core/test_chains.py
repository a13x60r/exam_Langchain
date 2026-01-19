from unittest.mock import MagicMock, patch
import pytest
from src.core.parsers import CodeAnalysis

import src.core.chains as chains_module

# Mock the LLM output for analysis chain
@pytest.fixture
def mock_llm_response_analysis():
    return CodeAnalysis(
        is_optimal=False,
        issues=["Syntax error"],
        suggestions=["Fix syntax"]
    )

def test_analysis_chain_structure(mock_llm_response_analysis):
    # Use patch.object on the imported module to avoid AttributeErrors with namespace packages
    with patch.object(chains_module, "llm") as mock_llm:
        from src.core.chains import analysis_chain
        assert analysis_chain is not None
