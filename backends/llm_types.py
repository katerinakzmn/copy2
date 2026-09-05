"""Shared data structures for real LLM calls and token-based accounting."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional


@dataclass
class LLMCallResult:
    """Normalized result of one developer or reviewer LLM request."""

    text: str = ""
    code: str = ""
    model: str = ""
    role: str = "developer"
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_seconds: float = 0.0
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def succeeded(self) -> bool:
        return self.error_type is None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _number(value: Any) -> float:
    return float(value or 0)


def calculate_cost_usd(usage: Mapping[str, Any], pricing: Mapping[str, Any]) -> float:
    """Calculate USD cost from token counts and USD-per-million-token prices."""
    input_tokens = _number(usage.get("input_tokens"))
    cached_input_tokens = _number(usage.get("cached_input_tokens"))
    output_tokens = _number(usage.get("output_tokens"))

    input_price = _number(pricing.get("input_per_million_usd"))
    cached_price = _number(pricing.get("cached_input_per_million_usd"))
    output_price = _number(pricing.get("output_per_million_usd"))

    return round(
        (input_tokens * input_price + cached_input_tokens * cached_price + output_tokens * output_price)
        / 1_000_000,
        8,
    )


def pricing_for_model(pricing_config: Mapping[str, Any], model: str) -> Mapping[str, Any]:
    """Return an exact-model price record, or an empty mapping if it is absent."""
    return pricing_config.get("models", {}).get(model, {})
