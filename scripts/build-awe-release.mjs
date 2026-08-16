import { createHash } from "node:crypto";
import { cp, mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, resolve } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "packages", "awe-node");
const output = resolve(root, "public", "exchange");
const stagingRoot = await mkdtemp(resolve(tmpdir(), "agent-wex-release-"));
const staging = resolve(stagingRoot, "package");

try {
  await cp(source, staging, { recursive: true });
  await cp(resolve(root, "LICENSE"), resolve(staging, "LICENSE"));
  const manifest = JSON.parse(await readFile(resolve(staging, "package.json"), "utf8"));
  const expectedName = `awe-node-${manifest.version}.tgz`;
  const { stdout } = await execFileAsync("npm", ["pack", "--json"], { cwd: staging });
  const packed = JSON.parse(stdout)[0];
  await mkdir(output, { recursive: true });
  const destination = resolve(output, expectedName);
  await cp(resolve(staging, packed.filename), destination);
  const bytes = await readFile(destination);
  const sha256 = createHash("sha256").update(bytes).digest("hex");
  await writeFile(resolve(output, "SHA256SUMS"), `${sha256}  ${expectedName}\n`);
  await writeFile(resolve(output, "release.json"), `${JSON.stringify({
    package: manifest.name,
    version: manifest.version,
    filename: expectedName,
    sha256,
    size: bytes.byteLength,
    node: manifest.engines.node,
    dependencies: 0,
    lifecycleScripts: false,
    source: manifest.repository.url,
  }, null, 2)}\n`);
  process.stdout.write(`${basename(destination)} ${sha256}\n`);
} finally {
  await rm(stagingRoot, { recursive: true, force: true });
}
