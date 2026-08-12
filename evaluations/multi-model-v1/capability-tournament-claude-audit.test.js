import assert from 'node:assert/strict';
import test from 'node:test';
import { summarizeAudit, workspaceBoundaryViolations } from './capability-tournament-claude-audit.js';

test('workspace audit permits the contestant directory and rejects outside paths', () => {
  assert.deepEqual(workspaceBoundaryViolations([
    { type: 'Read', input: { file_path: '/private/var/folders/x/T/mp-claude-b_tools-123/case.json' } },
    { type: 'Bash', input: { command: 'python3 analyze.py 2>/dev/null' } }
  ]), []);
  assert.deepEqual(workspaceBoundaryViolations([
    { type: 'Bash', input: { command: 'ls /tmp; find / -name case.json' } },
    { type: 'Write', input: { file_path: '/tmp/output.json' } }
  ]), [
    'Bash referenced an outside-workspace path',
    'Write referenced an outside-workspace path'
  ]);
  assert.deepEqual(workspaceBoundaryViolations([
    { type: 'Bash', input: { command: 'ls /tmp; pwd' } }
  ]), ['Bash referenced an outside-workspace path']);
});

test('audit preserves raw answers and applies the preregistered invalid-trial penalty', () => {
  const [summary] = summarizeAudit([
    { key: 'x', model: 'opus', model_version: 'claude-opus-5', lane: 'B_TOOLS', case_id: 'cap_001', status: 'COMPLETED', correct: 16, exact: true, execution_ms: 100, tool_events: [{ type: 'Bash', input: { command: 'ls /tmp' } }] },
    { key: 'y', model: 'opus', model_version: 'claude-opus-5', lane: 'B_TOOLS', case_id: 'cap_002', status: 'COMPLETED', correct: 10, exact: false, execution_ms: 200, tool_events: [] }
  ]);
  assert.equal(summary.raw_correct, 26);
  assert.equal(summary.protocol_correct, 10);
  assert.equal(summary.raw_exact_cases, 1);
  assert.equal(summary.protocol_exact_cases, 0);
  assert.equal(summary.invalid_trials, 1);
  assert.equal(summary.workspace_boundary_violations, 1);
});
