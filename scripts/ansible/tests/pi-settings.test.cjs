const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "../../..");
const template = fs.readFileSync(path.join(root, "run_after_merge-pi-settings.js.tmpl"), "utf8");
const fragment = fs.readFileSync(path.join(root, ".chezmoitemplates/pi/settings.json"), "utf8");

function fixture(t, existing, managed = fragment) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "pi-settings-test-"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const target = path.join(dir, "destination");
  const agent = path.join(target, ".pi", "agent");
  fs.mkdirSync(agent, { recursive: true });
  const settings = path.join(agent, "settings.json");
  if (existing !== undefined) fs.writeFileSync(settings, existing);
  const rendered = template
    .replace('{{ include ".chezmoitemplates/pi/settings.json" | quote }}', () => JSON.stringify(managed))
    .replace('{{ .chezmoi.destDir | quote }}', () => JSON.stringify(target));
  assert.ok(!rendered.includes("{{"), "all hook template fields must be rendered");
  const script = path.join(dir, "merge.cjs");
  fs.writeFileSync(script, rendered);
  const home = path.join(dir, "unrelated-home");
  fs.mkdirSync(home);
  const run = () => spawnSync(process.execPath, [script], {
    encoding: "utf8", env: { ...process.env, HOME: home, USERPROFILE: home },
  });
  return { run, settings, agent, home, dir, script };
}

test("creates managed settings at the destination, not HOME", t => {
  const f = fixture(t);
  assert.equal(f.run().status, 0);
  assert.deepEqual(JSON.parse(fs.readFileSync(f.settings)), JSON.parse(fragment));
  assert.deepEqual(fs.readdirSync(f.home), []);
  if (process.platform !== "win32") assert.equal(fs.statSync(f.settings).mode & 0o777, 0o600);
});

test("preserves local preferences and nested unowned subagents keys", t => {
  const f = fixture(t, JSON.stringify({ theme: "local", lastChangelogVersion: "local", extensions: ["local"],
    defaultModel: "old", subagents: { defaultModel: "old", concurrency: 2 } }));
  assert.equal(f.run().status, 0);
  const actual = JSON.parse(fs.readFileSync(f.settings));
  assert.equal(actual.theme, "local");
  assert.equal(actual.lastChangelogVersion, "local");
  assert.deepEqual(actual.extensions, ["local"]);
  assert.equal(actual.defaultModel, JSON.parse(fragment).defaultModel);
  assert.equal(actual.subagents.concurrency, 2);
  assert.equal(actual.subagents.defaultModel, JSON.parse(fragment).subagents.defaultModel);
});

test("repeat run does not rewrite unchanged settings", t => {
  const f = fixture(t);
  assert.equal(f.run().status, 0);
  const before = fs.statSync(f.settings);
  assert.equal(f.run().status, 0);
  assert.equal(fs.statSync(f.settings).mtimeMs, before.mtimeMs);
  assert.deepEqual(fs.readdirSync(f.agent), ["settings.json"]);
});

for (const invalid of ['{private-invalid-json', 'null', '[]', '42', '{"subagents":null}', '{"subagents":[]}']) {
  test(`rejects invalid existing settings (${invalid.slice(0, 12)}) without writes or data in errors`, t => {
    const f = fixture(t, invalid);
    const result = f.run();
    assert.equal(result.status, 1);
    assert.equal(fs.readFileSync(f.settings, "utf8"), invalid);
    assert.ok(!result.stderr.includes("private-invalid-json"));
    assert.deepEqual(fs.readdirSync(f.agent), ["settings.json"]);
  });
}

test("rejects invalid managed JSON without modifying the original", t => {
  const original = '{"theme":"local"}';
  const f = fixture(t, original, "not-json");
  assert.equal(f.run().status, 1);
  assert.equal(fs.readFileSync(f.settings, "utf8"), original);
});

test("write failure preserves settings and removes temporary output", t => {
  const original = '{"theme":"local"}';
  const f = fixture(t, original);
  // Inject at the filesystem boundary rather than rely on root/Windows ACLs.
  const injected = 'fs.renameSync = () => { const e = new Error("injected"); e.code = "EACCES"; throw e; };\n';
  fs.writeFileSync(f.script, fs.readFileSync(f.script, "utf8").replace('const path = require("node:path");', injected + 'const path = require("node:path");'));
  assert.equal(f.run().status, 1);
  assert.equal(fs.readFileSync(f.settings, "utf8"), original);
  assert.deepEqual(fs.readdirSync(f.agent), ["settings.json"]);
});

test("preserves a concurrent settings update", t => {
  const f = fixture(t, '{"theme":"old"}');
  const injected = 'const originalWrite = fs.writeFileSync; fs.writeFileSync = (...args) => { originalWrite(...args); originalWrite(settingsPath, \'{"theme":"concurrent"}\'); };\n';
  fs.writeFileSync(f.script, fs.readFileSync(f.script, "utf8").replace('const path = require("node:path");', injected + 'const path = require("node:path");'));
  assert.equal(f.run().status, 1);
  assert.equal(JSON.parse(fs.readFileSync(f.settings)).theme, "concurrent");
  assert.deepEqual(fs.readdirSync(f.agent), ["settings.json"]);
});

test("rejects symlink settings and parent directories", { skip: process.platform === "win32" }, t => {
  const f = fixture(t);
  const external = path.join(f.dir, "external.json");
  fs.writeFileSync(external, '{"theme":"outside"}');
  fs.symlinkSync(external, f.settings);
  assert.equal(f.run().status, 1);
  assert.equal(JSON.parse(fs.readFileSync(external)).theme, "outside");
  fs.unlinkSync(f.settings);
  fs.rmSync(f.agent, { recursive: true });
  const externalDir = path.join(f.dir, "external-dir");
  fs.mkdirSync(externalDir);
  fs.symlinkSync(externalDir, f.agent);
  assert.equal(f.run().status, 1);
  assert.deepEqual(fs.readdirSync(externalDir), []);
});

test("rejects a non-file settings destination", t => {
  const f = fixture(t);
  fs.mkdirSync(f.settings);
  assert.equal(f.run().status, 1);
  assert.ok(fs.statSync(f.settings).isDirectory());
});
