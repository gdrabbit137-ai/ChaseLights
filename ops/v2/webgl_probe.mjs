#!/usr/bin/env node
// CL-CI-39: record what the headless Chromium in CI can actually do with WebGL.
//
// Three map-dependent browser tests (CL-UI-106, CL-UI-118b, CL-APP-06) fail only
// in CI. Before treating that as a product defect, the gate must show whether
// the runner has a usable WebGL context at all — a headless Chromium without a
// GPU or a software rasteriser reports `getContext('webgl') === null`, and every
// MapLibre-backed assertion downstream of that is meaningless.
//
// The probe is informational: it never fails the build, it writes one line to
// stdout (and the job summary when $GITHUB_STEP_SUMMARY is set) so the verdict is
// evidence-backed instead of assumed.
import {spawnSync} from 'node:child_process';
import {appendFileSync} from 'node:fs';

const BROWSER = process.env.CHROMIUM_EXECUTABLE || 'chromium';
const page = `<!doctype html><meta charset="utf-8"><body><pre id="out">pending</pre>
<script>
(function(){
  const out = document.getElementById('out');
  let row = {ok:false, vendor:null, renderer:null, error:null};
  try {
    const c = document.createElement('canvas');
    const gl = c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl');
    if (!gl) {
      row.error = 'getContext returned null';
    } else {
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      row.ok = true;
      row.vendor = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR);
      row.renderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      row.version = gl.getParameter(gl.VERSION);
    }
  } catch (e) { row.error = String(e && e.message || e); }
  out.textContent = 'WEBGL_PROBE ' + JSON.stringify(row);
})();
</script>`;

const url = 'data:text/html;base64,' + Buffer.from(page, 'utf8').toString('base64');
const args = ['--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
              '--no-first-run', '--dump-dom', url];
const run = spawnSync(BROWSER, args, {encoding: 'utf8', timeout: 60000});
const output = (run.stdout || '') + (run.stderr || '');
const match = output.match(/WEBGL_PROBE (\{.*?\})/);
let line;
if (!match) {
  line = 'WEBGL_PROBE {"ok":null,"error":"probe did not run: ' +
    (run.error ? run.error.message : 'no marker in chrome output').replace(/"/g, "'") + '"}';
} else {
  let parsed;
  try { parsed = JSON.parse(match[1]); } catch { parsed = {ok: null, error: 'unparsable probe payload'}; }
  line = 'WEBGL_PROBE ' + JSON.stringify(parsed);
}
console.log(line);
if (process.env.GITHUB_STEP_SUMMARY) {
  appendFileSync(process.env.GITHUB_STEP_SUMMARY, '\n### Headless Chromium WebGL probe (CL-CI-39)\n\n```\n' + line + '\n```\n');
}
process.exit(0); // informational only — never gated
