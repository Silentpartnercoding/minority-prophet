#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const OUTSIDE_SHELL_PATH = /(?:^|[\s"'`;|&()<>])\/(?:tmp|mnt|home|Users)(?:\/|[\s;|&]|$)|(?:^|[\s"'`;|&()<>])(?:find|ls|cd|cat|head|tail)\s+\/(?:[\s;|&]|$)|(?:^|[\s"'`;|&()<>])\.\.(?:\/|[\s;|&]|$)/m;

export function workspaceBoundaryViolations(toolEvents = []) {
  const violations = [];
  for (const event of toolEvents) {
    if (event.type === 'Bash') {
      const command = event.input?.command ?? '';
      if (OUTSIDE_SHELL_PATH.test(command)) violations.push('Bash referenced an outside-workspace path');
      continue;
    }
    if (!['Read', 'Write', 'Edit'].includes(event.type)) continue;
    const filePath = event.input?.file_path ?? '';
    const relativeEscape = filePath === '..' || filePath.startsWith('../');
    const outsideAbsolute = filePath.startsWith('/') && !filePath.includes('/mp-claude-b_tools-');
    if (relativeEscape || outsideAbsolute) violations.push(`${event.type} referenced an outside-workspace path`);
  }
  return [...new Set(violations)];
}

export function auditTrials(trials) {
  return trials.map((trial) => {
    const boundary = trial.lane === 'B_TOOLS' ? workspaceBoundaryViolations(trial.tool_events) : [];
    const failed = trial.status !== 'COMPLETED';
    const invalid = failed || boundary.length > 0;
    return {
      key: trial.key,
      model: trial.model,
      model_version: trial.model_version ?? trial.model,
      lane: trial.lane,
      case_id: trial.case_id,
      raw_correct: trial.correct ?? 0,
      raw_exact: Boolean(trial.exact),
      protocol_correct: invalid ? 0 : (trial.correct ?? 0),
      protocol_exact: invalid ? false : Boolean(trial.exact),
      invalid,
      failed,
      workspace_boundary_violations: boundary,
      execution_ms: trial.execution_ms ?? 600_000,
      tool_events: trial.tool_events?.length ?? 0
    };
  });
}

export function summarizeAudit(trials) {
  const groups = new Map();
  for (const trial of auditTrials(trials)) {
    const key = `${trial.model}\u0000${trial.lane}`;
    const group = groups.get(key) ?? {
      model: trial.model,
      model_version: trial.model_version,
      lane: trial.lane,
      trials: 0,
      protocol_correct: 0,
      raw_correct: 0,
      protocol_exact_cases: 0,
      raw_exact_cases: 0,
      invalid_trials: 0,
      workspace_boundary_violations: 0,
      failed_trials: 0,
      execution_ms: 0,
      tool_events: 0
    };
    group.trials += 1;
    group.protocol_correct += trial.protocol_correct;
    group.raw_correct += trial.raw_correct;
    group.protocol_exact_cases += Number(trial.protocol_exact);
    group.raw_exact_cases += Number(trial.raw_exact);
    group.invalid_trials += Number(trial.invalid);
    group.workspace_boundary_violations += Number(trial.workspace_boundary_violations.length > 0);
    group.failed_trials += Number(trial.failed);
    group.execution_ms += trial.execution_ms;
    group.tool_events += trial.tool_events;
    groups.set(key, group);
  }
  return [...groups.values()].sort((left, right) => left.model.localeCompare(right.model) || left.lane.localeCompare(right.lane));
}

async function main() {
  const runtime = process.argv[2];
  if (!runtime) throw new Error('usage: node capability-tournament-claude-audit.js <runtime.json>');
  const state = JSON.parse(await readFile(runtime, 'utf8'));
  process.stdout.write(`${JSON.stringify(summarizeAudit(state.trials), null, 2)}\n`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main().catch((error) => { console.error(error); process.exitCode = 1; });
