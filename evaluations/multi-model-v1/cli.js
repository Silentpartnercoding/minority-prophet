#!/usr/bin/env node
import { developmentBenchmark } from './benchmark.js';
import { openStore, publishLocalDemo, runLocalDemo } from './operations.js';
import { startServer } from './server.js';
import { verifyRun } from './verifier.js';

const command = process.argv[2] ?? 'help';

if (command === 'generate') {
  const benchmark = developmentBenchmark();
  console.log(JSON.stringify({ manifest: benchmark.manifest, worlds: benchmark.worlds.length }, null, 2));
} else if (command === 'run-demo') {
  const result = await runLocalDemo();
  console.log(JSON.stringify({ run_id: result.run.id, status: result.run.status, completed_trials: result.run.completed_trials, verification: result.verification.status, official_eligible: result.verification.official_eligible }, null, 2));
} else if (command === 'verify') {
  const store = await openStore();
  const runId = process.argv[3] ?? store.all('benchmark_runs').at(-1)?.id;
  if (!runId) throw new Error('No run exists');
  console.log(JSON.stringify(await verifyRun(store, runId), null, 2));
} else if (command === 'publish-local') {
  console.log(JSON.stringify(await publishLocalDemo(), null, 2));
} else if (command === 'serve') {
  const port = Number(process.env.PORT ?? 4173);
  await startServer({ port });
  console.log(`Minority Prophet evaluation site: http://127.0.0.1:${port}`);
} else {
  console.log('Commands: generate | run-demo | verify [run-id] | publish-local | serve');
}
