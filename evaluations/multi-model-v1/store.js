import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { TABLES } from './src/domain/constants.js';
import { hashObject } from './src/lib/hash.js';
const deepFreeze=(value)=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.freeze(value);for(const child of Object.values(value))deepFreeze(child);}return value;};
const emptyState=()=>Object.fromEntries(TABLES.map(table=>[table,[]]));
export class JsonStore{
 constructor(path){this.path=path;this.state=emptyState();this.loaded=false;this.persistChain=Promise.resolve();}
 async load(){if(this.loaded)return this;try{this.state=JSON.parse(await readFile(this.path,'utf8'));}catch(error){if(error.code!=='ENOENT')throw error;}for(const table of TABLES){this.state[table]??=[];this.state[table]=this.state[table].map(deepFreeze);}this.loaded=true;return this;}
 all(table){if(!TABLES.includes(table))throw new Error(`Unknown table ${table}`);return[...this.state[table]];}
 find(table,predicate){return this.state[table].find(predicate);}
 filter(table,predicate){return this.state[table].filter(predicate);}
 async insert(table,record,{idField='id'}={}){if(!TABLES.includes(table))throw new Error(`Unknown table ${table}`);const copy=structuredClone(record);const frozen=deepFreeze({...copy,record_hash:copy.record_hash??hashObject(copy)});if(idField&&frozen[idField]!==undefined&&this.state[table].some(item=>item[idField]===frozen[idField]))throw new Error(`Immutable duplicate ${table}.${idField}=${frozen[idField]}`);this.state[table].push(frozen);await this.persist();return frozen;}
 async insertIfAbsent(table,record,options){const idField=options?.idField??'id';return this.state[table].find(item=>item[idField]===record[idField])??this.insert(table,record,{idField});}
 async persist(){const write=async()=>{await mkdir(dirname(this.path),{recursive:true});const temporary=`${this.path}.next`;await writeFile(temporary,`${JSON.stringify(this.state,null,2)}\n`,{mode:0o600});await rename(temporary,this.path);};this.persistChain=this.persistChain.then(write,write);return this.persistChain;}
 snapshotHash(){return hashObject(this.state);}
}
