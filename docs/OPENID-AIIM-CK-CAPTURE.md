# CK SaaS cold OAuth evidence capture

This is a one-run, opt-in evidence path for the OpenID AIIM CK SaaS rerun. Keith clarified on September 29 that both the September 3 and September 15 `partner-jameshe` runs used CK's manually pre-registered client; `client_kind: dcr` is CK's internal label for a non-URL client ID, not dynamic registration. This capture path does not change either run's test outcome or award a new checkmark.

## Before contacting CK SaaS

1. Confirm the deployed Sites version includes the Drizzle migration in `drizzle/` and that the live `DB` binding contains `openid_aiim_ck_capture`. Sites applies that migration during deployment; do **not** also apply `migrations/0007_openid_aiim_ck_capture.sql` to production. That file is retained as a local SQLite test fixture. A missing or unwritable table stops the recorded path before its first CK request.
2. Use a browser session with no `mp_aiim_ck_oauth` flow cookie. The Worker has no token or metadata cache; a recorded start rejects a pre-existing flow cookie.
3. Confirm the exact intended OAuth mode and a time with Keith. Do not run `/openid-aiim/ck/start` until that is agreed.

## Recorded run

The explicit **Record cold OAuth run** link on `/openid-aiim/ck/reproduce` starts the pre-registered path with `capture=1`. The Worker persists a `capture_start` row, then a tokenless `POST /mcp` and its 401/`WWW-Authenticate` response, the challenge-advertised OPRM GET, AS metadata, and the PKCE authorization URL. The signed flow cookie carries the run ID across the browser authorization redirect. The callback records the inbound authorization response, token request and response, MCP initialization, `tools/list`, and harmless `first_contact_ping` call. A failed write aborts the flow before the next CK request.

For a CIMD rerun only if requested, use `/openid-aiim/ck/start?mode=cimd&capture=1`. Its token record retains `client_assertion_type` and the decoded `alg`, `kid`, `iss`, `sub`, `aud`, and `exp` fields but not the signed assertion.

## Private evidence review

Read the `run_id` from the callback report. Query the private D1 database by exact ID, ordered by `seq` (or read the `openid_aiim_ck_capture` table through the Sites database viewer and select/sort the exact run):

```sql
SELECT seq, at, record_json
FROM openid_aiim_ck_capture
WHERE run_id = ?
ORDER BY seq;
```

Confirm one run ID, consecutive sequence numbers, 401 before OPRM before token, `code_challenge_method=S256` in the authorization URL, `code_verifier` present in the token form, and an authenticated MCP call. The JSON records preserve method, URL, status, headers, and body fields. Values of codes, state, verifiers, tokens, assertions, cookies, and MCP session IDs are replaced with `<redacted>` before storage. Do not put full records in Master Hand or Slack; share only the bounded evidence package through an agreed destination after owner approval.

Local verification uses synthetic responses only: `node --test tests/openid-aiim-ck-capture.test.mjs`. This does not prove CK's live response or Atul's acceptance.
