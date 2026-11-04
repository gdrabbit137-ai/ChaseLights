// CL-WG-16 test helper: an INDEPENDENT reimplementation of the CSS hsl()
// string -> 8-bit RGB conversion used by the PNG prerender generator and the
// browser's smooth-field raster. The constants it validates were also
// cross-pinned in test_weathergrid_png_prerender.py, so a formula drift in
// either the palette module or the generator's converter fails both suites.
export function rgbForTest(css){
  const m = /hsl\(\s*([-\d.]+)(?:deg)?\s+([\d.]+)%\s+([\d.]+)%\s*\)/.exec(css);
  if(!m) throw new Error(`unsupported css: ${css}`);
  const h = Number(m[1]), s = Number(m[2]) / 100, l = Number(m[3]) / 100;
  const k = n => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const to255 = x => Math.round(255 * x);
  return [to255(f(0)), to255(f(8)), to255(f(4))];
}