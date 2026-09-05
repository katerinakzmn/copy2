from backends.llm_types import LLMCallResult, calculate_cost_usd, pricing_for_model


def test_calculate_cost_usd_uses_all_token_categories():
    usage = {"input_tokens": 1_000_000, "cached_input_tokens": 1_000_000, "output_tokens": 1_000_000}
    pricing = {
        "input_per_million_usd": 2.0,
        "cached_input_per_million_usd": 0.5,
        "output_per_million_usd": 8.0,
    }
    assert calculate_cost_usd(usage, pricing) == 10.5


def test_call_result_serializes_without_credentials():
    result = LLMCallResult(code="def f():\n    return 1\n", model="model-id", input_tokens=10)
    data = result.to_dict()
    assert data["model"] == "model-id"
    assert data["input_tokens"] == 10
    assert "api_key" not in data


def test_pricing_for_model_returns_empty_mapping_for_unknown_model():
    assert pricing_for_model({"models": {}}, "missing") == {}
