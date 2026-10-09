// Render into disposable destinations. Never run repository provisioning hooks.
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const root = path.resolve(__dirname, "../../..");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "dotfiles-render-"));
const isolatedHome = path.join(temporary, "home");
fs.mkdirSync(isolatedHome);
const stateFlags = ["--cache", path.join(temporary, "cache"),
  "--persistent-state", path.join(temporary, "state.bbolt")];

function run(args, expected = [0]) {
  const result = spawnSync("chezmoi", [...args, ...stateFlags], {
    encoding: "utf8", timeout: 60000,
    env: { ...process.env, HOME: isolatedHome, USERPROFILE: isolatedHome,
      XDG_CONFIG_HOME: path.join(temporary, "config"),
      XDG_DATA_HOME: path.join(temporary, "data"), XDG_CACHE_HOME: path.join(temporary, "cache"),
      APPDATA: path.join(temporary, "appdata"), LOCALAPPDATA: path.join(temporary, "localappdata"),
      GIT_CONFIG_GLOBAL: process.platform === "win32" ? "NUL" : "/dev/null" },
  });
  if (!expected.includes(result.status)) {
    throw new Error(`chezmoi ${args[0]} failed (${result.status}): ${result.stderr}`);
  }
  return result.stdout;
}

try {
  const source = path.join(temporary, "source");
  const destination = path.join(temporary, "destination");
  const config = path.join(temporary, "chezmoi.toml");
  const excluded = new Set([".git", ".pi", ".ansible", "__pycache__"]);
  fs.cpSync(root, source, { recursive: true, filter: p => !excluded.has(path.basename(p)) });
  fs.mkdirSync(destination);
  const flags = ["--source", source, "--destination", destination, "--config", config, "--no-tty", "--no-pager"];
  run(["init", ...flags]);
  run(["diff", ...flags, "--use-builtin-diff"], [0, 1]);
  const managed = run(["managed", ...flags]).replaceAll("\\", "/").split(/\r?\n/);
  for (const prefix of [".github", "docs", "openspec", "scripts/ansible/tests", ".pi/agent/settings.json"]) {
    assert.ok(!managed.some(p => p === prefix || p.startsWith(prefix + "/")), `${prefix} must not be deployed`);
  }
  assert.deepEqual(fs.readdirSync(destination), [], "rendering must not modify its destination");

  // Exercise the actual interpreter and rendered hook, but with a minimal source
  // so no other repository script or dotfile can be applied.
  const hookSource = path.join(temporary, "hook-source");
  fs.mkdirSync(path.join(hookSource, ".chezmoitemplates", "pi"), { recursive: true });
  for (const file of [".chezmoi.toml.tmpl", "run_after_merge-pi-settings.js.tmpl", ".chezmoitemplates/pi/settings.json"]) {
    fs.copyFileSync(path.join(root, file), path.join(hookSource, file));
  }
  const hookConfig = path.join(temporary, "hook.toml");
  const hookFlags = ["--source", hookSource, "--destination", destination, "--config", hookConfig, "--no-tty", "--no-pager"];
  run(["init", ...hookFlags]);
  const agent = path.join(destination, ".pi", "agent");
  fs.mkdirSync(agent, { recursive: true });
  fs.writeFileSync(path.join(agent, "settings.json"), '{"theme":"local-integration"}');
  run(["apply", ...hookFlags]);
  assert.equal(JSON.parse(fs.readFileSync(path.join(agent, "settings.json"))).theme, "local-integration");
  console.log(`PASS: isolated ${process.platform} rendering and actual Pi hook execution`);
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
