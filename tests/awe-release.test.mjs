import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("public node release is checksummed and declares no runtime dependencies or lifecycle scripts", async () => {
  const root = new URL("../public/exchange/", import.meta.url);
  const release = JSON.parse(await readFile(new URL("release.json", root), "utf8"));
  const manifest = JSON.parse(await readFile(new URL("agent.json", root), "utf8"));
  const bytes = await readFile(new URL(release.filename, root));
  const checksum = createHash("sha256").update(bytes).digest("hex");
  const sums = await readFile(new URL("SHA256SUMS", root), "utf8");
  assert.equal(release.version, "0.6.0");
  assert.equal(checksum, release.sha256);
  assert.equal(sums, `${checksum}  ${release.filename}\n`);
  assert.equal(release.dependencies, 0);
  assert.equal(release.lifecycleScripts, false);
  assert.equal(manifest.distribution.directPackageSha256, checksum);
  assert.ok(manifest.distribution.directPackageUrl.endsWith(release.filename));
});
