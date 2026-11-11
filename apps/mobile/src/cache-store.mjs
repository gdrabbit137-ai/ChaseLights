// Memory-backed cache adapter (tests + non-persistent fallback).
// The shell injects a Capacitor Preferences-backed adapter at runtime.
export function memoryCache(initial = {}) {
  const store = new Map(Object.entries(initial));
  return {
    async read(key) { return store.has(key) ? store.get(key) : null; },
    async write(key, value) { store.set(key, String(value)); },
    keys: () => [...store.keys()]
  };
}
