import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { developmentBenchmark } from './benchmark.js';
import { runBenchmark } from './pipeline.js';
import { DeterministicAdapter } from './providers.js';
import { startServer } from './server.js';
import { JsonStore } from './store.js';
import { verifyRun } from './verifier.js';

test('public API isolates DEMO and hides private worlds',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'mp-web-')),statePath=join(dir,'state.json');
 const store=await new JsonStore(statePath).load();
 const adapters=[new DeterministicAdapter('majority-follower-v1'),new DeterministicAdapter('lineage-reasoner-v1')];
 const run=await runBenchmark({store,benchmark:developmentBenchmark({count:1}),adapters,runId:'web-run'});
 await verifyRun(store,run.id);
 const server=await startServer({port:0,statePath,adminToken:'test-token'});
 const base=`http://127.0.0.1:${server.address().port}`;
 try{
  assert.deepEqual(await(await fetch(`${base}/api/leaderboard`)).json(),[]);
  const demo=await(await fetch(`${base}/api/demo/leaderboard`)).text();
  assert.equal(JSON.parse(demo).length,2);
  assert.doesNotMatch(demo,/ground_truth|truth_relationship/);
  const page=await(await fetch(`${base}/leaderboard?namespace=DEMO`)).text();
  assert.match(page,/Which AI follows evidence/);
  assert.equal((await fetch(`${base}/api/admin/publish-demo`,{method:'POST'})).status,401);
 }finally{await new Promise(resolve=>server.close(resolve));}
});
