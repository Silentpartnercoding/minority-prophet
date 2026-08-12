import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { developmentBenchmark } from './benchmark.js';
import { publishArtifacts } from './artifacts.js';
import { runBenchmark } from './pipeline.js';
import { DeterministicAdapter } from './providers.js';
import { JsonStore } from './store.js';
import { verifyRun } from './verifier.js';

test('publication creates research artifacts without hidden worlds',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'mp-artifacts-'));
 const store=await new JsonStore(join(dir,'state.json')).load();
 const run=await runBenchmark({store,benchmark:developmentBenchmark({count:1}),adapters:[new DeterministicAdapter('majority-follower-v1')],runId:'artifact-run'});
 await verifyRun(store,run.id);
 const output=join(dir,'published');
 const snapshot=await publishArtifacts(store,output,'DEMO');
 assert.equal(snapshot.rows.length,1);
 for(const name of ['methodology.json','benchmark-manifest.json','results.json','results.csv','statistical-summary.json','leaderboard-snapshot.json','reproducibility.json','plots.json','publication-table.md']){
  const content=await readFile(join(output,name),'utf8');
  assert.ok(content.length>1,name);
  assert.doesNotMatch(content,/truth_relationship|ground_truth/);
 }
});

test('publication can be pinned to one exact run',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'mp-artifacts-pinned-'));
 const store=await new JsonStore(join(dir,'state.json')).load();
 const benchmark=developmentBenchmark({count:1});
 const adapter=new DeterministicAdapter('majority-follower-v1');
 const first=await runBenchmark({store,benchmark,adapters:[adapter],runId:'first-run'});
 const second=await runBenchmark({store,benchmark,adapters:[adapter],runId:'second-run'});
 await verifyRun(store,first.id); await verifyRun(store,second.id);
 const snapshot=await publishArtifacts(store,join(dir,'published'),'DEMO',{runIds:[second.id]});
 assert.deepEqual(snapshot.run_ids,[second.id]);
 assert.ok(snapshot.rows.every((row)=>row.run_id===second.id));
});
