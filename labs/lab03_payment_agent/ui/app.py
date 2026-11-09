"""Participant-local Streamlit workbench. No simulated cloud success path."""

from pathlib import Path

import streamlit as st
from lab03_payment_agent.confirmation import memory_proposal, review, save
from lab03_payment_agent.domain import Request, digest, investigate
from lab03_payment_agent.live import LiveBackend, Settings, write_receipt, write_report

st.set_page_config(page_title="Payment Investigation Agent", layout="wide")
st.title("Payment Investigation Agent")
st.caption("Synthetic workshop prototype. Human review is required. Not production-ready.")
state = st.session_state


def disconnect():
    backend = state.pop("backend", None)
    if backend:
        backend.close()
    for key in ("result", "request_hash", "case_saved"):
        state.pop(key, None)


with st.sidebar:
    st.header("1. Connection")
    session_path = st.text_input(
        "Private session file", placeholder="Absolute path outside the repository"
    )
    report_root = st.text_input(
        "Private evidence directory",
        value=str(Path.home() / "KhipuPrivate" / "workshop3" / "evidence"),
    )
    with st.form("connect", clear_on_submit=True):
        db_password = st.text_input("Database password", type="password")
        wallet_password = st.text_input("Wallet password", type="password")
        connect = st.form_submit_button("Connect and check readiness")
    if connect:
        candidate = None
        try:
            disconnect()
            settings = Settings.load(Path(session_path))
            candidate = LiveBackend(settings, db_password, wallet_password)
            candidate.readiness()
            state.backend = candidate
            st.success("Individual database identity verified")
        except Exception:
            if candidate:
                candidate.close()
            st.error("Connection failed. Check the private assignment and facilitator readiness.")
        finally:
            db_password = wallet_password = None
    if st.button("Disconnect / start a new session"):
        disconnect()
        st.rerun()

backend = state.get("backend")
if not backend:
    st.info("Connect using your individual assignment. No paid call is made by readiness.")
    st.stop()

st.header("2. Memory and evidence")
if st.button("Recover approved memories (no inference)"):
    try:
        records = backend.memories("payment idempotency")
        st.json([m.__dict__ for m in records])
        for memory in records:
            if memory.identifier == "payment-idempotency-approved":
                write_receipt(
                    Path(report_root),
                    backend.identity,
                    memory.source_run,
                    "memory_recovery",
                    {"recovered_after_connection": True, **memory.__dict__},
                )
        st.caption(
            "After saving a new memory, reconnect and find its identifier and source_run here."
        )
    except Exception:
        st.error("Memory retrieval failed; contact the facilitator.")

st.header("3. Investigate")
question = st.text_area(
    "Synthetic question", value="Investigate payment idempotency and prepare a recommendation."
)
payment_id = st.selectbox("Synthetic payment", ["PAY-104", "PAY-105", "PAY-106", "PAY-999"])
version = st.selectbox("Contract version", ["v2", "v1", "unspecified"])
request = Request(question, payment_id, version)
request_hash = digest(request.__dict__)
paid = st.checkbox(
    "I approve paid embeddings and agent inference for this execution.",
    key="paid-" + str(state.get("paid_generation", 0)),
)
if st.button("Run investigation", disabled=not paid):
    state.pop("case_saved", None)
    with st.spinner("Recovering context and running the ADB agent..."):
        state.result = investigate(backend, request)
        state.request_hash = request_hash
    try:
        write_report(state.result, Path(report_root), backend.identity)
    except Exception:
        st.warning("Execution completed but evidence export failed. Download the result below.")
    state.paid_generation = state.get("paid_generation", 0) + 1
    st.rerun()

result = state.get("result")
if result:
    st.header("4. Response and trace")
    st.write("Status:", result.status)
    st.caption("Execution mode: " + result.execution_mode)
    st.code(result.answer, language=None)
    sources, memories, tools, metrics = st.tabs(
        ["Contract citations", "Procedures", "Tool observations", "Metrics"]
    )
    sources.json(result.citations)
    memories.json(result.memories)
    tools.json(result.tools)
    metrics.json(result.telemetry)
    import json

    st.download_button(
        "Download evidence JSON", json.dumps(result.as_dict(), indent=2), "evidence.json"
    )
    current = state.get("request_hash") == request_hash
    if not current:
        st.warning("Inputs changed. Run again before confirming any proposal.")
    if result.proposal and current:
        st.header("5. Human review")
        st.json(result.proposal)
        case_hash = digest(result.proposal)
        approved_case = st.checkbox(
            "I reviewed and approve this exact case.", key="case-" + case_hash
        )
        if st.button("Register case", disabled=not approved_case):
            try:
                receipt = save(
                    backend,
                    backend.identity,
                    "case",
                    result.proposal,
                    review(backend.identity, "case", result.proposal),
                )
                state.case_saved = result.run_id
                st.json(receipt)
                write_receipt(
                    Path(report_root), backend.identity, result.run_id, "case_confirmation", receipt
                )
            except Exception:
                st.error(
                    "Save outcome is unknown. Audit the write ledger before retrying the same content."
                )
        if state.get("case_saved") == result.run_id:
            st.header("6. Approve a reusable procedural memory")
            proposal = memory_proposal(result)
            st.json(proposal)
            approved_memory = st.checkbox(
                "I approve this procedure and its provenance.", key="memory-" + digest(proposal)
            )
            if st.button("Save approved memory", disabled=not approved_memory):
                try:
                    receipt = save(
                        backend,
                        backend.identity,
                        "memory",
                        proposal,
                        review(backend.identity, "memory", proposal),
                    )
                    st.json(receipt)
                    write_receipt(
                        Path(report_root),
                        backend.identity,
                        result.run_id,
                        "memory_confirmation",
                        receipt,
                    )
                    st.success("Reconnect and recover this memory from a new session.")
                except Exception:
                    st.error(
                        "Save outcome is unknown. Audit the write ledger; do not change the proposed content."
                    )

st.header("7. Evaluation")
st.markdown(
    "- Verify the contract version and quoted claims.\n- Compare request identifiers, keys and hashes.\n- Repeat with PAY-105 and PAY-999.\n- Use v1 and unspecified version to inspect conflict and clarification.\n- Reconnect and recover the approved memory."
)
