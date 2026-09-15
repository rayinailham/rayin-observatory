// Deterministic lifecycle tests: exercise the production class with a controlled audio clock.
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
const require = createRequire(new URL('../package.json', import.meta.url));
const ts = require('typescript');
const compiled = ts.transpileModule(readFileSync(new URL('../lib/ambient.ts', import.meta.url), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const contexts = [];
class Param {
  value = 0;
  setValueAtTime(v) { this.value = v; }
  linearRampToValueAtTime(v) { this.value = v; }
  exponentialRampToValueAtTime(v) { this.value = v; }
  cancelScheduledValues() {}
  setTargetAtTime(v) { this.value = v; }
}
class Node {
  gain = new Param(); frequency = new Param(); disconnected = false; stopped = false;
  connect(node) { return node; }
  disconnect() { this.disconnected = true; }
  start() {}
  stop(time) { if (time === undefined) this.stopped = true; }
}
class Context {
  state = 'suspended'; currentTime = 0; destination = {}; nodes = []; resumes = [];
  constructor() { contexts.push(this); }
  createGain() { const n = new Node(); this.nodes.push(n); return n; }
  createOscillator() { const n = new Node(); this.nodes.push(n); return n; }
  resume() { return new Promise(resolve => this.resumes.push(() => { this.state = 'running'; resolve(); })); }
  close() { this.state = 'closed'; return Promise.resolve(); }
}
const document = { hidden: false };
const sandbox = { exports: {}, AudioContext: Context, document };
vm.runInNewContext(compiled, sandbox);
const Audio = sandbox.exports.ObservatoryAudio;
const checks = [];
const engine = new Audio();
await engine.setEnabled(false);
engine.click(); engine.transition('in');
assert.equal(contexts.length, 0); checks.push('Silent entry never creates AudioContext');
const pending = engine.setEnabled(true), context = contexts[0];
await engine.setEnabled(false);
context.resumes.shift()();
assert.equal(await pending, false);
assert.equal(engine.master.gain.value, 0); checks.push('Late resume cannot override mute');
const enabling = engine.setEnabled(true); context.resumes.shift()(); await enabling;
for (let i = 0; i < 100; i++) engine.click(i % 5);
assert.equal(engine.voices.size, 1); checks.push('Rapid repeated clicks are rate limited');
for (let i = 0; i < 20; i++) { context.currentTime += .1; engine.click(i % 5); }
assert.equal(engine.voices.size, 6); checks.push('Concurrent one-shot voices capped at six');
const old = [...engine.voices.entries()]; engine.transition('in');
assert.equal(engine.voices.size, 2);
assert(old.every(([source, gain]) => source.stopped && source.disconnected && gain.disconnected));
checks.push('Transition replaces previous voices and disconnects nodes');
document.hidden = true; engine.visibilityChanged();
assert.equal(engine.voices.size, 0); assert.equal(engine.master.gain.value, 0);
engine.click(); engine.transition('out'); assert.equal(engine.voices.size, 0);
checks.push('Hidden tab cancels effects, silences master, rejects new effects');
document.hidden = false; engine.visibilityChanged(); assert.equal(engine.master.gain.value, 1);
engine.transition('out'); const [source, gain] = [...engine.voices.entries()][0];
source.onended(); assert.equal(engine.voices.size, 1); assert(source.disconnected && gain.disconnected);
checks.push('Completed one-shot disconnects itself');
const playing = [...engine.voices.keys()]; engine.dispose();
assert.equal(context.state, 'closed'); assert.equal(engine.voices.size, 0);
assert(playing.every(source => source.stopped)); engine.click(); assert.equal(contexts.length, 1);
checks.push('Dispose closes context and stops sources; later clicks stay silent');
const second = new Audio(); const waiting = second.setEnabled(true); const secondContext = contexts[1];
second.dispose(); secondContext.resumes.shift()(); assert.equal(await waiting, false);
checks.push('Dispose invalidates pending resume');
const out = fileURLToPath(new URL('../../assets/renders/showpiece/dev/', import.meta.url));
mkdirSync(out, { recursive: true });
writeFileSync(out + 'audio-verification.json', JSON.stringify({ status: 'passed', checks }, null, 2) + '\n');
console.log(`PASS ${checks.length} audio lifecycle checks`);
