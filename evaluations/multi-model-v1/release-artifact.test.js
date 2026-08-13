import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { buildRuntimeRelease } from './build-runtime-release.mjs';

test('release evidence is deterministic and package scope excludes evaluation material', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'mp-release-'));
  try {
    const first = await buildRuntimeRelease({ outputDirectory: join(directory, 'one'), allowDirtyForTest: true });
    const second = await buildRuntimeRelease({ outputDirectory: join(directory, 'two'), allowDirtyForTest: true });
    assert.equal(first.artifact.sha256, second.artifact.sha256);
    assert.equal(first.published, false);
    assert.equal(first.registry, null);
    assert.equal(first.source_tree_clean, false);
    assert.equal(first.packaged_files.includes('EVALUATION.md'), false);
    assert.equal(first.packaged_files.some((path) => /world|result|response/i.test(path)), false);
    const sbom = JSON.parse(await readFile(join(directory, 'one', 'sbom.spdx.json'), 'utf8'));
    assert.equal(sbom.spdxVersion, 'SPDX-2.3');
    assert.equal(sbom.packages[0].licenseDeclared, 'Apache-2.0');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
