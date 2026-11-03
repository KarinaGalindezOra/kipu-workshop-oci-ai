# Real-workflow acceptance rubric

The participant reference is data/evaluation/workshop_questions.json: 16 cases, no injected failures or fixtures. Read the actual validated OCI answer next to the expected answer criteria, not only the pass flag. Reference answers are independent evaluation data and never enter model context. Custom questions are marked without a frozen reference answer.

| Gate | Requirement |
|---|---|
| Individual execution | Own OCI identity, private session, schema/table and report namespace |
| Real services | Actual embedding/ADB/chat traces for supported questions; application controls explicitly labeled |
| Version scope | Every candidate respects corpus/API/target version; positive cases must not be empty |
| Support coverage | All expected source sections and required facts present in positive answers |
| Citation coverage | Every published contractual claim has valid evidence IDs, hashes and source locators |
| Unsupported claims | Zero unsupported claims in the reviewed matrix |
| Correct abstention | SLA/TLS questions retrieve through OCI then abstain without invented facts |
| Controls | Version clarification, structured-data routing and v3 rejection correctly labeled as application decisions |
| Actual text review | Human confirms relevance, completeness and correct version alongside the actual answer |
| Operational readiness | Record service latency, usage and operational errors from approved real executions |

A source pair is (version, section). Required terms are a reproducible proxy, not a general semantic proof. Reported precision/support checks do not replace reading the actual claims. A system that always abstains fails the ten positive cases. Automatic contract checks can fail when a generated answer omits a required fact even if the citations are valid.

Record participant, reviewer, date, run/case IDs and rationale. No offline/demo report, simulated fixture, skipped service invocation, wrong-identity report or screenshot alone can establish real OCI completion. If a real operational failure occurs, record it and leave unexecuted cases pending. Developer unit/mock/UI tests remain mandatory software checks but are never participant acceptance.
