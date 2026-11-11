// Harness for assets/expiring-inventory-dashboard.html: runs the data model and the brief builder in Node (no browser).
// Usage: node check-dashboard.mjs <path-to-html>
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
assert.equal(scripts.length, 3, 'expected d3, model and app script blocks');
const [d3src, modelSrc, appSrc] = scripts;

// Every block parses.
for (const s of scripts) new vm.Script(s);

const ctx = vm.createContext({ console });
vm.runInContext(modelSrc + '\nglobalThis.ExpiryModel = ExpiryModel;', ctx);
const M = ctx.ExpiryModel;
let n = 0;
const t = (name, fn) => { fn(); n += 1; console.log('ok', name); };

// ---- dates and window (F1) ----
t('addMonths clamps month ends', () => {
  assert.equal(M.addMonths('2026-08-31', 6), '2027-02-28');
  assert.equal(M.addMonths('2027-08-31', 6), '2028-02-29');
  assert.equal(M.addMonths('2026-11-05', -12), '2025-11-05');
  assert.equal(M.addMonths('2026-01-31', -2), '2025-11-30');
});
t('window is today through six months ahead inclusive, with the partial last month', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  assert.equal(b.start, '2026-11-05');
  assert.equal(b.end, '2027-05-05');
  assert.equal(JSON.stringify([...b.months]), JSON.stringify(['2026-11', '2026-12', '2027-01', '2027-02', '2027-03', '2027-04', '2027-05']));
  assert.equal(b.historyStart, '2025-11-05');
});
t('reviewer walkthrough: expired and beyond-window lots excluded, final partial month kept', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [
    { productId: 'p', product: 'P', expirationDate: '2026-11-01', quantityActive: 10 },
    { productId: 'p', product: 'P', expirationDate: '2026-11-20', quantityActive: 20 },
    { productId: 'p', product: 'P', expirationDate: '2027-05-05', quantityActive: 30 },
    { productId: 'p', product: 'P', expirationDate: '2027-05-06', quantityActive: 40 },
  ];
  const r = M.expiring(pk, [{ productId: 'p', unitPrice: 10, wholesaleUnitPrice: null }], b);
  const units = r.rows.reduce((s, x) => s + x.units, 0), value = r.rows.reduce((s, x) => s + x.value, 0);
  assert.equal(units, 50);
  assert.equal(value, 500);
  assert.equal(r.issues.expired, 1);
  assert.equal(r.issues.expiredUnits, 10);
});

// ---- valuation, numbers, duplicates, units (F2) ----
t('missing price is unvalued, not $0; recorded zero stays zero', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [
    { productId: 'a', product: 'A', expirationDate: '2026-12-01', quantityActive: 5 },
    { productId: 'z', product: 'Z', expirationDate: '2026-12-01', quantityActive: 5 },
  ];
  const r = M.expiring(pk, [{ productId: 'z', unitPrice: 0, wholesaleUnitPrice: null }], b);
  const a = r.rows.find((x) => x.productId === 'a'), z = r.rows.find((x) => x.productId === 'z');
  assert.equal(a.unitPrice, null); assert.equal(a.unvaluedUnits, 5); assert.equal(a.valuedUnits, 0);
  assert.equal(z.unitPrice, 0); assert.equal(z.valuedUnits, 5); assert.equal(z.value, 0);
});
t('wholesale price wins; null wholesale falls back to unit price', () => {
  const p = M.priceMap([{ productId: 'w', unitPrice: 20, wholesaleUnitPrice: 12 }, { productId: 'u', unitPrice: 20, wholesaleUnitPrice: null }]);
  assert.equal(p.get('w').price, 12); assert.equal(p.get('u').price, 20);
});
t('string, NaN, Infinity and negative quantities are held as invalid, never summed', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = ['2', '3', '1,5', NaN, Infinity, -4].map((q) => ({ productId: 'p', product: 'P', expirationDate: '2026-12-01', quantityActive: q }));
  const r = M.expiring(pk, [{ productId: 'p', unitPrice: 10 }], b);
  assert.equal(r.rows.length, 0);
  assert.equal(r.issues.invalid, 6);
});
t('negative or string price is unvalued', () => {
  const p = M.priceMap([{ productId: 'n', unitPrice: -1 }, { productId: 's', unitPrice: '1,5' }]);
  assert.equal(p.get('n').price, null); assert.equal(p.get('s').price, null);
});
t('duplicate package IDs counted once; missing IDs disclosed', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [1, 1, 2].map((id) => ({ packageId: 'pkg' + id, productId: 'p', product: 'P', expirationDate: '2026-12-01', quantityActive: 5 }));
  const r = M.expiring(pk, [{ productId: 'p', unitPrice: 10 }], b);
  assert.equal(r.rows[0].units, 10); assert.equal(r.issues.duplicate, 1); assert.equal(r.issues.noPackageIds, 0);
  const r2 = M.expiring([{ productId: 'p', product: 'P', expirationDate: '2026-12-01', quantityActive: 5 }], [], b);
  assert.equal(r2.issues.noPackageIds, 1);
});
t('a package in a different unit from its product is held, not summed', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [
    { productId: 'p', product: 'P', expirationDate: '2026-12-01', quantityActive: 2, unit: 'case' },
    { productId: 'p', product: 'P', expirationDate: '2026-12-01', quantityActive: 24, unit: 'each' },
  ];
  const r = M.expiring(pk, [{ productId: 'p', unitPrice: 10, unit: 'each' }], b);
  assert.equal(r.rows[0].units, 24); assert.equal(r.issues.unitMismatch, 1);
});
t('missing or impossible expiry dates are unclassified, not dropped silently', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [null, '2026-02-30', 'soon'].map((d) => ({ productId: 'p', product: 'P', expirationDate: d, quantityActive: 1 }));
  const r = M.expiring(pk.concat([null]), [], b);
  assert.equal(r.issues.missingDate, 3); assert.equal(r.issues.invalid, 1);
});
t('lots inside one month keep their own dates', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const pk = [['2026-12-10', 100], ['2026-12-31', 50]].map(([d, q]) => ({ productId: 'p', product: 'P', expirationDate: d, quantityActive: q }));
  const r = M.expiring(pk, [{ productId: 'p', unitPrice: 10 }], b);
  assert.equal(r.rows[0].value, 1500);
  assert.equal(r.rows[0].firstExpiry, '2026-12-10'); assert.equal(r.rows[0].lastExpiry, '2026-12-31');
  assert.equal(JSON.stringify(r.rows[0].lots.map((l) => [l.date, l.units])), JSON.stringify([['2026-12-10', 100], ['2026-12-31', 50]]));
});

// ---- buyers (F3) ----
const line = (o) => ({ orderId: 'o1', orderNumber: 'SO-1', orderDate: '2026-10-01 10:00:00', productId: 'p', customerId: 'c1', customer: 'C1', salesRep: 'Rep A', quantity: 5, orderItemPrice: 8, ...o });
t('identical duplicate line counted once (no line IDs)', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([line({}), line({})], new Set(['p']), b);
  assert.equal(r.rows[0].units, 5); assert.equal(r.rows[0].lastOrderValue, 40); assert.equal(r.issues.duplicate, 1);
});
t('duplicate line IDs counted once; distinct line IDs both count', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([line({ lineId: 'l1' }), line({ lineId: 'l1' }), line({ lineId: 'l2' })], new Set(['p']), b);
  assert.equal(r.rows[0].units, 10); assert.equal(r.issues.duplicate, 1);
});
t('zero, negative and $0 lines establish no buyer', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([line({ quantity: 0 }), line({ quantity: -5, orderId: 'o2' }), line({ orderItemPrice: 0, orderId: 'o3' })], new Set(['p']), b);
  assert.equal(r.rows.length, 0); assert.equal(r.issues.notPaid, 3);
});
t('lines outside the 12-month history period, ineligible status or samples are excluded', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([
    line({ orderDate: '2025-11-04', orderId: 'old' }),
    line({ orderDate: '2026-11-06', orderId: 'future' }),
    line({ status: 'CANCELLED', orderId: 'x' }),
    line({ isSample: true, orderId: 's' }),
    line({ orderDate: '2025-11-05', orderId: 'edge', status: 'Delivered' }),
  ], new Set(['p']), b);
  assert.equal(r.issues.outOfPeriod, 2); assert.equal(r.issues.ineligibleStatus, 1); assert.equal(r.issues.sample, 1);
  assert.equal(r.rows[0].orders, 1);
});
t('missing order date or string quantity is invalid, not a crash', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([line({ orderDate: undefined }), line({ quantity: '5' }), null], new Set(['p']), b);
  assert.equal(r.rows.length, 0); assert.equal(r.issues.invalid, 3);
});
t('all order reps kept; other products on the order ignored', () => {
  const b = M.bounds('2026-11-05', 6, 12);
  const r = M.buyers([line({}), line({ orderId: 'o2', orderNumber: 'SO-2', salesRep: 'Rep B', orderDate: '2026-10-02' }), line({ productId: 'q', orderId: 'o3' })], new Set(['p']), b);
  assert.equal(r.rows.length, 1); assert.equal(JSON.stringify([...r.rows[0].reps]), JSON.stringify(['Rep A', 'Rep B'])); assert.equal(r.rows[0].lastOrder, '2026-10-02');
});

// ---- app code: run it with the real d3 and a stub DOM, then check the brief (F4-F7) ----
const nodes = new Map();
const stub = () => ({ hidden: false, textContent: '', dataset: {}, style: {}, clientWidth: 0, setAttribute() {}, append() {}, replaceChildren() {}, scrollIntoView() {} });
const document = { getElementById: (id) => { if (!nodes.has(id)) nodes.set(id, stub()); return nodes.get(id); }, querySelectorAll: () => [], fonts: { ready: new Promise(() => {}) } };
const app = vm.createContext({ console, document, location: { search: '?agent=claude' }, matchMedia: () => ({ matches: true }), ResizeObserver: class { observe() {} }, URLSearchParams, Intl, performance, requestAnimationFrame: () => 0, setTimeout });
vm.runInContext(d3src + '\n' + modelSrc + '\nglobalThis.ExpiryModel = ExpiryModel;', app);
const hooked = appSrc.replace(/\}\)\(\);\s*$/, 'globalThis.__app = { S, brief, compute, windowModel, renderFoot, SNAPSHOT, drafts };\n})();');
assert.notEqual(hooked, appSrc, 'could not hook the app IIFE');
vm.runInContext(hooked, app);
const A = app.__app;

t('snapshot: default window is Nov 5, 2026 to May 5, 2027 and holds out expired stock', () => {
  assert.equal(A.S.B.start, '2026-11-05'); assert.equal(A.S.B.end, '2027-05-05');
  assert.equal(A.S.B.months.length, 7);
  assert.ok(A.S.expiring.every((r) => r.firstExpiry >= '2026-11-05' && r.lastExpiry <= '2027-05-05'));
  assert.equal(A.S.stockIssues.expired, 6);
});
t('snapshot: $0 order lines and identical lines are not counted as purchases', () => {
  const all = app.ExpiryModel.buyers(A.SNAPSHOT.orders, new Set(A.SNAPSHOT.orders.map((o) => o.productId)), A.S.B);
  console.log('   window buyer issues:', JSON.stringify(A.S.buyerIssues), 'all-product issues:', JSON.stringify(all.issues));
  assert.equal(all.issues.duplicate, 3); assert.equal(all.issues.notPaid, 136);
  assert.ok(A.S.targets.every((r) => r.units > 0 && r.lastOrderValue > 0));
});
t('window change: matrix and chart share months; stale selection is cleared', () => {
  const row = A.S.expiring[0];
  A.S.cell = row.key;
  A.S.horizon = 18; A.compute();
  assert.equal(A.windowModel().months.length, A.S.B.months.length);
  assert.equal(A.S.B.months.length, 19);
  A.S.cell = 'nope|2030-01'; A.compute();
  assert.equal(A.S.cell, '');
  A.S.horizon = 6; A.compute();
});
t('brief: user terms go in literally; nothing is invented when blank', () => {
  const row = A.S.expiring.find((r) => A.S.targets.some((b) => b.productId === r.productId));
  const buyer = A.S.targets.find((b) => b.productId === row.productId);
  const blank = A.brief(row, buyer, { contact: '', offer: '', deadline: '', minimum: '', sender: '' });
  assert.match(blank, /Offer: \[Offer not set/); assert.match(blank, /Order by: \[Deadline not set/);
  assert.match(blank, /Sender: \[Sender not set/); assert.match(blank, /Recipient: \[Recipient not set/);
  assert.doesNotMatch(blank, /\[X\]% off/); assert.doesNotMatch(blank, /sign it from/i); assert.doesNotMatch(blank, /sales team/i);
  const full = A.brief(row, buyer, { contact: 'Jordan', offer: '15% off', deadline: '2026-12-01', minimum: '', sender: 'Alex' });
  assert.match(full, /Recipient: Jordan \(entered by the user\)/); assert.match(full, /Offer: 15% off/);
  assert.match(full, /Order by: Dec 1, 2026/); assert.match(full, /Sender: Alex/);
  assert.match(full, /Context only; they are not the sender/);
});
t('brief: carries IDs, read time, every lot date, window and history completeness', () => {
  const row = A.S.expiring.find((r) => A.S.targets.some((b) => b.productId === r.productId));
  const buyer = A.S.targets.find((b) => b.productId === row.productId);
  const text = A.brief(row, buyer, { contact: '', offer: '', deadline: '', minimum: '', sender: '' });
  assert.ok(text.includes(row.productId) && text.includes(buyer.customerId));
  assert.match(text, /snapshot read Nov 5, 2026/); assert.match(text, /not a live read/);
  assert.match(text, /4,000 of 8,983 order lines read, so some buyers may be missing/);
  assert.match(text, /expiry window Nov 5, 2026 to May 5, 2027/);
  for (const l of row.lots) assert.ok(text.includes('expiring ' + new Date(l.date + 'T00:00:00Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })));
  assert.match(text, /do not send, schedule or queue anything/);
});
t('brief: an order-by date on or after the first lot expiry is flagged outside the email', () => {
  const row = A.S.expiring[0];
  const buyer = { customer: 'X', customerId: 'c', orders: 1, units: 1, lastOrder: '2026-10-01', lastOrderValue: 10, reps: [] };
  const text = A.brief(row, buyer, { contact: '', offer: '', deadline: row.firstExpiry, minimum: '', sender: '' });
  assert.match(text, /Note for me, not for the email: The order-by date/);
});
t('footer: discloses snapshot, bounds, partial history and held-out records', () => {
  A.renderFoot();
  const f = nodes.get('loaded').textContent;
  assert.match(f, /not live/); assert.match(f, /Nov 5, 2026 to May 5, 2027/); assert.match(f, /4,000 of 8,983/);
  assert.match(f, /already-expired package/); assert.match(f, /no package IDs/);
  console.log('   footer:', f);
});

console.log(`\n${n} checks passed`);
