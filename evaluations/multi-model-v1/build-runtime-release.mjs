#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { mkdir, readFile, realpath, rm, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const PACKAGE_DIRECTORY = fileURLToPath(new URL('.', import.meta.url));

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: 'utf8', ...options });
  if (result.status !== 0) throw new Error(`${command} failed: ${result.stderr || result.stdout}`);
  return result.stdout.trim();
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function sourceCommit() {
  return run('git', ['rev-parse', 'HEAD'], { cwd: PACKAGE_DIRECTORY });
}

function sourceIsClean() {
  return run('git', ['status', '--porcelain', '--untracked-files=all'], { cwd: PACKAGE_DIRECTORY }) === '';
}

function sourceCreatedAt() {
  if (process.env.SOURCE_DATE_EPOCH) {
    const value = Number(process.env.SOURCE_DATE_EPOCH);
    if (!Number.isInteger(value) || value < 0) throw new Error('SOURCE_DATE_EPOCH must be a non-negative integer');
    return new Date(value * 1000).toISOString();
  }
  return new Date(run('git', ['show', '-s', '--format=%ct', 'HEAD'], { cwd: PACKAGE_DIRECTORY }) * 1000).toISOString();
}

export async function buildRuntimeRelease({
  outputDirectory = resolve(PACKAGE_DIRECTORY, 'dist/runtime-release'),
  allowDirtyForTest = false,
} = {}) {
  if (!allowDirtyForTest && !sourceIsClean()) {
    throw new Error('refusing release evidence from a dirty working tree; commit and verify the exact source first');
  }
  const output = resolve(outputDirectory);
  await rm(output, { recursive: true, force: true });
  await mkdir(output, { recursive: true });
  const manifest = JSON.parse(await readFile(resolve(PACKAGE_DIRECTORY, 'package.json'), 'utf8'));
  const packed = JSON.parse(run('npm', ['pack', '--json', '--pack-destination', output], { cwd: PACKAGE_DIRECTORY }));
  if (!Array.isArray(packed) || packed.length !== 1) throw new Error('npm pack returned an unexpected result');
  const record = packed[0];
  const archiveName = basename(record.filename);
  const archive = await readFile(resolve(output, archiveName));
  const archiveSha256 = sha256(archive);
  const automatic = new Set(['package.json', 'README.md', 'LICENSE']);
  const declared = new Set([...automatic, ...(manifest.files ?? [])]);
  const actual = (record.files ?? []).map((item) => item.path).sort();
  const unexpected = actual.filter((path) => !declared.has(path));
  const missing = [...declared].filter((path) => !actual.includes(path)).sort();
  if (unexpected.length || missing.length) {
    throw new Error(`runtime package scope mismatch: unexpected=${unexpected.join(',')} missing=${missing.join(',')}`);
  }
  const commit = sourceCommit();
  const createdAt = sourceCreatedAt();
  const evidence = {
    schema: 'minority-prophet.runtime-release-evidence.v1',
    package: manifest.name,
    version: manifest.version,
    source_commit: commit,
    source_tree_clean: !allowDirtyForTest,
    created_at: createdAt,
    published: false,
    registry: null,
    artifact: { filename: archiveName, sha256: archiveSha256, bytes: archive.length },
    packaged_files: actual,
    excluded_classes: ['benchmark_worlds', 'model_responses', 'ground_truth_labels', 'leaderboard_results', 'provider_credentials'],
  };
  const namespace = `https://minorityprophet.org/spdx/engine/${manifest.version}/${archiveSha256}`;
  const sbom = {
    spdxVersion: 'SPDX-2.3',
    dataLicense: 'CC0-1.0',
    SPDXID: 'SPDXRef-DOCUMENT',
    name: `${manifest.name}-${manifest.version}`,
    documentNamespace: namespace,
    creationInfo: { created: createdAt, creators: ['Tool: minority-prophet-build-runtime-release'] },
    packages: [{
      name: manifest.name,
      SPDXID: 'SPDXRef-Package',
      versionInfo: manifest.version,
      downloadLocation: 'NOASSERTION',
      filesAnalyzed: false,
      licenseConcluded: 'Apache-2.0',
      licenseDeclared: 'Apache-2.0',
      checksums: [{ algorithm: 'SHA256', checksumValue: archiveSha256 }],
      externalRefs: [{
        referenceCategory: 'PACKAGE-MANAGER',
        referenceType: 'purl',
        referenceLocator: `pkg:npm/${encodeURIComponent(manifest.name)}@${manifest.version}`,
      }],
    }],
    relationships: [{ spdxElementId: 'SPDXRef-DOCUMENT', relationshipType: 'DESCRIBES', relatedSpdxElement: 'SPDXRef-Package' }],
  };
  await writeFile(resolve(output, 'release-evidence.json'), `${JSON.stringify(evidence, null, 2)}\n`);
  await writeFile(resolve(output, 'sbom.spdx.json'), `${JSON.stringify(sbom, null, 2)}\n`);
  await writeFile(resolve(output, 'SHA256SUMS'), `${archiveSha256}  ${archiveName}\n`);
  return evidence;
}

async function invokedDirectly() {
  if (!process.argv[1]) return false;
  try { return await realpath(fileURLToPath(import.meta.url)) === await realpath(process.argv[1]); }
  catch { return false; }
}

if (await invokedDirectly()) {
  const outputDirectory = process.argv[2] ? resolve(process.argv[2]) : undefined;
  process.stdout.write(`${JSON.stringify(await buildRuntimeRelease({ outputDirectory }), null, 2)}\n`);
}
