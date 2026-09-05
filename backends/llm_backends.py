"""Real and mock-compatible LLM backends for benchmark evaluation.

The OpenAI backend keeps credentials in environment variables and returns a
structured LLMCallResult containing code/text, usage, latency, and token cost.
No API key is stored in this repository.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, Mapping, Optional

from backends.llm_types import LLMCallResult, calculate_cost_usd, pricing_for_model
from tasks import load_tasks

_DEVELOPER_SYSTEM_PROMPT = (
    "You repair Python code. Return only the complete corrected Python code. "
    "Do not use Markdown fences. Do not explain your answer."
)

_REVIEWER_SYSTEM_PROMPT = """You are a routing reviewer for Python bug fixing.
Estimate whether one more attempt by the CURRENT model tier can solve the task,
given the candidate code and test feedback. Return JSON only:
{"confidence": number from 0 to 1,
 "verdict": "retry_current" | "escalate",
 "reason": "at most 12 words"}
Do not return code or Markdown."""


class _TaskLookupMixin:
    def __init__(self) -> None:
        self._tasks = {task.instance_id: task for task in load_tasks()}

    def _developer_prompt(
        self,
        task_id: str,
        previous_code: str = "",
        feedback: str = "",
        attempt: int = 1,
    ) -> str:
        task = self._tasks[task_id]
        code = previous_code or task.original_code
        parts = [
            f"Task: {task.problem_statement}",
            f"Attempt: {attempt}",
            "Code to repair:\n" + code,
        ]
        if feedback:
            parts.append("Test feedback from the previous attempt:\n" + feedback)
        return "\n\n".join(parts)

    def _reviewer_prompt(
        self,
        task_id: str,
        candidate_code: str,
        feedback: str,
        tier: str,
    ) -> str:
        task = self._tasks[task_id]
        return "\n\n".join(
            [
                f"Task: {task.problem_statement}",
                f"Current tier: {tier}",
                "Candidate code:\n" + candidate_code,
                "Test feedback:\n" + (feedback or "No detailed feedback available."),
            ]
        )

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        lines = text.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()

    @classmethod
    def _parse_code(cls, raw: str) -> str:
        raw = (raw or "").strip()
        if not raw:
            return ""
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return str(payload.get("fixed_code") or payload.get("code") or raw)
        except json.JSONDecodeError:
            pass
        return cls._strip_code_fences(raw)

    @staticmethod
    def _parse_review(raw: str) -> Dict[str, Any]:
        fallback = {
            "confidence": 0.0,
            "verdict": "escalate",
            "reason": "Reviewer output was not valid JSON.",
        }
        try:
            payload = json.loads((raw or "").strip())
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw or "", re.DOTALL)
            if not match:
                return fallback
            try:
                payload = json.loads(match.group())
            except json.JSONDecodeError:
                return fallback
        if not isinstance(payload, dict):
            return fallback
        try:
            confidence = min(1.0, max(0.0, float(payload.get("confidence", 0.0))))
        except (TypeError, ValueError):
            confidence = 0.0
        verdict = payload.get("verdict", "escalate")
        if verdict not in {"retry_current", "escalate"}:
            verdict = "escalate"
        return {
            "confidence": confidence,
            "verdict": verdict,
            "reason": str(payload.get("reason", ""))[:240],
        }


class OpenAIBackend(_TaskLookupMixin):
    """OpenAI backend with model IDs supplied only through environment variables."""

    def __init__(
        self,
        pricing_config: Optional[Mapping[str, Any]] = None,
        temperature: float = 0,
        max_output_tokens: int = 600,
        reviewer_max_output_tokens: int = 120,
    ) -> None:
        super().__init__()
        self.models = {
            "weak": os.getenv("OPENAI_WEAK_MODEL", ""),
            "strong": os.getenv("OPENAI_STRONG_MODEL", ""),
            "reviewer": os.getenv("OPENAI_REVIEW_MODEL", ""),
        }
        self.pricing_config = pricing_config or {}
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.reviewer_max_output_tokens = reviewer_max_output_tokens
        self._client = None

    def _client_or_error(self):
        if self._client is not None:
            return self._client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for backend=openai")
        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)
        return self._client

    @staticmethod
    def _usage_dict(response: Any) -> Dict[str, int]:
        usage = getattr(response, "usage", None)
        details = getattr(usage, "prompt_tokens_details", None)
        return {
            "input_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
            "cached_input_tokens": int(getattr(details, "cached_tokens", 0) or 0),
            "output_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
        }

    def _request(self, model: str, system: str, prompt: str, max_tokens: int, role: str) -> LLMCallResult:
        if not model:
            return LLMCallResult(
                model=model,
                role=role,
                error_type="configuration_error",
                error_message=f"No OpenAI model configured for role={role}.",
            )
        started = time.perf_counter()
        try:
            response = self._client_or_error().chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=max_tokens,
            )
            raw = response.choices[0].message.content or ""
            usage = self._usage_dict(response)
            cost = calculate_cost_usd(usage, pricing_for_model(self.pricing_config, model))
            return LLMCallResult(
                text=raw,
                code=self._parse_code(raw) if role == "developer" else "",
                model=model,
                role=role,
                input_tokens=usage["input_tokens"],
                cached_input_tokens=usage["cached_input_tokens"],
                output_tokens=usage["output_tokens"],
                cost_usd=cost,
                latency_seconds=round(time.perf_counter() - started, 4),
            )
        except Exception as exc:
            return LLMCallResult(
                model=model,
                role=role,
                latency_seconds=round(time.perf_counter() - started, 4),
                error_type=type(exc).__name__,
                error_message=str(exc)[:500],
            )

    def generate(
        self,
        task_id: str,
        tier: str,
        previous_code: str = "",
        feedback: str = "",
        attempt: int = 1,
    ) -> LLMCallResult:
        model = self.models.get(tier, "")
        return self._request(
            model=model,
            system=_DEVELOPER_SYSTEM_PROMPT,
            prompt=self._developer_prompt(task_id, previous_code, feedback, attempt),
            max_tokens=self.max_output_tokens,
            role="developer",
        )

    def review(
        self,
        task_id: str,
        candidate_code: str,
        feedback: str,
        tier: str,
    ) -> Dict[str, Any]:
        model = self.models.get("reviewer") or self.models.get("weak", "")
        call = self._request(
            model=model,
            system=_REVIEWER_SYSTEM_PROMPT,
            prompt=self._reviewer_prompt(task_id, candidate_code, feedback, tier),
            max_tokens=self.reviewer_max_output_tokens,
            role="reviewer",
        )
        review = self._parse_review(call.text) if call.succeeded else {
            "confidence": 0.0,
            "verdict": "escalate",
            "reason": call.error_message or "Reviewer request failed.",
        }
        review["call"] = call
        return review


class GeminiBackend(_TaskLookupMixin):
    """Compatibility adapter. It retains the prior lightweight text-only behavior."""

    def __init__(self) -> None:
        super().__init__()
        self.models = {
            "weak": os.getenv("GEMINI_WEAK_MODEL", "gemini-1.5-flash"),
            "strong": os.getenv("GEMINI_STRONG_MODEL", "gemini-1.5-pro"),
        }

    def generate(self, task_id: str, tier: str, prompt: str = "") -> str:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is required for backend=gemini")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.models.get(tier, self.models["weak"]))
        response = model.generate_content(prompt or self._developer_prompt(task_id))
        return self._parse_code(getattr(response, "text", "") or "")


def _strip_code_fences(text: str) -> str:
    return _TaskLookupMixin._strip_code_fences(text)
