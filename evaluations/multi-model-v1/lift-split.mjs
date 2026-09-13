/**
 * Seal a confirmatory world set before anyone can look at it.
 *
 * v1.1's own interpretation boundary names the reason this file exists: the
 * worlds are synthetic and were designed alongside the deterministic analysis,
 * and v1.0 outcomes on those same worlds were known before the replication.
 * A result on worlds whose outcomes you have already seen is a development
 * result, whatever its p-value.
 *
 * The split is deterministic and committed, not chosen. Every world id is
 * hashed with a salt fixed at seal time; the low bit of that digest assigns it.
 * Nobody picks which worlds are hidden, and the assignment can be recomputed by
 * anyone holding the salt and the generator seed.
 *
 * The development set is written in full. The confirmatory set is written as
 * ids and a set digest only. Its contents are never emitted here, so inspecting
 * this repository does not contaminate it.
 *
 *   node evaluations/multi-model-v1/lift-split.mjs --repetitions 24 --salt <hex>
 */

import { createHash, randomBytes } from 'node:crypto';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { generateLiftWorlds, LIFT_SCENARIO_FAMILIES } from './lift-worlds.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(HERE, 'lift-v12');

function parseArgs(argv) {
  const args = { repetitions: 24, seed: 1_730_000, salt: null };
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i]?.replace(/^--/, '');
    const value = argv[i + 1];
    if (key === 'repetitions' || key === 'seed') args[key] = Number(value);
    else if (key === 'salt') args.salt = value;
  }
  if (!Number.isInteger(args.repetitions) || args.repetitions < 1) {
    throw new Error('--repetitions must be a positive integer');
  }
  return args;
}

function digest(value) {
  return createHash('sha256').update(value).digest('hex');
}

/** Deterministic, unbiased-by-construction assignment. */
function assign(worldId, salt) {
  const h = digest(`${salt}:${worldId}`);
  return parseInt(h.slice(-1), 16) % 2 === 0 ? 'development' : 'confirmatory';
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const salt = args.salt ?? randomBytes(16).toString('hex');
  const saltWasGenerated = !args.salt;

  const worlds = generateLiftWorlds({ repetitions: args.repetitions, seed: args.seed });
  const development = [];
  const confirmatory = [];
  for (const world of worlds) {
    const id = world.world_id ?? world.id;
    if (!id) throw new Error('a generated world has no id; cannot split reproducibly');
    (assign(id, salt) === 'development' ? development : confirmatory).push(world);
  }

  const idsOf = (set) => set.map((w) => w.world_id ?? w.id).sort();
  const setDigest = (set) => digest(idsOf(set).join('\n'));

  mkdirSync(OUT_DIR, { recursive: true });

  // The development set is emitted in full. Looking at it is allowed.
  writeFileSync(
    join(OUT_DIR, 'development-worlds.json'),
    `${JSON.stringify({ worlds: development }, null, 2)}\n`
  );

  // The confirmatory set is sealed: ids and digests only, never contents.
  const seal = {
    schema: 'minority-prophet.lift-split.v1',
    sealedAt: new Date().toISOString(),
    generator: { seed: args.seed, repetitions: args.repetitions },
    families: LIFT_SCENARIO_FAMILIES,
    salt,
    totals: {
      worlds: worlds.length,
      development: development.length,
      confirmatory: confirmatory.length
    },
    developmentDigest: setDigest(development),
    confirmatoryDigest: setDigest(confirmatory),
    confirmatoryIds: idsOf(confirmatory),
    note:
      'Confirmatory world CONTENTS are deliberately absent. Regenerate them ' +
      'from seed, repetitions and salt only at run time, and only once.'
  };
  writeFileSync(join(OUT_DIR, 'confirmatory-seal.json'), `${JSON.stringify(seal, null, 2)}\n`);

  console.log(`worlds generated:      ${worlds.length}`);
  console.log(`development (visible): ${development.length}`);
  console.log(`confirmatory (sealed): ${confirmatory.length}`);
  console.log(`development digest:    ${seal.developmentDigest}`);
  console.log(`confirmatory digest:   ${seal.confirmatoryDigest}`);
  if (saltWasGenerated) {
    console.log('\nA salt was generated for this seal. Commit the seal file before');
    console.log('any model call, or the split is not a commitment.');
  }
}

main();
