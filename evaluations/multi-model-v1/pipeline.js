import { CONDITIONS, RESULT_NAMESPACES } from './src/domain/constants.js';
import { persistBenchmark } from './benchmark.js';
import { recordId } from './run-ids.js';
import { runTrial } from './trial-runner.js';
import { costTelemetry, registerExperiment, scoreRun } from './pipeline-support.js';
export const DEFAULT_SETTINGS=Object.freeze({temperature:0,top_p:1,max_tokens:500,provider_concurrency:1,tool_configuration:{regime:'closed_world',allowed_tools:[],external_retrieval:false}});
export async function runBenchmark({store,benchmark,adapters,namespace=RESULT_NAMESPACES.DEMO,settings=DEFAULT_SETTINGS,runId}){
 await persistBenchmark(store,benchmark);
 const id=runId??recordId('run',{benchmark:benchmark.manifest.manifest_hash,models:adapters.map(a=>`${a.provider}:${a.model}:${a.version}`),settings,namespace});
 const done=store.find('benchmark_runs',r=>(r.logical_run_id??r.id)===id&&r.status==='COMPLETED');
 if(done)return done;
 const attempt=store.filter('benchmark_runs',r=>(r.logical_run_id??r.id)===id).length+1;
 await registerExperiment(store,id,benchmark,adapters);
 const errors=[];
 for(const adapter of adapters)for(const world of benchmark.worlds)for(const condition of [CONDITIONS.BASELINE,CONDITIONS.PROVENANCE,CONDITIONS.MINORITY_PROPHET])try{await runTrial({store,runId:id,adapter,world,condition,settings});}catch(error){errors.push({provider:adapter.provider,model:adapter.model,world_id:world.world_id,condition,message:error.message});}
 const trials=store.filter('trials',t=>t.run_id===id&&t.status==='COMPLETED');
 const common={logical_run_id:id,attempt,namespace,benchmark_version:benchmark.manifest.benchmark_version,benchmark_manifest_hash:benchmark.manifest.manifest_hash,expected_trials:benchmark.worlds.length*adapters.length*3,completed_trials:trials.length,failed_trials:errors.length,models:adapters.map(a=>({provider:a.provider,model:a.model,version:a.version})),settings,cost_telemetry:{...costTelemetry(trials,benchmark.worlds.length),failures:errors.length},created_at:new Date().toISOString(),errors};
 if(errors.length)return store.insert('benchmark_runs',{id:`${id}:attempt:${attempt}`,status:'FAILED',...common});
 await scoreRun(store,id,adapters);
 return store.insert('benchmark_runs',{id,status:'COMPLETED',...common});
}
