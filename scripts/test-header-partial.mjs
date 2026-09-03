/**
 * lib/header-partial.mjs のテスト。
 * オンライン版リポの `src/lib/header-partial.test.ts`（vitest・11ケース）をそのまま移植。
 *
 *   node scripts/test-header-partial.mjs
 *
 * 末尾に「正典との乖離検知」を1ケース足してある（オンライン版リポが手元にある場合のみ）。
 */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import {
  applyAltLangUrl,
  collectClasses,
  extractHeader,
  extractStylesheetHrefs,
  sanitizeAltLangUrl,
  transformCss,
  transformHeaderHtml,
} from "../lib/header-partial.mjs";

let pass = 0;
const failures = [];
function it(name, fn) {
  try {
    fn();
    pass++;
    console.log(`  ok  ${name}`);
  } catch (e) {
    failures.push({ name, e });
    console.log(`  NG  ${name}\n      ${e.message.split("\n")[0]}`);
  }
}
function describe(name, fn) {
  console.log(name);
  fn();
}

const cmt = (t) => `/* ${t} ` + "*/";

describe("transformCss", () => {
  it(":root / html / body を :host へ寄せる", () => {
    const out = transformCss(":root{--a:1}html{--b:2}body{--c:3}", new Set());
    assert.ok(out.includes(":host{--a:1}"));
    assert.ok(out.includes(":host{--b:2}"));
    assert.ok(out.includes(":host{--c:3}"));
  });

  it("zoom と --z は落とし、末尾で --z:1 を与える", () => {
    const out = transformCss("html{--z:.9;zoom:.9;--header-h:56px}", new Set());
    assert.ok(!/zoom:\s*\.9/.test(out));
    assert.ok(out.includes("--header-h:56px"));
    assert.equal(out.endsWith(":host{--z:1;display:contents}"), true);
  });

  it("@font-face は落とす（Shadow DOM で効かない＋巨大）", () => {
    const out = transformCss("@font-face{font-family:X;src:url(a.woff2)}.a{color:red}", new Set(["a"]));
    assert.ok(!out.includes("font-face"));
    assert.ok(out.includes(".a{color:red}"));
  });

  it("コメントが前置された at-rule も at-rule として扱う", () => {
    const css = `${cmt("x.module.css")}@font-face{src:url(a)}${cmt("y")}.a{color:red}`;
    const out = transformCss(css, new Set(["a"]));
    assert.ok(!out.includes("src:url(a)"));
    assert.ok(out.includes(".a{color:red}"));
  });

  it("@layer properties 内の @supports ゲートを外す（@property の代替）", () => {
    const css =
      "@layer properties{@supports (-webkit-hyphens:none){*,:before{--tw-border-style:solid}}}" +
      "@layer utilities{.b{border-bottom-style:var(--tw-border-style)}}";
    const out = transformCss(css, new Set(["b"]));
    assert.ok(!out.includes("@supports"));
    assert.ok(out.includes("--tw-border-style:solid"));
  });

  it("ヘッダーに出てこないクラスのルールは落とす", () => {
    const out = transformCss(".used{a:1}.unused{a:2}.used .unused{a:3}", new Set(["used"]));
    assert.ok(out.includes(".used{a:1}"));
    assert.ok(!out.includes(".unused"));
  });

  it("動的に付け外しするクラスは残す", () => {
    const css = String.raw`.max-\[1024px\]\:hidden{display:none}`;
    assert.ok(transformCss(css, new Set()).includes("display:none"));
  });

  it("空になった @media は出さない", () => {
    assert.ok(!transformCss("@media (min-width:1px){.x{a:1}}", new Set()).includes("@media"));
  });
});

describe("transformHeaderHtml", () => {
  it("ルート相対リンクを絶対URLにし、言語トグルだけ差し替える", () => {
    const html =
      '<header><a href="/pricing">p</a>' +
      '<a href="/en" aria-label="Language">EN</a>' +
      '<a href="https://web.locahun3d.com/works/index.html">w</a>' +
      "<script>x()</" + "script></header>";
    const out = transformHeaderHtml(html, "https://web.locahun3d.com/en/works/a.html");
    assert.ok(out.includes('href="https://locahun3d.com/pricing"'));
    assert.ok(out.includes('href="https://web.locahun3d.com/en/works/a.html" aria-label="Language"'));
    assert.ok(out.includes('href="https://web.locahun3d.com/works/index.html"'));
    assert.ok(!out.includes("<script"));
  });
});

describe("sanitizeAltLangUrl", () => {
  it("works ドメイン配下だけ通す", () => {
    assert.equal(
      sanitizeAltLangUrl("https://web.locahun3d.com/works/a.html"),
      "https://web.locahun3d.com/works/a.html",
    );
    assert.equal(sanitizeAltLangUrl("https://evil.example/x"), null);
    assert.equal(sanitizeAltLangUrl(null), null);
  });
});

describe("抽出", () => {
  it("header / stylesheet / class を拾う", () => {
    const page =
      '<html><head><link rel="stylesheet" href="/a.css"/><link rel="icon" href="/i.svg"/></head>' +
      '<body><header class="x y"><div class="z"></div></header></body></html>';
    assert.deepEqual(extractStylesheetHrefs(page), ["/a.css"]);
    const h = extractHeader(page);
    assert.equal(h.startsWith("<header"), true);
    assert.deepEqual([...collectClasses(h)].sort(), ["x", "y", "z"]);
  });
});

// ── works 側で足した分 ────────────────────────────────────────────────
describe("applyAltLangUrl（キャッシュ後に当てる分）", () => {
  it("合成済み部品に対しても言語トグルだけ差し替わる", () => {
    const partial =
      '<div id="lh-online-header"><template shadowrootmode="open"><style>.a{color:red}</style>' +
      '<header><a href="https://locahun3d.com/en" aria-label="Language">EN</a></header>' +
      "</template></div>";
    const out = applyAltLangUrl(partial, "https://web.locahun3d.com/en/works/a.html");
    assert.ok(out.includes('href="https://web.locahun3d.com/en/works/a.html" aria-label="Language"'));
    assert.equal(applyAltLangUrl(partial, null), partial);
  });
});

// ── 正典との乖離検知 ──────────────────────────────────────────────────
// 正典 = オンライン版リポの src/lib/header-partial.ts。中身が変わったら
// この移植も追随させる必要があるので、ハッシュが動いたら落とす。
// （オンライン版リポが手元に無い環境ではスキップ）
const CANON_PATH = "F:/Htlml/3DGS/locahun3d_online/src/lib/header-partial.ts";
const CANON_SHA256 = "313c016fbd6161bfb115a4c9adde66838b603cb4b1dcb9a0241d8e81ef722602";

describe("正典との乖離検知", () => {
  if (!existsSync(CANON_PATH)) {
    console.log("  --  skip（正典ファイルが無い環境）");
    return;
  }
  it("online の header-partial.ts が移植時点から変わっていない", () => {
    const actual = createHash("sha256").update(readFileSync(CANON_PATH)).digest("hex");
    assert.equal(
      actual,
      CANON_SHA256,
      `正典 header-partial.ts が変更されている。lib/header-partial.mjs を追随させ、` +
        `一致させたうえで CANON_SHA256 を ${actual} に更新すること。`,
    );
  });
});

console.log(`\n${pass} passed, ${failures.length} failed`);
process.exit(failures.length ? 1 : 0);
