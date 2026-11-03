"""Frozen acceptance evaluation with gold sections and independent extractive checks."""

import argparse
import hashlib
import json
import statistics
from dataclasses import replace
from pathlib import Path

from .agent import run_agent
from .corpus import LAB_ROOT, load_corpus
from .participant import artifact_directory
from .retrieval import retrieve


def fixture_retriever(case, chunks, base):
    fixture = case.get("fixture")
    if fixture not in {"T16", "T18", "T20"}:
        return base

    def wrapped(version, question):
        if fixture == "T20":
            raise TimeoutError("Private provider exception must not enter reports")
        original = next(
            c for c in chunks if c.contract_version == "v2" and c.section == "Idempotency"
        )
        name = "conflict" if fixture == "T16" else "injection"
        data = json.loads(
            (LAB_ROOT / f"data/evaluation/adversarial_fixtures/{name}.json").read_text(
                encoding="utf-8"
            )
        )
        content = data["content"]
        changed = replace(
            original,
            chunk_id=f"fixture-{name}",
            content=content,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
        )
        from .models import RetrievedEvidence

        items = [RetrievedEvidence(changed, 1)]
        return [RetrievedEvidence(original, 2), *items] if fixture == "T16" else items

    return wrapped


def grade(case: dict, result: dict) -> dict:
    sources = result["citations"]
    ids = {s["evidence_id"]: s for s in sources}
    claims = result["claims"]
    valid = all(
        claim.get("evidence_ids")
        and all(
            eid in ids
            and claim["text"] in ids[eid]["excerpt"]
            and hashlib.sha256(ids[eid]["excerpt"].encode()).hexdigest() == ids[eid]["content_hash"]
            for eid in claim["evidence_ids"]
        )
        for claim in claims
    )
    scope = all(s["contract_version"] in case["versions"] for s in result["candidates"])
    expected = {(v, s) for v in case["versions"] for s in case["sections"]}
    actual = {(s["contract_version"], s["section"]) for s in sources}
    text = " ".join(c["text"] for c in claims)
    recall = len(expected & actual) / len(expected) if expected else None
    precision = len(expected & actual) / len(actual) if actual and expected else None
    passed = (
        result["status"] == case["expected_status"]
        and valid
        and scope
        and expected <= actual
        and all(term in text for term in case["required_terms"])
    )
    if case["expected_status"] == "answered":
        passed = passed and bool(claims) and bool(sources)
    return {
        "id": case["id"],
        "passed": bool(passed),
        "status": result["status"],
        "expected_status": case["expected_status"],
        "version_scope_pass": scope,
        "citation_checks_pass": valid,
        "support_recall": recall,
        "accepted_evidence_precision": precision,
    }


def evaluate(cases: list[dict], retriever=None, generator=None) -> dict:
    """Developer-only fixture regression. Never mix fixtures with real inference."""
    if generator is not None:
        raise ValueError(
            "Use the real OCI workshop evaluator; fixtures cannot call cloud generators"
        )
    chunks = load_corpus()
    base = retriever or (lambda version, question: retrieve(chunks, question, version))
    rows, results = [], []
    for case in cases:
        generate = generator
        if case.get("fixture") == "T17":

            def generate(q, e):
                return {
                    "status": "answered",
                    "claims": [{"text": "Unsupported output", "evidence_ids": ["E999"]}],
                }

        result = run_agent(
            case["question"], fixture_retriever(case, chunks, base), generator=generate
        )
        result["case_id"] = case["id"]
        result["fixture_simulated"] = bool(case.get("fixture"))
        rows.append(grade(case, result))
        results.append(result)
    precisions = [
        r["accepted_evidence_precision"]
        for r in rows
        if r["accepted_evidence_precision"] is not None
    ]
    precision = statistics.mean(precisions) if precisions else None
    durations = sorted(r["timings_ms"]["total"] for r in results)
    return {
        "report_version": "2.0",
        "mode": "oci" if generator else "local",
        "acceptance_pass": all(r["passed"] for r in rows)
        and precision is not None
        and precision >= 0.8,
        "accepted_evidence_precision": precision,
        "latency_median_ms": statistics.median(durations),
        "latency_p95_ms": durations[max(0, int(len(durations) * 0.95 + 0.999) - 1)],
        "human_relevance_review_required": True,
        "cloud_validation": "executed" if generator else "not_run",
        "simulated_cases": [c["id"] for c in cases if c.get("fixture")],
        "cases": rows,
        "results": results,
    }


def _main() -> None:
    """The participant evaluator accepts real OCI execution only; fixtures are developer tests."""
    from getpass import getpass

    from .dashboard import workshop_cases
    from .execution import execute_live
    from .live_validation import settings_from_environment
    from .private_session import add_session_file_argument, load_participant_session

    parser = argparse.ArgumentParser(description=__doc__)
    add_session_file_argument(parser)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab02"))
    parser.add_argument("--mode", choices=["oci"], default="oci")
    parser.add_argument("--confirm-live-inference", action="store_true")
    args = parser.parse_args()
    if not args.confirm_live_inference:
        parser.error("Workshop evaluation requires real OCI access and --confirm-live-inference")
    load_participant_session(args.session_file)
    settings = settings_from_environment()
    cases = workshop_cases()
    database_password = getpass("My database password: ")
    wallet_password = getpass("Wallet password: ")
    results, rows = [], []
    for case in cases:
        result = execute_live(
            settings,
            case["question"],
            confirm_inference=True,
            database_password=database_password,
            wallet_password=wallet_password,
            output_root=args.output_dir,
        )
        result["case_id"] = case["id"]
        results.append(result)
        rows.append(grade(case, result))
        if result["status"] == "error":
            break
    database_password = wallet_password = ""
    report = {
        "report_version": "2.1",
        "participant_id": settings.participant_id,
        "mode": "oci",
        "simulated_cases": [],
        "cases": rows,
        "results": results,
        "acceptance_pass": len(rows) == len(cases) and all(row["passed"] for row in rows),
        "not_run_cases": [c["id"] for c in cases[len(rows) :]],
        "cloud_validation": "requires_review",
        "human_relevance_review_required": True,
    }
    output = artifact_directory(args.output_dir, settings.participant_id)
    output.mkdir(parents=True, exist_ok=True)
    (output / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"EVALUATION_REPORT {output / 'evaluation.json'}")
    print(f"CASES_PASSED {sum(r['passed'] for r in rows)}/{len(cases)}")
    if not report["acceptance_pass"]:
        raise SystemExit(1)


def main() -> None:
    try:
        _main()
    except Exception:
        raise SystemExit("Evaluation failed; consult the private troubleshooting runbook") from None


if __name__ == "__main__":
    main()
