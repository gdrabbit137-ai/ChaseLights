// Locale sidecar loader (CL-I18N-01).
// Loads locales/<lang>/{ui,taxonomy,catalog}.json at runtime and falls back to
// `en` per missing key. Never blocks first paint: callers await it and re-render.
export const SIDECAR_FILES = ["ui", "taxonomy", "catalog"];
export const FALLBACK_LOCALE = "en";

export function resolveLangFromQuery(search) {
  const q = new URLSearchParams(search || "");
  const lang = q.get("lang");
  return lang || null;
}

function mergeDeep(base, over) {
  if (over === undefined || over === null) return base;
  if (Array.isArray(base) || Array.isArray(over) || typeof base !== "object" || typeof over !== "object") {
    return over;
  }
  const out = { ...base };
  for (const [k, v] of Object.entries(over)) out[k] = mergeDeep(base?.[k], v);
  return out;
}

async function fetchJson(url, fetchImpl) {
  const res = await fetchImpl(url, { cache: "no-cache" });
  if (!res.ok) throw new Error(`${url} -> HTTP ${res.status}`);
  return res.json();
}

// Repo-root locales/ resolved from this module's own URL (apps/web-v2/ -> ../../locales/).
const DEFAULT_BASE = new URL("../../locales/", import.meta.url).href;

export async function loadLocaleSidecar(lang, { fetchImpl = globalThis.fetch, base = DEFAULT_BASE } = {}) {
  const read = async (l) => {
    const out = {};
    for (const name of SIDECAR_FILES) {
      out[name] = await fetchJson(`${base}${l}/${name}.json`, fetchImpl);
    }
    return out;
  };
  const primary = await read(lang);
  const fallback = lang === FALLBACK_LOCALE ? primary : await read(FALLBACK_LOCALE);
  const merged = {};
  for (const name of SIDECAR_FILES) merged[name] = mergeDeep(fallback[name], primary[name]);
  return { lang, fallback: FALLBACK_LOCALE, ...merged };
}

// Merge sidecar UI copy over the embedded dictionary so missing keys keep the
// shipped defaults (no blank labels on the first render).
export function applyUiCopy(copy, lang, sidecar) {
  if (!copy || !sidecar || !sidecar.ui) return false;
  const app = sidecar.ui.app || {};
  const research = sidecar.ui.research || {};
  Object.assign(copy[lang], app);
  if (copy[lang] && research) for (const [k, v] of Object.entries(research)) {
    if (!(k in copy[lang])) copy[lang][k] = v;
  }
  return true;
}

export function taxonomyLabel(sidecar, metric, lang) {
  const node = sidecar?.taxonomy?.metrics?.[metric];
  if (!node) return null;
  return node.label || null;
}
