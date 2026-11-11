// APP shell i18n. Key structure mirrors apps/web-v2's flat camelCase copy keys
// (see apps/web-v2/app.mjs `copy`/`researchCopy` dicts) so strings are reused,
// not rewritten. Bundled locales are the boot fallback; cloud language packs
// (same key shape) can be merged at runtime, so adding a language is a data-layer
// change with no app release. UI code must never hardcode copy — always t(key).
const BASE_LOCALES = ['zh-TW', 'en', 'ja'];
const FALLBACK_LOCALE = 'zh-TW';

const bundled = {};
for (const locale of BASE_LOCALES) {
  bundled[locale] = (await import(`./locales/${locale}.json`, {with: {type: 'json'}})).default;
}

export function createI18n({locale = FALLBACK_LOCALE, locales = bundled, fallback = FALLBACK_LOCALE} = {}) {
  let active = locales[locale] ? locale : fallback;
  function t(key, vars = {}) {
    const dict = locales[active] ?? {};
    let text = dict[key] ?? locales[fallback]?.[key] ?? locales[BASE_LOCALES[0]]?.[key];
    if (typeof text !== 'string') return key; // missing key surfaces as the key itself, never silent copy
    for (const [name, value] of Object.entries(vars)) {
      text = text.replaceAll(`{${name}}`, String(value));
    }
    return text;
  }
  return {
    t,
    get locale() { return active; },
    availableLocales: () => Object.keys(locales),
    setLocale(next) { if (locales[next]) active = next; },
    // Merge a cloud language pack (flat key/value JSON). New languages = new data.
    registerLocale(code, pack) {
      if (code && pack && typeof pack === 'object' && Object.keys(pack).length) locales[code] = {...pack};
    }
  };
}

export function keyParity(locales = bundled) {
  const base = Object.keys(locales[FALLBACK_LOCALE] ?? {}).sort();
  const report = {};
  for (const [code, pack] of Object.entries(locales)) {
    const keys = Object.keys(pack ?? {}).sort();
    report[code] = {missing: base.filter((k) => !(k in (pack ?? {}))),
      extra: keys.filter((k) => !base.includes(k)), complete: keys.join('|') === base.join('|')};
  }
  return report;
}

export {BASE_LOCALES, FALLBACK_LOCALE, bundled};
