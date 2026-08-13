#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import process from 'node:process';

import { executeMinorityProphetTool } from './mp-tool-v2.js';
import { startMcpStdio } from './mp-mcp-server.js';
import { compileProvenanceProposal } from './provenance-receipt.js';
import { runtimeReadiness, startRuntimeServer } from './runtime-http.js';

async function input(path) {
  const raw = path ? await readFile(path, 'utf8') : await new Promise((resolve) => {
    let value = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { value += chunk; });
    process.stdin.on('end', () => resolve(value));
  });
  return JSON.parse(raw);
}

function flag(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const command = process.argv[2] ?? 'help';
if (command === 'mcp') startMcpStdio();
else if (command === 'analyze') {
  process.stdout.write(`${JSON.stringify(executeMinorityProphetTool(await input(flag('--input'))), null, 2)}\n`);
} else if (command === 'receipt') {
  const value = await input(flag('--input'));
  process.stdout.write(`${JSON.stringify(compileProvenanceProposal(value.packet, value.proposal), null, 2)}\n`);
} else if (command === 'doctor') {
  const host = process.env.MP_ENGINE_HOST ?? '127.0.0.1';
  const readiness = runtimeReadiness({ host, token: process.env.MP_ENGINE_TOKEN ?? '',
    allowInsecureLocal: process.env.MP_ENGINE_ALLOW_INSECURE_LOCAL === '1' });
  const report = { schema: 'mp-engine-doctor.v1', node: process.version, host, ...readiness };
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  process.exit(report.ready ? 0 : 1);
} else if (command === 'serve') {
  const server = await startRuntimeServer();
  const address = server.address();
  process.stdout.write(`${JSON.stringify({ event: 'listening', host: address.address, port: address.port })}\n`);
} else {
  process.stdout.write('Usage: mp-engine <doctor|analyze|receipt|mcp|serve> [--input FILE]\n');
  process.exit(command === 'help' ? 0 : 2);
}
