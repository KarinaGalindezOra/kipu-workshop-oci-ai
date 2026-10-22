"""Transparent, model-agnostic token estimates for the Phase 1 offline demo."""

from dataclasses import asdict, dataclass
import re


_TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def estimate_tokens(text: str) -> int:
    """Return a deterministic approximation, not a provider billing meter.

    OCI model-specific usage returned by the selected inference API replaces this
    estimate during the Trial integration phase.
    """

    return len(_TOKEN_PATTERN.findall(text))


@dataclass(frozen=True)
class PromptComparison:
    """Separate inference-input reduction from memory lifecycle activity."""

    baseline_prompt_tokens: int
    memory_prompt_tokens: int
    retrieved_guideline_tokens: int
    estimated_request_tokens_with_memory: int
    repeated_prompt_reduction_tokens: int
    estimated_request_reduction_tokens: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


def compare_prompt_usage(
    baseline_prompt: str,
    compact_prompt: str,
    retrieved_guidelines: list[str],
) -> PromptComparison:
    """Compare a repeated prompt against a compact scoped-memory request."""

    baseline_tokens = estimate_tokens(baseline_prompt)
    compact_tokens = estimate_tokens(compact_prompt)
    guideline_tokens = estimate_tokens("\n".join(retrieved_guidelines))
    request_tokens_with_memory = compact_tokens + guideline_tokens
    return PromptComparison(
        baseline_prompt_tokens=baseline_tokens,
        memory_prompt_tokens=compact_tokens,
        retrieved_guideline_tokens=guideline_tokens,
        estimated_request_tokens_with_memory=request_tokens_with_memory,
        repeated_prompt_reduction_tokens=max(baseline_tokens - compact_tokens, 0),
        estimated_request_reduction_tokens=max(baseline_tokens - request_tokens_with_memory, 0),
    )
