from dataclasses import dataclass

import pytest
from lab01_agent_memory.inference import (
    InferenceSettings,
    ModelResponse,
    run_token_comparison,
)


@dataclass
class FakeInferenceClient:
    responses: list[ModelResponse]
    prompts: list[str]

    def chat(self, prompt: str, settings: InferenceSettings) -> ModelResponse:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def _response(
    prompt_tokens: int,
    text: str = "Use idempotency and original request identifier.",
) -> ModelResponse:
    return ModelResponse(
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=12,
        total_tokens=prompt_tokens + 12,
        finish_reason="COMPLETE",
    )


def _settings() -> InferenceSettings:
    return InferenceSettings("workshop-compartment", "approved-chat-model", 120)


def test_real_comparison_uses_same_question_and_only_retrieved_memory() -> None:
    client = FakeInferenceClient([_response(80), _response(45)], [])

    comparison = run_token_comparison(
        client,
        _settings(),
        question="How do we process a repeated payment request?",
        baseline_decisions=[
            (
                "payment-idempotency",
                "Use idempotency and preserve the original request identifier.",
            ),
            ("contract-compatibility", "Preserve backward compatibility."),
        ],
        retrieved_decisions=[
            (
                "payment-idempotency",
                "Use idempotency and preserve the original request identifier.",
            ),
        ],
        required_terms=("idempotency", "original request identifier"),
    )

    assert len(client.prompts) == 2
    assert "contract-compatibility" in client.prompts[0]
    assert "contract-compatibility" not in client.prompts[1]
    assert "How do we process a repeated payment request?" in client.prompts[0]
    assert "How do we process a repeated payment request?" in client.prompts[1]
    assert comparison["input_token_reduction"] == 35
    assert comparison["both_quality_checks_passed"] is True


def test_real_comparison_rejects_missing_usage() -> None:
    client = FakeInferenceClient(
        [
            ModelResponse("idempotency original request identifier", None, 12, 12, "COMPLETE"),
            _response(45),
        ],
        [],
    )

    with pytest.raises(RuntimeError, match="prompt_tokens"):
        run_token_comparison(
            client,
            _settings(),
            question="Question",
            baseline_decisions=[("id", "idempotency original request identifier")],
            retrieved_decisions=[("id", "idempotency original request identifier")],
            required_terms=("idempotency",),
        )


def test_real_comparison_rejects_incomplete_or_low_quality_response() -> None:
    incomplete = FakeInferenceClient([_response(80), _response(45)], [])
    incomplete.responses[0] = ModelResponse("idempotency", 80, 12, 92, "MAX_TOKENS")

    with pytest.raises(RuntimeError, match="not complete"):
        run_token_comparison(
            incomplete,
            _settings(),
            question="Question",
            baseline_decisions=[("id", "idempotency original request identifier")],
            retrieved_decisions=[("id", "idempotency original request identifier")],
            required_terms=("idempotency",),
        )

    low_quality = FakeInferenceClient([_response(80, "idempotency"), _response(45)], [])
    with pytest.raises(RuntimeError, match="criteria"):
        run_token_comparison(
            low_quality,
            _settings(),
            question="Question",
            baseline_decisions=[("id", "idempotency original request identifier")],
            retrieved_decisions=[("id", "idempotency original request identifier")],
            required_terms=("idempotency", "original request identifier"),
        )


def test_real_comparison_rejects_when_memory_does_not_reduce_provider_tokens() -> None:
    client = FakeInferenceClient([_response(45), _response(45)], [])

    with pytest.raises(RuntimeError, match="did not reduce"):
        run_token_comparison(
            client,
            _settings(),
            question="Question",
            baseline_decisions=[("id", "idempotency original request identifier")],
            retrieved_decisions=[("id", "idempotency original request identifier")],
            required_terms=("idempotency",),
        )
