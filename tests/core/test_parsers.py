from src.core.parsers import CodeAnalysis, TestGeneration, TestExplanation

def test_code_analysis_parser_validation():
    # Valid data
    data = {
        "is_optimal": True,
        "issues": [],
        "suggestions": ["Great job!"]
    }
    model = CodeAnalysis(**data)
    assert model.is_optimal is True
    assert model.issues == []
    assert model.suggestions == ["Great job!"]

def test_test_generation_parser_validation():
    data = {"test_code": "def test_foo(): pass"}
    model = TestGeneration(**data)
    assert model.test_code == "def test_foo(): pass"

def test_test_explanation_parser_validation():
    data = {"explanation": "This is a test."}
    model = TestExplanation(**data)
    assert model.explanation == "This is a test."
