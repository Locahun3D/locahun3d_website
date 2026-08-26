/**
 * works_dark_audit.mjs — works（JA/EN 全24ページ）が「ダーク＋青アクセント」で
 * 読める状態かを機械検査する。works_light_audit.mjs の逆（黒地版）。
 *
 * 前提:
 *   1) リポジトリ直下で  python -m http.server 8830 --bind 127.0.0.1
 *   2) playwright を用意（node_modules は .gitignore 済み）:  npm i playwright
 * 実行:
 *   node scripts/works_dark_audit.mjs [--base http://127.0.0.1:8830] [--shots dir] [--width 1280]
 *   （--width 375 でスマホ幅の横スクロール検査も回す）
 *
 * 検査項目（1ページあたり）:
 *   bg      : <body> の実効背景が黒系か（輝度 <= 0.06）
 *   hscroll : 横スクロールが出ていないか（documentElement.scrollWidth <= clientWidth+1）
 *   contrast: 全テキストノードの computed color と「実際に後ろにある地色」（祖先を
 *             遡って alpha 合成した実効値）の WCAG コントラスト比を測り、
 *             AA 未満（通常 4.5:1 / 大きい文字 3.0:1）を列挙する。
 *             白文字が黒地でちゃんと読めるかの検出が主目的。
 *             ヘッダー(.site-header)も今回の作業対象なので通常の検査に含める。
 *             ⚠ --faint = rgba(255,255,255,.36) の極小メタ文字（日付・所要時間・
 *               COMING SOON・WORKFLOW 帯）は 3.06〜3.28:1 で AA 未満だが、これは
 *               2026-08-16 以前から続く旧デザイン由来。b25b40d（白青化直前）を
 *               別ポートで配信して同じ検査を回し、24ページすべてで件数が
 *               完全一致することを確認済み＝本作業による退行ではない。
 *               よって inherited として別枠で数え、PASS/FAIL は退行だけで決める。
 *   accent  : 旧アンバー #ffb454 / #ff9f1c / #ff8a4c 系の残留が無いか
 *   http4xx : 画像・動画の 404（EN 記事の /works/images/ 絶対参照の回帰検出）
 */
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const args = process.argv.slice(2);
const base = (args.includes('--base') ? args[args.indexOf('--base') + 1] : 'http://127.0.0.1:8830').replace(/\/$/, '');
const shots = args.includes('--shots') ? args[args.indexOf('--shots') + 1] : 'shots';
const width = args.includes('--width') ? +args[args.indexOf('--width') + 1] : 1280;

const ARTICLES = [
  '3dgs-file-formats', '3dgs-lidar-denoise', '3dgs-software-comparison',
  'chevron-rokunowa-mv', 'houdini-comfyui-gsplat-workflow', 'isaacsim-3dgs-import',
  'isaacsim-3dgs-robot-demos', 'portalcam-drone-ai-workflow',
  'portalcam-xbin-raw-extraction', 'ue5-xgrids-3dgs-aerial-ai', 'vectorworks-3dgs-mesh',
];
const pages = [
  '/works/index.html',
  ...ARTICLES.map((a) => `/works/${a}.html`),
  '/en/works/index.html',
  ...ARTICLES.map((a) => `/en/works/${a}.html`),
];

const AUDIT = () => {
  const lum = (r, g, b) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const parse = (c) => {
    const m = /rgba?\(([^)]+)\)/.exec(c || '');
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1,
  });
  // 要素の後ろにある「実際の地色」を祖先を遡って合成する
  const bgOf = (el) => {
    let acc = null;
    for (let n = el; n && n !== document.documentElement.parentNode; n = n.parentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) acc = acc ? over(acc, c) : c;
      if (acc && acc.a >= 0.999) break;
    }
    // ダークテーマなので最終的な下地はブラウザキャンバスではなく黒（body 背景）
    const base = { r: 0, g: 0, b: 0, a: 1 };
    return acc ? (acc.a >= 0.999 ? acc : over(acc, base)) : base;
  };
  const ratio = (a, b) => {
    const l1 = lum(a.r, a.g, a.b), l2 = lum(b.r, b.g, b.b);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };

  const bodyBg = bgOf(document.body);
  const EXEMPT = '';
  const bad = [], preexisting = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  let n;
  while ((n = walker.nextNode())) {
    const t = (n.nodeValue || '').trim();
    if (!t) continue;
    const el = n.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    if (EXEMPT && el.closest(EXEMPT)) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const fg = parse(cs.color);
    if (!fg) continue;
    const solid = fg.a >= 0.999 ? fg : over(fg, bgOf(el));
    const cr = ratio(solid, bgOf(el));
    // WCAG AA: 通常文字 4.5:1 / 大きい文字（24px以上、または18.66px以上の太字）3.0:1
    const px = parseFloat(cs.fontSize) || 16;
    const w = parseInt(cs.fontWeight, 10) || 400;
    const large = px >= 24 || (px >= 18.66 && w >= 700);
    const need = large ? 3.0 : 4.5;
    if (cr < need) {
      const rec = {
        sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
        color: cs.color, ratio: +cr.toFixed(2), need, px, text: t.slice(0, 40),
      };
      // 旧デザイン由来の --faint（極小メタ文字）は inherited へ。上の注記を参照。
      const inherited = /rgba\(255,\s*255,\s*255,\s*0\.3[0-9]*\)/.test(cs.color);
      (inherited ? preexisting : bad).push(rec);
    }
  }
  // 旧アクセントの残留
  const css = [...document.querySelectorAll('style')].map((s) => s.textContent).join('\n');
  // <style> だけでなく共有ヘッダーCSS（assets/works-header.css）も見る
  const linkCss = [...document.querySelectorAll('link[rel=stylesheet]')]
    .map((l) => { try { return [...l.sheet.cssRules].map((r) => r.cssText).join('\n'); } catch (e) { return ''; } })
    .join('\n');
  const cssAll = css + '\n' + linkCss;
  const legacy = (cssAll.match(/#ffb454|#ff9f1c|#ff8a4c|#ffd9a8|rgba\(255,\s*180,\s*84|rgba\(255,\s*138,\s*76/gi) || []).length;

  return {
    bodyBg: `rgb(${Math.round(bodyBg.r)},${Math.round(bodyBg.g)},${Math.round(bodyBg.b)})`,
    bodyLum: +lum(bodyBg.r, bodyBg.g, bodyBg.b).toFixed(3),
    scrollW: document.documentElement.scrollWidth,
    clientW: document.documentElement.clientWidth,
    bad, preexisting, legacy,
  };
};

const browser = await chromium.launch({ channel: 'chrome' });
const ctx = await browser.newContext({ viewport: { width, height: 1000 }, deviceScaleFactor: 1 });
fs.mkdirSync(shots, { recursive: true });

let fails = 0;
const rows = [];
for (const p of pages) {
  const pg = await ctx.newPage();
  // 画像・動画の 404 を拾う（EN 記事の /works/images/ 絶対参照の回帰検出）
  const notFound = [];
  pg.on('response', (res) => { if (res.status() >= 400) notFound.push(`${res.status()} ${res.url()}`); });
  await pg.goto(base + p, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await pg.waitForTimeout(600);
  await pg.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await pg.waitForTimeout(400);
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(300);
  const r = await pg.evaluate(AUDIT);
  const name = p.replace(/^\//, '').replace(/[\/]/g, '_').replace(/\.html$/, '');
  await pg.screenshot({ path: path.join(shots, name + '.png'), fullPage: true });
  await pg.close();

  const okBg = r.bodyLum <= 0.06;
  const okScroll = r.scrollW <= r.clientW + 1;
  const okContrast = r.bad.length === 0;
  const okAccent = r.legacy === 0;
  const ok404 = notFound.length === 0;
  const ok = okBg && okScroll && okContrast && okAccent && ok404;
  if (!ok) fails++;
  rows.push({ p, okBg, okScroll, okContrast, okAccent, r });
  console.log(
    `${ok ? 'PASS' : 'FAIL'}  ${p.padEnd(50)} bg=${r.bodyBg} lum=${r.bodyLum} ` +
    `scroll=${r.scrollW}/${r.clientW} lowContrast=${r.bad.length} legacyAccent=${r.legacy} http4xx=${notFound.length} (inherited-faint=${r.preexisting.length})`
  );
  for (const u of notFound.slice(0, 6)) console.log(`        ✗ ${u}`);
  for (const b of r.bad.slice(0, 12)) console.log(`        ↳ ${b.ratio} (need ${b.need}, ${b.px}px)  ${b.color}  ${b.sel}  "${b.text}"`);
}
console.log(`\n${pages.length} pages, ${fails} failing`);
await browser.close();
process.exit(fails ? 1 : 0);
