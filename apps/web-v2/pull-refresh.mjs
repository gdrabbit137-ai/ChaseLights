// Pull-to-refresh gesture + cloud bundle-digest probe for the ChaseLights V2 shell.
//
// Pure logic (no DOM at import time) so `node --test` in apps/web-v2 and the
// Capacitor shell suite can exercise it with synthetic touch events and a stub
// fetch. The app layer in app.mjs wires the handlers to document listeners.
//
// Refresh contract (CL-APP-02): a qualifying pull re-fetches the published
// bundle digest (/api/v1/catalog/digests) AND the data itself; digest
// verification stays fail-closed in catalog-state / bundle-digests.mjs.
export function createPullToRefresh({
  threshold = 80,
  atTop = () => true, // injected scroll-position check; never assume window in tests
  onRefresh = () => {},
  onPullChange = () => {}
} = {}) {
  if (typeof threshold !== "number" || !(threshold > 0)) throw new Error("createPullToRefresh: threshold must be a positive number");
  let startY = null;
  let maxPull = 0;
  let fired = false;
  function handleTouchStart(event) {
    const y = event?.touches?.[0]?.clientY;
    if (typeof y !== "number") return;
    // Only a downward pull that starts at the top of the page counts.
    startY = atTop() ? y : null;
    maxPull = 0;
    fired = false;
  }
  function handleTouchMove(event) {
    if (startY === null) return;
    const y = event?.touches?.[0]?.clientY;
    if (typeof y !== "number") return;
    const pull = Math.max(0, y - startY);
    if (pull > maxPull) maxPull = pull;
    onPullChange(pull >= threshold);
  }
  function handleTouchEnd() {
    if (startY === null) return;
    const shouldRefresh = maxPull >= threshold;
    startY = null;
    maxPull = 0;
    onPullChange(false);
    // Fire exactly once per gesture even if the handler runs twice.
    if (shouldRefresh && !fired) { fired = true; onRefresh(); }
  }
  return { handleTouchStart, handleTouchMove, handleTouchEnd };
}

// Re-fetch the cloud-published bundle digest. Tolerant of static hosting
// (endpoint may 404 or be unreachable offline) — returns null instead of
// throwing so a refresh never regresses into a harder failure than a missed
// probe. Response contract matches version-check.mjs: {digest} or {catalog:{sha256}}.
export async function fetchCloudDigest(fetchImpl = (...args) => fetch(...args), url = "/api/v1/catalog/digests") {
  try {
    const response = await fetchImpl(url, { headers: { accept: "application/json" }, cache: "no-store" });
    if (!response.ok) return null;
    const doc = await response.json();
    const digest = typeof doc?.digest === "string" ? doc.digest
      : typeof doc?.catalog?.sha256 === "string" ? doc.catalog.sha256 : null;
    return digest || null;
  } catch {
    return null;
  }
}
