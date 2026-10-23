"""Load bounded, synthetic context experiments for the extended workshop."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inference import ContextExperimentVariant
from .procedure_builder import ProcedureDefinition


def _required_string(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Experiment field '{field}' must be a non-empty string")
    return value.strip()


def _required_strings(payload: dict[str, Any], field: str) -> tuple[str, ...]:
    value = payload.get(field)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Experiment field '{field}' must be a non-empty array")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"Experiment field '{field}' must contain non-empty strings")
    return tuple(item.strip() for item in value)


@dataclass(frozen=True)
class ContextExperimentPlan:
    """A portable plan for a finite set of real OCI inference variants."""

    experiment_id: str
    title: str
    question: str
    retrieval_query: str
    control_query: str
    procedures: tuple[ProcedureDefinition, ...]
    variants: tuple[ContextExperimentVariant, ...]

    def procedure_contents(self) -> dict[str, str]:
        """Return exact synthetic text associated with each approved procedure."""

        return {
            procedure.procedure_id: procedure.as_memory_content() for procedure in self.procedures
        }


def load_context_experiment(path: Path) -> ContextExperimentPlan:
    """Load a safe experiment plan and resolve every variant against its catalog."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Experiment file was not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Experiment file is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise ValueError("Experiment file root must be a JSON object")
    if payload.get("synthetic") is not True:
        raise ValueError("Experiment plans must explicitly declare synthetic=true")

    raw_procedures = payload.get("procedures")
    if not isinstance(raw_procedures, list) or not raw_procedures:
        raise ValueError("Experiment field 'procedures' must be a non-empty array")
    procedures = tuple(ProcedureDefinition.from_payload(entry) for entry in raw_procedures)
    by_id = {procedure.procedure_id: procedure for procedure in procedures}
    if len(by_id) != len(procedures):
        raise ValueError("Experiment procedure_id values must be unique")

    raw_variants = payload.get("variants")
    if not isinstance(raw_variants, list) or not 2 <= len(raw_variants) <= 8:
        raise ValueError("Experiment field 'variants' must contain between 2 and 8 entries")
    variants: list[ContextExperimentVariant] = []
    for entry in raw_variants:
        if not isinstance(entry, dict):
            raise ValueError("Every experiment variant must be a JSON object")
        procedure_ids = _required_strings(entry, "procedure_ids")
        unknown = [procedure_id for procedure_id in procedure_ids if procedure_id not in by_id]
        if unknown:
            raise ValueError(f"Experiment variant references unknown procedure IDs: {unknown}")
        variants.append(
            ContextExperimentVariant(
                variant_id=_required_string(entry, "variant_id"),
                label=_required_string(entry, "label"),
                decisions=tuple(
                    (procedure_id, by_id[procedure_id].as_memory_content())
                    for procedure_id in procedure_ids
                ),
                required_terms=_required_strings(entry, "required_terms"),
            )
        )

    return ContextExperimentPlan(
        experiment_id=_required_string(payload, "experiment_id"),
        title=_required_string(payload, "title"),
        question=_required_string(payload, "question"),
        retrieval_query=_required_string(payload, "retrieval_query"),
        control_query=_required_string(payload, "control_query"),
        procedures=procedures,
        variants=tuple(variants),
    )
