// CL-WG-16: WeatherGrid PNG prerender generator.
//
// Rasterises published WeatherGrid browser bundles into per-layer, per-frame
// transparent PNGs using THE SAME palette module the browser draws with
// (assets/weather-map-palette.js) — the honest-rule single source. PNG pixels
// are a Web Mercator-aligned rect covering the bundle bbox: x is linear in
// longitude and the row pitch is linear in Mercator y, so the frontend can
// drawImage the frame over the projected bbox corners with no resampling
// beyond the browser's bilinear filter (identical geometry to the existing
// smooth-field path, but exact in Mercator y).
//
// Per-cell color = colorFor(value, cfg); per-cell alpha = cellOpacityFor(...)
// baked in. The live layer opacity slider and the cloud 78% cap are applied
// at draw time (ctx.globalAlpha), so the committed PNG stays slider-neutral.
// Cells with missing values stay fully transparent, exactly like the
// smooth-field path's transparent holes.
//
// Usage:
//   node scripts/weathergrid_png_prerender.mjs --out weathergrid/png \
//     region=tw,source=gfs,bundle=weathergrid/gfs_tw_weather_browser.json \
//     region=tw,source=icon,bundle=weathergrid/icon_tw_cloud_browser.json \
//     [--layers total_cloud_percent,low_cloud_percent,visibility_km] \
//     [--max-frames N]
//
// Writes weathergrid/png/<region>/<source>/<layer>/f<NNN>.png and one
// weathergrid/png/<region>/manifest.json per region (aggregating every spec
// for that region; sources absent from this run keep previously published
// entries so a partial CI run never blanks the frontend).
//
// NOTE: this script originally lived at tools/weathergrid_png_prerender.mjs,
// but the tools/ directory became access-denied on this Windows host
// (OS-level ACL; content identical). scripts/ is the canonical location.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import palette from '../assets/weather-map-palette.js';

// palette module is a UMD classic script; the default import above resolves
// module.exports. Guard against accidental ESM-only breakage:
if (!palette || !palette.PALETTE_VERSION) {
  throw new Error('weather-map-palette.js did not export the palette API');
}

const DEFAULT_LAYERS = ['total_cloud_percent', 'low_cloud_percent', 'visibility_km'];
const PACKED_NULL_SENTINEL = -32768;

function parseArgs(argv) {
  const args = { specs: [], layers: DEFAULT_LAYERS, out: null, maxFrames: Infinity };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') args.out = argv[++i];
    else if (a.startsWith('--out=')) args.out = a.slice(6);
    else if (a === '--layers') args.layers = String(argv[++i] || '').split(',').filter(Boolean);
    else if (a.startsWith('--layers=')) args.layers = a.slice(9).split(',').filter(Boolean);
    else if (a === '--max-frames') args.maxFrames = Number(argv[++i]) || Infinity;
    else if (a.startsWith('--max-frames=')) args.maxFrames = Number(a.slice(13)) || Infinity;
    else args.specs.push(a);
  }
  if (!args.out) throw new Error('--out=<dir> is required');
  if (!args.specs.length) throw new Error('at least one region=..,source=..,bundle=.. spec is required');
  return args;
}

function parseSpec(spec) {
  const kv = {};
  for (const part of spec.split(',')) {
    const [k, v] = part.split('=');
    if (!k || !v) throw new Error(`bad spec fragment "${part}" in "${spec}"`);
    kv[k.trim()] = v.trim();
  }
  for (const k of ['region', 'source', 'bundle']) {
    if (!kv[k]) throw new Error(`spec "${spec}" is missing ${k}=`);
  }
  return kv;
}

// Packed bundle hydration (bundle_encoding "i16gz-v1") — mirrors the browser's
// hydratePackedBundle: base64(gzip(int16 LE)), sentinel -32768 => null.
function decodePackedField(entry) {
  const bytes = Buffer.from(entry.data, 'base64');
  const buf = zlib.gunzipSync(bytes);
  const ints = new Int16Array(buf.buffer, buf.byteOffset, buf.byteLength / 2);
  const out = new Array(ints.length);
  for (let i = 0; i < ints.length; i++) {
    out[i] = ints[i] === PACKED_NULL_SENTINEL ? null : ints[i];
  }
  return out;
}

function hydrateBundle(bundle) {
  if (!bundle || bundle.bundle_encoding !== 'i16gz-v1') return bundle;
  const out = structuredClone(bundle);
  delete out.bundle_encoding;
  for (const frame of out.frames || []) {
    const values = frame.values || {};
    const hydrated = {};
    for (const [key, entry] of Object.entries(values)) {
      if (entry && (entry.enc === 'i16gz' || entry.encoding === 'i16gz') && typeof entry.data === 'string') {
        hydrated[key] = decodePackedField(entry);
      } else {
        hydrated[key] = entry;
      }
    }
    frame.values = hydrated;
  }
  return out;
}

// Standard CSS hsl() -> 8-bit RGB, the same conversion the browser canvas
// applies when the smooth-field path rasterises colorFor() strings.
function hslToRgb(h, sPercent, lPercent) {
  const s = sPercent / 100, l = lPercent / 100;
  const k = n => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const to255 = x => Math.round(255 * x);
  return [to255(f(0)), to255(f(8)), to255(f(4))];
}

function cssColorToRgb(css) {
  let m = /hsl\(\s*([-\d.]+)(?:deg)?\s+([\d.]+)%\s+([\d.]+)%\s*\)/.exec(css);
  if (m) return hslToRgb(Number(m[1]), Number(m[2]), Number(m[3]));
  m = /rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)/.exec(css);
  if (m) return [Number(m[1]), Number(m[2]), Number(m[3])];
  throw new Error(`unsupported color string: ${css}`);
}

// Minimal PNG writer: 8-bit RGBA, no filtering (filter byte 0 per row),
// zlib deflate. Fully deterministic output bytes.
function writePng(width, height, rgba) {
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++) {
    const rowStart = y * (width * 4 + 1);
    raw[rowStart] = 0; // filter: none
    rgba.copy(raw, rowStart + 1, y * width * 4, (y + 1) * width * 4);
  }
  const idat = zlib.deflateSync(raw, { level: 9 });
  const chunk = (type, data) => {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length);
    const typeBuf = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])) >>> 0);
    return Buffer.concat([len, typeBuf, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;  // bit depth
  ihdr[9] = 6;  // color type RGBA
  ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

let CRC_TABLE = null;
function crc32(buf) {
  if (!CRC_TABLE) {
    CRC_TABLE = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      CRC_TABLE[n] = c;
    }
  }
  let crc = -1;
  for (let i = 0; i < buf.length; i++) crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ buf[i]) & 0xff];
  return ~crc;
}

// Rasterise one frame/layer into a cols x rows RGBA buffer whose pixel rows
// run north->south (PNG convention), regardless of the bundle's latitude order.
// Applies the same decodeValue semantics as the browser: encoded * scale,
// wrapped into [0, wrap) when the field declares wrap.
function rasterizeFrame(values, rows, cols, cfg, meta = {}) {
  const scale = Number.isFinite(meta.scale) ? meta.scale : 1;
  const wrap = Number.isFinite(meta.wrap) ? meta.wrap : null;
  const decode = v => {
    if (v == null || !Number.isFinite(v)) return null;
    let x = v * scale;
    if (wrap) x = ((x % wrap) + wrap) % wrap;
    return x;
  };
  const rgba = Buffer.alloc(rows * cols * 4);
  // colorFor/cellOpacityFor depend only on the value; memoise per distinct value.
  const colorCache = new Map();
  const rgbaFor = value => {
    let hit = colorCache.get(value);
    if (hit) return hit;
    const css = palette.colorFor(value, cfg);
    const [r, g, b] = cssColorToRgb(css);
    const alpha = Math.max(0, Math.min(1, palette.cellOpacityFor(value, cfg)));
    hit = [r, g, b, Math.round(alpha * 255)];
    colorCache.set(value, hit);
    return hit;
  };
  const ascendingLat = true; // bundle latitudes ascend (row 0 = south) for these products
  for (let py = 0; py < rows; py++) {
    const r = ascendingLat ? rows - 1 - py : py;
    for (let c = 0; c < cols; c++) {
      const v = decode(values[r * cols + c]);
      if (v == null) continue; // transparent hole
      const [rr, gg, bb, aa] = rgbaFor(v);
      if (aa === 0) continue;
      const o = (py * cols + c) * 4;
      rgba[o] = rr; rgba[o + 1] = gg; rgba[o + 2] = bb; rgba[o + 3] = aa;
    }
  }
  return rgba;
}

function latitudesFor(bbox, rows, cols) {
  const latStep = (bbox.toplat - bbox.bottomlat) / (rows - 1);
  const lonStep = (bbox.rightlon - bbox.leftlon) / (cols - 1);
  const lats = [], lons = [];
  for (let i = 0; i < rows; i++) lats.push(Number((bbox.bottomlat + i * latStep).toFixed(6)));
  for (let i = 0; i < cols; i++) lons.push(Number((bbox.leftlon + i * lonStep).toFixed(6)));
  return { lats, lons };
}

function fieldMeta(fields, key) {
  const meta = fields?.[key];
  if (!meta) return null;
  const out = {};
  if (Number.isFinite(meta.scale)) out.scale = meta.scale;
  if (Number.isFinite(meta.wrap)) out.wrap = meta.wrap;
  return out;
}

function processSpec(spec, args) {
  const bundlePath = spec.bundle;
  if (!fs.existsSync(bundlePath)) {
    // A source may legitimately be absent from this run (e.g. CWA/jma not
    // published); skip it instead of failing the whole snapshot publish.
    console.warn(`skip ${spec.region}/${spec.source}: bundle not found: ${bundlePath}`);
    return { spec, sourceEntry: null, written: [] };
  }
  const raw = JSON.parse(fs.readFileSync(bundlePath, 'utf8'));
  const bundle = hydrateBundle(raw);
  const rows = bundle.grid?.rows, cols = bundle.grid?.cols;
  if (!rows || !cols || !bundle.frames?.length) {
    throw new Error(`${bundlePath}: not a browser bundle (missing grid/frames)`);
  }
  // If the bundle carries explicit axes, trust them; else derive from bbox.
  let lats = bundle.grid.latitudes, lons = bundle.grid.longitudes;
  if (!Array.isArray(lats) || lats.length !== rows) {
    lats = latitudesFor(bundle.bbox, rows, cols).lats;
  }
  if (!Array.isArray(lons) || lons.length !== cols) {
    lons = latitudesFor(bundle.bbox, rows, cols).lons;
  }
  const frames = bundle.frames.slice(0, args.maxFrames === Infinity ? undefined : args.maxFrames);
  const outDir = path.join(args.out, spec.region, spec.source);
  const layerEntries = {};
  const written = [];
  for (const key of args.layers) {
    const cfg = palette.LAYER_RENDER_CONFIG[key];
    if (!cfg) throw new Error(`no LAYER_RENDER_CONFIG for layer ${key}`);
    const present = Boolean(bundle.fields?.[key]);
    if (!present) { layerEntries[key] = { covered: false }; continue; }
    const layerDir = path.join(outDir, key);
    fs.mkdirSync(layerDir, { recursive: true });
    const frameList = [];
    frames.forEach((frame, idx) => {
      const values = frame.values?.[key];
      if (!Array.isArray(values) || values.length !== rows * cols) {
        // Frame without this field: skip honestly (manifest simply lacks it).
        return;
      }
      const fh = Number.isFinite(Number(frame.forecast_hour)) ? Number(frame.forecast_hour) : idx;
      const file = `${key}/f${String(fh).padStart(3, '0')}.png`;
      const png = rasterizeFrame(values, rows, cols, cfg, {
        scale: fieldMeta(bundle.fields, key)?.scale,
        wrap: fieldMeta(bundle.fields, key)?.wrap
      });
      const abs = path.join(outDir, file);
      fs.mkdirSync(path.dirname(abs), { recursive: true });
      fs.writeFileSync(abs, writePng(cols, rows, png));
      frameList.push({
        forecast_hour: fh,
        valid_time_utc: frame.valid_time_utc,
        file: `${spec.source}/${file}`,
        bytes: png.length
      });
      written.push(abs);
    });
    if (!frameList.length) { layerEntries[key] = { covered: false }; continue; }
    layerEntries[key] = {
      covered: true,
      scale: fieldMeta(bundle.fields, key)?.scale ?? 1,
      wrap: fieldMeta(bundle.fields, key)?.wrap,
      frames: frameList
    };
  }
  return {
    spec, bundle, rows, cols, lats, lons,
    sourceEntry: {
      file: path.basename(bundlePath),
      bbox: bundle.bbox,
      grid: { rows, cols, latitudes: lats, longitudes: lons },
      cycle: bundle.cycle || null,
      model: bundle.model || spec.source,
      source_kind: bundle.source_kind || 'forecast',
      layers: layerEntries
    },
    written
  };
}

function mergeExistingManifest(abs, region) {
  try {
    const m = JSON.parse(fs.readFileSync(abs, 'utf8'));
    if (m && m.schema_version === 1 && m.region === region) return m;
  } catch (_) { /* fresh manifest */ }
  return null;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  fs.mkdirSync(args.out, { recursive: true });
  const perRegion = new Map();
  const allWritten = [];
  for (const specStr of args.specs) {
    const spec = parseSpec(specStr);
    const result = processSpec(spec, args);
    if (!perRegion.has(spec.region)) perRegion.set(spec.region, []);
    perRegion.get(spec.region).push(result);
    allWritten.push(...result.written);
    console.log(`${spec.region}/${spec.source}: ${result.written.length} PNG frames`);
  }
  const generatedUtc = new Date().toISOString();
  for (const [region, results] of perRegion) {
    const manifestAbs = path.join(args.out, region, 'manifest.json');
    const prev = mergeExistingManifest(manifestAbs, region);
    const sources = prev?.sources ? structuredClone(prev.sources) : {};
    for (const r of results) {
      if (!r.sourceEntry) continue;
      sources[r.spec.source] = r.sourceEntry;
    }
    const manifest = {
      schema_version: 1,
      palette_version: palette.PALETTE_VERSION,
      generated_utc: generatedUtc,
      region,
      sources
    };
    fs.mkdirSync(path.dirname(manifestAbs), { recursive: true });
    fs.writeFileSync(manifestAbs, JSON.stringify(manifest));
    console.log(`manifest: ${manifestAbs}`);
  }
  const total = allWritten.reduce((n, f) => n + fs.statSync(f).size, 0);
  console.log(`done: ${allWritten.length} PNGs, ${total} bytes`);
}

main();