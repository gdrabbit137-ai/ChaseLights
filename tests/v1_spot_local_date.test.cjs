// V1 regression coverage for spot-local calendar days and displayed forecast windows.
// Run: node --test tests/v1_spot_local_date.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/app.js'), 'utf8');
function extractFunction(name, nextName) {
  const start = source.indexOf('    function ' + name + '(');
  const end = source.indexOf('    function ' + nextName + '(', start + 1);
  assert.ok(start >= 0 && end > start, 'Expected V1 function ' + name);
  return source.slice(start, end);
}
const calendarCode = extractFunction('localDateString', 'selectedDateForSpot');
const windowCode = extractFunction('fmtWindow', 'confidenceLabel');
const context = vm.createContext({ Intl, Date });
vm.runInContext(calendarCode + '\n' + windowCode, context);
test('Alaska local calendar date can differ from UTC', () => {
  const RealDate = Date;
  class FrozenDate extends RealDate { constructor(...args) { super(...(args.length ? args : ['2026-10-18T02:30:00Z'])); } }
  const ctx = vm.createContext({ Intl, Date: FrozenDate });
  vm.runInContext(calendarCode, ctx);
  assert.equal(vm.runInContext("localDateString('America/Anchorage',0)", ctx), '2026-10-17');
  assert.equal(vm.runInContext("localDateString('America/Anchorage',1)", ctx), '2026-10-18');
});
test('local day selection remains calendar-based across Alaska DST change', () => {
  class FrozenDate extends Date { constructor(...args) { super(...(args.length ? args : ['2026-11-01T10:30:00Z'])); } }
  const ctx = vm.createContext({ Intl, Date: FrozenDate });
  vm.runInContext(calendarCode, ctx);
  assert.equal(vm.runInContext("localDateString('America/Anchorage',0)", ctx), '2026-11-01');
  assert.equal(vm.runInContext("localDateString('America/Anchorage',1)", ctx), '2026-11-02');
});
test('window renders source-provided Alaska abbreviation without browser-timezone conversion', () => {
  const result = vm.runInContext("fmtWindow({window_start:'2026-10-17 15:00',window_end:'2026-10-17 16:00',timezone_abbr:'AKDT'})", context);
  assert.equal(result, '10/17 15:00–16:00 AKDT');
});
