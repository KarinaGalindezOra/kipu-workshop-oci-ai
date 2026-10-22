from lab01_agent_memory.metrics import compare_prompt_usage, estimate_tokens


def test_estimate_tokens_is_deterministic() -> None:
    assert estimate_tokens("one, two!") == 4


def test_prompt_comparison_separates_repeated_and_retrieved_context() -> None:
    comparison = compare_prompt_usage(
        baseline_prompt="Rule one. Rule two. Question.",
        compact_prompt="Question.",
        retrieved_guidelines=["Rule one."],
    )

    assert comparison.baseline_prompt_tokens > comparison.memory_prompt_tokens
    assert comparison.retrieved_guideline_tokens > 0
    assert comparison.estimated_request_tokens_with_memory == (
        comparison.memory_prompt_tokens + comparison.retrieved_guideline_tokens
    )
    assert comparison.estimated_request_reduction_tokens == 3
