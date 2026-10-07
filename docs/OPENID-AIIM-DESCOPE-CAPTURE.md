# OpenID AIIM CIMD evidence capture

The hosted `/openid-aiim/start` path is evidence-mandatory. It will not contact an interoperability partner unless the private D1 binding is present and the first append-only evidence write succeeds. There is no unrecorded browser-run path.

## What one successful run retains

All records share one random `run_id` and consecutive `seq` values. Every HTTP exchange records UTC `started_at` and `completed_at` values, the request method and exact redacted URL, redacted request and response headers and bodies, the response status, and bounded partner correlation headers (`x-request-id`, `x-correlation-id`, `traceparent`, `cf-ray`, or `seal_in`) when returned.

The required phase order is:

1. `capture_start`
2. `tokenless_mcp`
3. `oprm`
4. `authorization_server_metadata`
5. `authorization_redirect`
6. `authorization_callback`
7. `token_exchange`
8. `mcp_initialize`
9. `mcp_initialized_notification`
10. `tools_list`
11. `capture_complete`

The final row contains the schema, run ID, expected record count, required phase list, outcome, and tool-call boundary. The UI reports success only after that row is durably written. OAuth error callbacks are retained even when no token is issued. A failed evidence write stops the flow before the next partner request; a failure after the token exchange stops before authenticated MCP traffic.

Authorization codes, OAuth state, PKCE verifiers, access and refresh tokens, ID tokens, client assertions, passwords, cookies, MCP session IDs, client secrets, and private keys are replaced with `<redacted>` or are never passed to the capture layer. Bodies larger than 64 KiB or with an unrecognized format abort the captured run rather than silently producing partial evidence.

## Private review and export

Read the `run_id` from the callback report and query the private D1 database by exact ID:

```sql
SELECT run_id, seq, at, record_json
FROM openid_aiim_descope_capture
WHERE run_id = ?
ORDER BY seq;
```

Before using the evidence, confirm one run ID, sequence values `0` through `10`, the exact phase order above, `evidence_record_count = 11`, and `outcome = success` in `capture_complete`. Preserve the ordered rows as the raw client-side log and derive any bounded report from that immutable export. Do not put full records in Master Hand or Slack.

## Evidence boundary

This capture proves what the Minority Prophet client sent and received and what the Minority Prophet MCP resource observed. It cannot substitute for the authorization server's private validation telemetry. For a CIMD grading report, the authorization-server operator must still supply its own raw lines showing the client metadata fetch, JWKS/key selection, PKCE validation, and `private_key_jwt` validation. Match those server-side lines to this capture by UTC window, client ID, endpoint, and correlation identifiers where available.

Local verification uses synthetic traffic only:

```sh
node --test tests/openid-aiim-descope-capture.test.mjs
```

Passing locally verifies the capture and redaction behavior; it does not prove a live partner result or organizer acceptance.
