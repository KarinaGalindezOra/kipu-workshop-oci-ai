# Workshop 1: Token Economy and Decision Memory

Lab 1 is a hands-on Oracle AI Agent Memory exercise backed by Autonomous Database. Each participant directly uses the Oracle SDK with an individual temporary application database user, an mTLS wallet, and a pre-created team memory store. First, the participant persists and retrieves one selected synthetic decision through ADB without inference. Then the participant makes two bounded OCI Generative AI calls with synthetic data and compares provider-reported token usage.

## Learning outcome

Participants persist synthetic engineering decisions as `guideline` records, retrieve them with exact `user_id` scope plus `record_types=["guideline"]`, verify that a control-scope query is not returned from their individual scope, and compare two real OCI Inference requests: a repetitive prompt and a compact prompt plus retrieved memory.

The participant never uses `ADMIN`, never creates Agent Memory objects, and always runs with `SchemaPolicy.REQUIRE_EXISTING`.

## Repository components

- `src/lab01_agent_memory/sdk_exercise.py`: credential-free core exercise behavior and evidence schema.
- `scripts/run_participant_sdk_lab.py`: direct Oracle AI Agent Memory SDK runner.
- `scripts/run_participant_live.ps1`: participant launcher for preflight, the real no-inference memory exercise, and the single two-call token comparison.
- `ui/app.py`: visualizes safe JSON evidence; it does not receive or display credentials.
- `tests/test_sdk_exercise.py`: deterministic core behavior tests.
- `../../platform/bootstrap/`: database owner and runtime-access SQL scripts.

## Local verification

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[lab01,dev,ui]"
python -m pytest labs/lab01_agent_memory/tests -q
```

## Direct SDK execution

The workshop team prepares ADB, the memory store, participant database user, wallet and individual OCI identity before the participant begins. The participant receives those private prerequisites through the approved channel.

The participant starts with the generic launcher documented in the Spanish [participant guide](../../docs/participant-guides/01-decision-memory.md). Its `-Preflight` mode checks the private local configuration without invoking the model. Its `-MemoryExercise` mode persists and retrieves one approved synthetic decision from ADB without invoking the model and writes `memory-exercise-evidence.json`. The live mode explicitly confirms the exactly two on-demand calls and writes only a safe JSON evidence artifact, such as `artifacts/lab01/t01/p01/oci-inference-evidence.json`.

The live comparison accepts evidence only when OCI returns complete usage statistics, both responses satisfy the bundle's required decision terms, and the memory-optimized request uses fewer provider-reported input tokens. This result is not a claim about total solution cost: memory, storage, and retrieval have separate costs.

## Scope and security boundary

An exact `user_id` passed to Agent Memory search is a retrieval boundary. It is real behavior in Agent Memory, but it is not row-level authorization by itself: a caller able to change the scope value could request a different scope. This workshop uses synthetic data and temporary credentials. A production service must derive the scope from authenticated identity and apply database, IAM, and network controls.

## Documents

- [Participant guide](../../docs/participant-guides/01-decision-memory.md)
- [Architecture](../../docs/architecture.md)
