# Local dashboard operations

## Binding and privacy

Launch scripts/run_dashboard.py from the participant's own private session. It validates LAB02_PARTICIPANT_ID and binds Streamlit to 127.0.0.1:8502. LAB02_REPORT_ROOT optionally selects a trusted report root; the UI always adds the assigned participant namespace. No account selector, arbitrary report path input, upload, global connection cache or shared credential store is available. A browser session may hold one participant-only ADB pool with a maximum of one connection. It is bound to the participant/schema/DSN/wallet target, cannot be reused after an identity change, never writes plaintext credentials, and is closed when the dashboard process ends. Peer paths, redirected participant directories, legacy offline reports and simulated fixtures are rejected by the reader.

This is a local internal workshop prototype, not a production authenticated web service. Another person with access to the same OS account/port is not blocked by a server login. Use separate workstations or private OS/Cloud Shell workspaces; never expose the loopback server via a public proxy without a new authenticated design.

## Actions and controls

The corpus action calls actual OCI document embeddings and inserts only approved missing chunks in the authenticated participant schema. The question action uses actual query embeddings, ADB exact search and OCI chat when supporting evidence exists. UI and CLI share execution.py; neither imports a lexical retriever or fixture factory. Missing credentials/configuration, invalid calibration, failed queries and rejected model output stop the workflow without a substitute answer.

Inference and synthetic-load acknowledgements are independent and reset per submission. Password widgets are masked and clear on submission; plaintext credentials never enter report data or Streamlit caches. The database driver may retain an authenticated connection inside the participant-only local pool to avoid a new wallet/TLS handshake on every request. Organization approval is separate from these acknowledgements. No bulk evaluation runs automatically on opening the UI or changing a question. Developer tests use AppTest/doubles but are never a participant mode.

## Visible review

The observed column displays only the published actual validated model answer or the explicit nonanswer state. The expected column is loaded from the independent frozen workshop reference. That reference is never sent to the model. Custom questions are visibly ungraded against a golden answer. Structural/fact checks can fail even when citations exist; human relevance/completeness review remains required.

Claim-to-citation expanders expose excerpt, version, section, source URI, line span, chunk ID and content hash. Candidate ranks are separate from accepted evidence. Service operations show attempted/succeeded/failed status and elapsed time; counters represent attempts and provider usage is null when not supplied. A rate-limited operation is labeled without exposing exception text. No raw model drafts, SDK profile data or secrets are displayed.

Clarification, structured-data routing and unsupported-version handling are application decisions. They are never labeled as model responses. Unsupported documentary queries with a valid version perform real OCI retrieval, but may abstain before chat if selected support is absent. Failed connectivity is an operational error, not an insufficiency success.

## History and review

Only own reports with mode=oci, an explicit service/application origin and fixture_simulated=false are accepted. Refresh history to inspect a new run. Reports are local review artifacts, not independently signed proof that a provider executed an operation. During rehearsal corroborate actual calls and provider usage with approved OCI observability. Never import an example file as real execution evidence.

The acceptance set is workshop_questions.json (16 cases). The four artificial error/adversarial fixtures from developer tests are excluded. A real operational error is displayed when it occurs; it is not deliberately injected during the participant session. The CLI evaluator stops on operational error and records remaining cases as not run.

## Workshop 1 comparison

The existing Workshop 1 guide launches Streamlit locally per participant. Its app also includes a teaching simulator and multiple evidence views, so locality alone was not identity binding. Workshop 2 deliberately binds its process and history to the participant session and offers real-service actions only. Workshop 1 files are unchanged.

References: [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form), [Streamlit AppTest for developer tests](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
