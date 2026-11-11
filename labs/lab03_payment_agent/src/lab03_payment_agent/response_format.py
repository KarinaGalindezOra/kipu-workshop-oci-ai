"""Strict final-answer presentation normalization; no narrative or JSON repair."""

import json
import re


def parse_final_response(raw: str) -> dict:
    """Accept JSON presentation markers and a scalar citation alias without repairing content."""
    if not isinstance(raw, str) or len(raw) > 20000:
        raise ValueError("Invalid final response size or type")
    value = raw.strip()
    marker = re.match(r"^```(?:json)?[ \t]*\r?\n", value)
    if marker:
        value = value[marker.end() :].strip()
        if value.endswith("```"):
            value = value[:-3].strip()

    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("Duplicate final response key")
            result[key] = item
        return result

    result = json.loads(value, object_pairs_hook=unique_object)
    if not isinstance(result, dict):
        raise ValueError("Final response must be an object")
    claims = result.get("claims", [])
    if not isinstance(claims, list):
        raise ValueError("Claims must be an array")
    if claims and all(isinstance(claim, str) for claim in claims):
        shared = result.get("evidence_ids")
        if (
            not isinstance(shared, list)
            or len(shared) != 1
            or not isinstance(shared[0], str)
            or not shared[0].strip()
            or any(not claim.strip() for claim in claims)
        ):
            raise ValueError("Ambiguous shared citation representation")
        result["claims"] = [{"text": claim, "evidence_ids": list(shared)} for claim in claims]
        claims = result["claims"]
        del result["evidence_ids"]
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Each claim must be an object")
        if "evidence_id" in claim:
            if "evidence_ids" in claim or not isinstance(claim["evidence_id"], str):
                raise ValueError("Ambiguous citation representation")
            claim["evidence_ids"] = [claim.pop("evidence_id")]
    return result
