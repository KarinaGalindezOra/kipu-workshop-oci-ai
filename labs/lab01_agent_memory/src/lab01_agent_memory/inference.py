"""Real OCI Generative AI token measurement for Lab 1.

The local comparison in :mod:`metrics` remains useful for offline preparation,
but participant evidence uses the usage block returned by OCI Inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol

SYSTEM_INSTRUCTION = (
    "You are an integration engineering assistant. Answer using only the supplied "
    "decision rules. State the applicable decision identifiers, do not invent rules, "
    "and keep the response to no more than 60 tokens."
)


@dataclass(frozen=True)
class InferenceSettings:
    """Non-secret OCI Inference configuration for the Lab 1 comparison."""

    compartment_id: str
    model_id: str
    max_output_tokens: int

    def __post_init__(self) -> None:
        if not self.compartment_id.strip():
            raise ValueError("compartment_id is required")
        if not self.model_id.strip():
            raise ValueError("model_id is required")
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")


@dataclass(frozen=True)
class ModelResponse:
    """The minimum OCI response facts needed for a reproducible comparison."""

    text: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    finish_reason: str | None


class InferenceClient(Protocol):
    """Small testable surface for the OCI chat client."""

    def chat(self, prompt: str, settings: InferenceSettings) -> ModelResponse:
        """Run one non-streaming chat request and return OCI usage facts."""


@dataclass(frozen=True)
class InferenceVariant:
    """Evidence for one prompt design sent to the same model."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    quality_passed: bool
    finish_reason: str

    def as_dict(self) -> dict[str, int | bool | str]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "quality_passed": self.quality_passed,
            "finish_reason": self.finish_reason,
        }


@dataclass(frozen=True)
class ContextExperimentVariant:
    """One deliberately selected context sent to the same inference configuration."""

    variant_id: str
    label: str
    decisions: tuple[tuple[str, str], ...]
    required_terms: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.variant_id.strip():
            raise ValueError("variant_id is required")
        if not self.label.strip():
            raise ValueError("label is required")
        if not self.decisions:
            raise ValueError("An experiment variant requires at least one decision")
        if not self.required_terms:
            raise ValueError("An experiment variant requires quality terms")


def build_prompt(question: str, decisions: list[tuple[str, str]]) -> str:
    """Build an explicit prompt whose only variable is supplied decision context."""

    if not decisions:
        raise ValueError("At least one decision is required for model inference")
    context = "\n".join(f"- [{identifier}] {content}" for identifier, content in decisions)
    return f"Decision rules:\n{context}\n\nQuestion: {question}"


def _required_usage(value: int | None, label: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise RuntimeError(f"OCI Inference did not return a valid {label}")
    return value


def _validate_response(
    response: ModelResponse, required_terms: tuple[str, ...]
) -> tuple[bool, str]:
    if not response.text or not response.text.strip():
        raise RuntimeError("OCI Inference returned an empty response")
    if response.finish_reason != "COMPLETE":
        raise RuntimeError(
            "OCI Inference response was not complete; token evidence cannot be accepted "
            f"(finish_reason={response.finish_reason!r})"
        )
    normalized = response.text.casefold()
    passed = all(term.casefold() in normalized for term in required_terms)
    return passed, response.finish_reason


def _run_variant(
    client: InferenceClient,
    prompt: str,
    settings: InferenceSettings,
    required_terms: tuple[str, ...],
) -> InferenceVariant:
    started = perf_counter()
    response = client.chat(prompt, settings)
    latency_ms = round((perf_counter() - started) * 1000)
    quality_passed, finish_reason = _validate_response(response, required_terms)
    prompt_tokens = _required_usage(response.prompt_tokens, "prompt_tokens")
    completion_tokens = _required_usage(response.completion_tokens, "completion_tokens")
    total_tokens = _required_usage(response.total_tokens, "total_tokens")
    if total_tokens != prompt_tokens + completion_tokens:
        raise RuntimeError("OCI Inference returned inconsistent token usage")
    return InferenceVariant(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        quality_passed=quality_passed,
        finish_reason=finish_reason,
    )


def run_token_comparison(
    client: InferenceClient,
    settings: InferenceSettings,
    *,
    question: str,
    baseline_decisions: list[tuple[str, str]],
    retrieved_decisions: list[tuple[str, str]],
    required_terms: tuple[str, ...],
) -> dict[str, object]:
    """Compare two real OCI calls that differ only in the decision context sent."""

    baseline = _run_variant(
        client,
        build_prompt(question, baseline_decisions),
        settings,
        required_terms,
    )
    memory_optimized = _run_variant(
        client,
        build_prompt(question, retrieved_decisions),
        settings,
        required_terms,
    )
    if not baseline.quality_passed or not memory_optimized.quality_passed:
        raise RuntimeError("A model response did not satisfy the required decision criteria")
    if memory_optimized.prompt_tokens >= baseline.prompt_tokens:
        raise RuntimeError("Retrieved memory did not reduce OCI prompt tokens")
    reduction = baseline.prompt_tokens - memory_optimized.prompt_tokens
    return {
        "measurement_type": "oci_inference_usage",
        "model_id": settings.model_id,
        "max_output_tokens": settings.max_output_tokens,
        "baseline": baseline.as_dict(),
        "memory_optimized": memory_optimized.as_dict(),
        "input_token_reduction": reduction,
        "input_token_reduction_percent": round(reduction * 100 / baseline.prompt_tokens),
        "both_quality_checks_passed": True,
    }


def run_context_experiment(
    client: InferenceClient,
    settings: InferenceSettings,
    *,
    experiment_id: str,
    question: str,
    variants: tuple[ContextExperimentVariant, ...],
) -> dict[str, object]:
    """Measure several intentional context designs through real OCI inference.

    This is an opt-in extension for the workshop. It keeps model and generation
    settings constant, changes only the supplied decisions, and captures OCI
    usage for every variant. A bounded variant count protects participants from
    accidentally turning a learning exercise into an unbounded request loop.
    """

    if not experiment_id.strip():
        raise ValueError("experiment_id is required")
    if not question.strip():
        raise ValueError("question is required")
    if not 2 <= len(variants) <= 8:
        raise ValueError("An experiment must contain between 2 and 8 variants")
    variant_ids = [variant.variant_id for variant in variants]
    if len(set(variant_ids)) != len(variant_ids):
        raise ValueError("Experiment variant_id values must be unique")

    results: list[dict[str, object]] = []
    for variant in variants:
        measured = _run_variant(
            client,
            build_prompt(question, list(variant.decisions)),
            settings,
            variant.required_terms,
        )
        results.append(
            {
                "variant_id": variant.variant_id,
                "label": variant.label,
                "procedure_ids": [identifier for identifier, _ in variant.decisions],
                "procedure_count": len(variant.decisions),
                **measured.as_dict(),
            }
        )

    baseline = results[0]
    lowest_input = min(results, key=lambda result: int(result["prompt_tokens"]))
    all_quality_passed = all(result["quality_passed"] for result in results)
    return {
        "measurement_type": "oci_context_experiment",
        "experiment_id": experiment_id,
        "model_id": settings.model_id,
        "max_output_tokens": settings.max_output_tokens,
        "question": question,
        "variant_count": len(results),
        "variants": results,
        "baseline_variant_id": baseline["variant_id"],
        "lowest_input_variant_id": lowest_input["variant_id"],
        "lowest_input_reduction_from_baseline": int(baseline["prompt_tokens"])
        - int(lowest_input["prompt_tokens"]),
        "all_quality_checks_passed": all_quality_passed,
    }


class OciCohereInferenceClient:
    """OCI native SDK implementation for the preflight-approved Cohere chat model."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def chat(self, prompt: str, settings: InferenceSettings) -> ModelResponse:
        import oci

        request = oci.generative_ai_inference.models.CohereChatRequest(
            message=prompt,
            preamble_override=SYSTEM_INSTRUCTION,
            temperature=0,
            max_tokens=settings.max_output_tokens,
        )
        details = oci.generative_ai_inference.models.ChatDetails(
            compartment_id=settings.compartment_id,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=settings.model_id
            ),
            chat_request=request,
        )
        response = self._client.chat(details).data.chat_response
        usage = response.usage
        return ModelResponse(
            text=response.text,
            prompt_tokens=None if usage is None else usage.prompt_tokens,
            completion_tokens=None if usage is None else usage.completion_tokens,
            total_tokens=None if usage is None else usage.total_tokens,
            finish_reason=response.finish_reason,
        )
