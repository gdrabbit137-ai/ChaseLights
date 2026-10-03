export const V2_INDEX_URL = './weathergrid/v2/index.json';

export async function loadV2Index(fetchImpl = fetch) {
  const r = await fetchImpl(V2_INDEX_URL, { cache: 'no-store' });
  if (!r.ok) throw new Error('V2 index HTTP ' + r.status);
  const data = await r.json();
  if (data.schema_version !== 2 || data.payload_partition !== 'valid_time') {
    throw new Error('unsupported V2 cache index');
  }
  return data;
}

export function validTimeToken(value) {
  const raw = String(value);
  const normalized = /(?:Z|[+-]\d\d:\d\d)$/.test(raw) ? raw : raw + 'Z';
  const d = new Date(normalized);
  if (Number.isNaN(d.getTime())) throw new Error('invalid valid time ' + value);
  return d.toISOString().slice(0, 16).replace(/[-:]/g, '') + 'Z';
}

export function providerRun(index, provider) {
  return index?.provider_runs?.[provider] || null;
}

export function providerSupportsField(index, provider, field) {
  const run = providerRun(index, provider);
  return !!(run && Array.isArray(run.supported_fields) && run.supported_fields.includes(field));
}

function utcTimeMs(value) {
  if (value instanceof Date) return value.getTime();
  const raw = String(value);
  const normalized = /(?:Z|[+-]\\d\\d:\\d\\d)$/.test(raw) ? raw : raw + 'Z';
  return new Date(normalized).getTime();
}

export function nearestValidTime(index, provider, target = new Date()) {
  const run = providerRun(index, provider);
  const entries = run?.valid_times || [];
  if (!entries.length) return run?.default_valid_time_utc || null;
  const targetMs = utcTimeMs(target);
  let best = null;
  let distance = Infinity;
  for (const entry of entries) {
    const value = typeof entry === 'string' ? entry : entry.valid_time_utc;
    if (!value) continue;
    const ms = utcTimeMs(value);
    if (Number.isNaN(ms)) continue;
    const d = Math.abs(ms - targetMs);
    if (d < distance) {
      best = value;
      distance = d;
    }
  }
  return best || run?.default_valid_time_utc || null;
}

export function tileToSamples(tile) {
  if (tile.schema_version !== 1 || !tile.native_grid) throw new Error('unsupported native tile');
  const { rows, cols, latitudes, longitudes } = tile.grid;
  const expected = rows * cols;
  const fields = Object.entries(tile.values);
  for (const [name, values] of fields) {
    if (values.length !== expected) throw new Error(name + ' grid length mismatch');
  }
  const out = [];
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const i = r * cols + c;
      const values = {};
      for (const [name, array] of fields) values[name] = array[i];
      out.push({ lat: latitudes[r], lon: longitudes[c], values, time: tile.valid_time_utc });
    }
  }
  return out;
}

export async function loadNativeTile(url, fetchImpl = fetch) {
  const r = await fetchImpl(url, { cache: 'no-store' });
  if (!r.ok) throw new Error('native tile HTTP ' + r.status);
  const tile = await r.json();
  return { tile, samples: tileToSamples(tile) };
}

function intersects(a, b) {
  return a.west < b.e && a.east > b.w && a.south < b.n && a.north > b.s;
}

export function cellsForViewport(index, region, viewport, provider = 'jma') {
  const r = index.regions?.[region];
  if (!r) return [];
  const published = providerRun(index, provider)?.published_cell_ids;
  const publishedSet = Array.isArray(published) ? new Set(published) : null;
  return r.cells.filter((cell) =>
    cell.providers?.[provider]
    && (!publishedSet || publishedSet.has(cell.id))
    && intersects(cell.bbox, viewport)
  );
}

export function tileUrl(cell, provider, validTime) {
  const spec = cell.providers?.[provider];
  if (!spec?.url_template) throw new Error('provider tile unavailable');
  return spec.url_template.replace('{valid_time}', validTimeToken(validTime));
}

export function dedupeSamples(samples) {
  const unique = new Map();
  for (const sample of samples) {
    const key = Number(sample.lat).toFixed(6) + ',' + Number(sample.lon).toFixed(6);
    if (!unique.has(key)) unique.set(key, sample);
  }
  return [...unique.values()];
}

export async function loadViewportTiles(index, region, viewport, provider, validTime, fetchImpl = fetch) {
  const cells = cellsForViewport(index, region, viewport, provider);
  const settled = await Promise.allSettled(cells.map(async (cell) => {
    const url = tileUrl(cell, provider, validTime);
    const loaded = await loadNativeTile(url, fetchImpl);
    return { cell, url, ...loaded };
  }));
  const loaded = settled.filter((x) => x.status === 'fulfilled').map((x) => x.value);
  const failed = settled.filter((x) => x.status === 'rejected').map((x) => String(x.reason));
  return {
    cells,
    loaded,
    failed,
    samples: dedupeSamples(loaded.flatMap((x) => x.samples)),
  };
}
