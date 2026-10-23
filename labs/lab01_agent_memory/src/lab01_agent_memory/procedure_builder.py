"""Validated synthetic procedural definitions for the extended Lab 1 exercises."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_VERSION = re.compile(r"^[0-9]+\.[0-9]+$")
_MAX_PROCEDURE_CHARS = 1_200
_MAX_TRIGGER_TERMS = 8
_MAX_EVIDENCE_FIELDS = 8


def _required_string(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Procedure field '{field}' must be a non-empty string")
    return value.strip()


def _string_list(payload: dict[str, Any], field: str, maximum: int) -> tuple[str, ...]:
    value = payload.get(field)
    if not isinstance(value, list) or not value or len(value) > maximum:
        raise ValueError(f"Procedure field '{field}' must contain between 1 and {maximum} strings")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"Procedure field '{field}' must contain non-empty strings")
    return tuple(item.strip() for item in value)


@dataclass(frozen=True)
class ProcedureDefinition:
    """A versioned, synthetic procedure that can safely enter a participant scope."""

    procedure_id: str
    title: str
    version: str
    domain: str
    trigger_terms: tuple[str, ...]
    procedure: str
    required_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.procedure_id):
            raise ValueError("procedure_id must use lowercase letters, digits, and hyphens")
        if not _VERSION.fullmatch(self.version):
            raise ValueError("version must use the form major.minor")
        if len(self.procedure) > _MAX_PROCEDURE_CHARS:
            raise ValueError(f"procedure must not exceed {_MAX_PROCEDURE_CHARS} characters")
        if len(self.trigger_terms) > _MAX_TRIGGER_TERMS:
            raise ValueError("Too many trigger_terms")
        if len(self.required_evidence) > _MAX_EVIDENCE_FIELDS:
            raise ValueError("Too many required_evidence fields")

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ProcedureDefinition":
        """Create one validated definition from a non-secret JSON object."""

        if payload.get("synthetic") is not True:
            raise ValueError("Procedure definitions must explicitly declare synthetic=true")
        return cls(
            procedure_id=_required_string(payload, "procedure_id"),
            title=_required_string(payload, "title"),
            version=_required_string(payload, "version"),
            domain=_required_string(payload, "domain"),
            trigger_terms=_string_list(payload, "trigger_terms", _MAX_TRIGGER_TERMS),
            procedure=_required_string(payload, "procedure"),
            required_evidence=_string_list(payload, "required_evidence", _MAX_EVIDENCE_FIELDS),
        )

    def as_memory_content(self) -> str:
        """Build stable text passed to Agent Memory without putting metadata in prompt code."""

        evidence = ", ".join(self.required_evidence)
        return (
            f"Procedure [{self.procedure_id}] version {self.version}. {self.procedure} "
            f"Required evidence: {evidence}."
        )

    def as_metadata(self) -> dict[str, str]:
        """Return safe metadata for an Agent Memory guideline record."""

        return {
            "procedure_id": self.procedure_id,
            "title": self.title,
            "version": self.version,
            "domain": self.domain,
            "synthetic": "true",
            "lab": "lab01",
        }


def load_procedure_definition(path: Path) -> ProcedureDefinition:
    """Load a structured synthetic procedure from disk without accepting arbitrary content."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Procedure file was not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Procedure file is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise ValueError("Procedure file root must be a JSON object")
    return ProcedureDefinition.from_payload(payload)
