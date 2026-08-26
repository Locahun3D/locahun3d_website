"""
⚠ 2026-08-16 に役目を終えた。本人判断で works は「以前のダーク配色＋青アクセント」へ
  戻したので、このスクリプトを実行すると却下されたデザインが復活する。走らせないこと。
  現行は scripts/works_dark_blue.py。ここは経緯の記録として残す。
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
works_light_theme.py — works 記事本文（JA/EN）のダークテーマを白青デザインへ機械変換する。

背景:
  works/index.html は 2026-08-26 に白青へリデザイン済み（b418e26）だが、記事本体は
  「白いヘッダー＋黒い本文」という過渡状態のまま残っていた。記事は共通テンプレから
  生成されており <style> の構造がほぼ同一なので、1本ずつ手で書き換えず、
  「色トークンの体系的マップ」として機械変換する（drift を作らないため）。

方針（ここが本スクリプトの契約）:
  1. 触るのは <style>...</style> の中身と <meta name="theme-color"> の値だけ。
     それ以外（本文テキスト・画像・動画・リンク・表・コード・OGP/meta/noindex/
     canonical/hreflang・<script>）は 1 バイトも変えない。--verify が保証する。
  2. :root のトークン名は据え置き、値だけ光背景用に差し替える。
     → var(--x) を使っている既存ルールがそのまま生きる（＝レイアウト無変更）。
  3. ハードコードされた色は「プロパティ種別（文字／地／罫線／影）」ごとに写像する。
     color:#fff は濃いインクへ、background:#fff は白のまま、という文脈依存が要るため。
  4. 映画モチーフ（フィルムグレイン／フィルムストリップ）は削除。
  5. 最後に共通オーバーライドを追記して、読み物としての体裁
     （本文16px/行間1.9・角丸6px・薄グレー地のコードブロック・罫線の表・
       accent 薄地のコールアウト）を index と揃える。

使い方:
  python scripts/works_light_theme.py --check    # 変換対象と差分規模を表示（書き込まない）
  python scripts/works_light_theme.py --write    # 変換して書き込む
  python scripts/works_light_theme.py --verify   # 本文（style 以外）が無傷か検査
"""
import re, os, sys, glob, argparse, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# リダイレクトスタブと管理画面は記事ではない
SKIP = {"index.html", "admin.html", "blog.html", "shibuya-ten-simulations.html"}

MARK = "/* ==== 白青リデザイン: 記事共通オーバーライド (works_light_theme.py 生成) ==== */"


def targets():
    out = []
    for pat in ("works/*.html", "en/works/*.html"):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.basename(f) in SKIP:
                continue
            out.append(f)
    return out


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


# ════════════════════════════════════════════════════════════════════════
# 色マップ
# ════════════════════════════════════════════════════════════════════════
# 記事は 2 系統のテンプレから出来ている:
#   A（post 型 / 20本）: --bg --surface --ink --body --sub --faint --line --line-2
#                         --brand --brand-ink --brand-bg --accent2 --code --note-* --warn-*
#   B（case 型 / chevron 2本）: --ink --bg --line --line-2 --accent --dim
# どちらも --ink が「明るい文字色」なので、光背景では濃いインクに反転する。

ROOT_A = (
    "--bg:#fff; --surface:#f7fafc; --ink:#101828; --body:#3c4a5a; --sub:#5c6b7a; --faint:#5f6f80;\n"
    "    --line:#d8e3ef; --line-2:#e8eef5; --btnline:#c9d7e5;\n"
    "    --brand:#1ea0c4; --brand-ink:#10586c; --brand-bg:rgba(30,160,196,.08);\n"
    "    --accent2:#0d6d8a; --accent2-bg:rgba(15,127,160,.08);\n"
    "    --code:#f4f7fa; --code-ink:#1f2937;\n"
    "    --note-bg:rgba(30,160,196,.07); --note-line:rgba(30,160,196,.35);\n"
    "    --warn-bg:rgba(180,83,9,.07); --warn-line:rgba(180,83,9,.38);"
)
ROOT_B = (
    "--ink:#101828;--bg:#fff;--line:#d8e3ef;--line-2:#e8eef5;--btnline:#c9d7e5;"
    "--accent:#10586c;--brand:#1ea0c4;--brand-ink:#10586c;--dim:#5c6b7a;"
    "--surface:#f7fafc;--sub:#5c6b7a;--body:#3c4a5a"
)

# 文字色（color / fill / stroke）
TEXT_MAP = {
    "#fff": "var(--ink)", "#ffffff": "var(--ink)", "white": "var(--ink)",
    "#fafaf6": "var(--ink)",
    "#000": "#fff", "#000000": "#fff", "black": "#fff",
    "rgba(255,255,255,.78)": "var(--body)",
    "rgba(255,255,255,.75)": "var(--body)",
    "rgba(255,255,255,.62)": "var(--dim)",
    "rgba(255,255,255,.56)": "var(--sub)",
    "rgba(255,255,255,.5)": "var(--sub)",
    "rgba(255,255,255,.36)": "var(--faint)",
    "#ffd9a8": "#9a3412",
}
# 地色（background / background-color / background-image）
BG_MAP = {
    "#fff": "#fff", "#ffffff": "#fff", "white": "#fff",
    "#000": "#eef3f8", "#000000": "#eef3f8", "black": "#eef3f8",
    "#111": "#eef3f8", "#060606": "var(--surface)", "#0c0c0e": "var(--surface)",
    "#15110c": "#fff7ed",
    "rgba(0,0,0,.82)": "rgba(255,255,255,.9)",
    "rgba(0,0,0,.4)": "rgba(15,23,42,.06)",
    "rgba(0,0,0,.5)": "rgba(15,23,42,.08)",
    "rgba(255,255,255,.02)": "rgba(15,23,42,.03)",
    "rgba(255,255,255,.04)": "rgba(15,23,42,.04)",
    "rgba(255,180,84,.3)": "rgba(30,160,196,.22)",
}
# 罫線（border* / outline*）
BORDER_MAP = {
    "#fff": "var(--line)", "#ffffff": "var(--line)", "white": "var(--line)",
    "rgba(255,255,255,.75)": "var(--btnline)",
    "rgba(255,255,255,.5)": "var(--btnline)",
    "rgba(255,255,255,.4)": "var(--btnline)",
    "rgba(255,255,255,.18)": "var(--line)",
    "rgba(255,255,255,.16)": "var(--line)",
    "rgba(255,255,255,.1)": "var(--line-2)",
    "rgba(255,255,255,.09)": "var(--line-2)",
    "rgba(255,255,255,.02)": "var(--line-2)",
}
# 影（box-shadow / text-shadow）
SHADOW_MAP = {
    "rgba(0,0,0,.35)": "rgba(15,23,42,.10)",
    "rgba(0,0,0,.8)": "rgba(15,23,42,.14)",
    "rgba(0,0,0,.5)": "rgba(15,23,42,.10)",
}
# どのプロパティでも一律に置く旧アクセント（琥珀 → 青）
GLOBAL_MAP = [
    ("#ffb454", "#1ea0c4"),
    ("#ff9f1c", "#10586c"),
    ("#ff8a4c", "#0d6d8a"),
    ("rgba(255,180,84,", "rgba(30,160,196,"),
    ("rgba(255,138,76,", "rgba(15,127,160,"),
    ("rgba(255,120,80,", "rgba(180,83,9,"),
]

# 映像の上に重なる UI は暗いままが正しい（白地に反転させると画が読めなくなる）
DARK_KEEP = (".lightbox", ".case-hero", ".ytfacade")

COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|\b(?:white|black)\b")


def prop_kind(prop):
    p = prop.strip().lower()
    if p in ("color", "fill", "stroke", "-webkit-text-fill-color", "caret-color",
             "text-decoration-color", "-webkit-text-stroke-color"):
        return "text"
    if p.startswith("background"):
        return "bg"
    if p.startswith("border") or p.startswith("outline"):
        return "border"
    if p.endswith("shadow"):
        return "shadow"
    return None


def map_decl(prop, value, rule_flags):
    """1宣言の色を写像する。rule_flags はルール全体から得た文脈。"""
    kind = prop_kind(prop)
    if kind is None:
        return value
    table = {"text": TEXT_MAP, "bg": BG_MAP, "border": BORDER_MAP, "shadow": SHADOW_MAP}[kind]

    # 反転ホバー（暗地 → 白地 + 黒文字）は、光背景では「濃紺地 + 白文字」に読み替える
    if rule_flags.get("invert_hover"):
        if kind == "bg":
            return re.sub(r"#fff\b|#ffffff\b|\bwhite\b", "var(--brand-ink)", value)
        if kind == "text":
            return re.sub(r"#000\b|#000000\b|\bblack\b", "#fff", value)
    # アクセント地の上の文字は白のまま
    if kind == "text" and rule_flags.get("accent_bg"):
        return re.sub(r"#000\b|#000000\b|\bblack\b|#fff\b|\bwhite\b", "#fff", value)

    def sub(m):
        tok = m.group(0)
        key = tok.lower()
        return table.get(key, tok)

    return COLOR_RE.sub(sub, value)


def split_decls(body):
    """ルール本体を [(raw_before, prop, sep, value)] 風に走査するための単純分割。
       url(data:...) や gradient の ; は含まれないので単純な split で足りるが、
       安全のため丸括弧の深さを見る。"""
    out, buf, depth = [], "", 0
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    out.append(buf)
    return out


def transform_rule(sel, body):
    if any(k in sel for k in DARK_KEEP):
        return body  # 映像上のオーバーレイは触らない

    flat = re.sub(r"\s+", "", body)
    flags = {
        "invert_hover": bool(re.search(r"background:#fff\b", flat)) and bool(re.search(r"color:#000\b", flat)),
        "accent_bg": bool(re.search(r"background(-color)?:(var\(--(brand|accent)\)|#1ea0c4)", flat)),
    }

    parts = []
    for d in split_decls(body):
        if ":" not in d or not COLOR_RE.search(d):
            parts.append(d)
            continue
        prop, sep, val = d.partition(":")
        if prop.strip().startswith("--"):
            parts.append(d)
            continue
        parts.append(prop + sep + map_decl(prop, val, flags))
    return ";".join(parts)


def walk_css(css):
    """トップレベル＆@media 1段を走査して各ルール本体を変換する。"""
    out, i, n, buf = [], 0, len(css), ""
    while i < n:
        ch = css[i]
        if ch == "{":
            sel = buf
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            body = css[i + 1:j - 1]
            bare = re.sub(r"/\*.*?\*/", "", sel, flags=re.S).strip()
            if bare.startswith("@") and "{" in body:
                new = walk_css(body)
            elif bare.startswith(("@keyframes", "@font-face", "@supports", "@media", "@container")):
                new = walk_css(body) if "{" in body else body
            else:
                new = transform_rule(bare, body)
            out.append(sel + "{" + new + "}")
            buf = ""
            i = j
        else:
            buf += ch
            i += 1
    out.append(buf)
    return "".join(out)


GRAIN_RE = re.compile(
    r"\n?\s*body::before\s*\{[^{}]*feTurbulence[^{}]*\}", re.S)


def new_root(m):
    """色トークンだけ差し替え、色でないトークン（--max / --radius / --sans / --mono 等）は
       元の宣言をそのまま残す。ここを丸ごと置き換えると本文幅とフォント指定が消える
       （実際に一度やって .wrap の max-width とフォントが飛んだ）。"""
    inner = m.group(1)
    palette = ROOT_A if "--brand" in inner else ROOT_B
    replaced = {d.split(":")[0].strip() for d in palette.split(";") if ":" in d}
    kept = []
    for d in inner.split(";"):
        name = d.split(":")[0].strip()
        if not name.startswith("--") or name in replaced:
            continue
        kept.append(d.strip())
    tail = ("\n    " + "; ".join(kept) + ";") if kept else ""
    return ":root{" + palette + tail + "}"


TAIL = """

""" + MARK + """
/* 読み物としての体裁を works/index.html（白青）と揃える。
   ここは「最後に効く」層なので、テンプレ側の値を上書きする用途だけに使うこと。 */
.filmstrip{display:none}                       /* 映画モチーフ（フィルムストリップ）は廃止 */
body{font-size:16px;line-height:1.9;font-weight:400;letter-spacing:0}
header.post .lead,.credit-card p,.data-cta p,.case-body .lead{font-weight:400}
article p,article li,.toc a,figcaption{letter-spacing:0}
article strong,.tblwrap td b,footer b,.spec dt,.callout b{color:var(--ink);font-weight:700}
h1,h2,h3{font-feature-settings:"palt"}
header.post h1{font-weight:800}
article h2{border-top:1px solid var(--line)}
::selection{background:rgba(30,160,196,.22);color:var(--ink)}

/* 画像・動画は index のカードと同じ言語（角丸6px＋薄い枠線） */
figure img,figure video,article img,.rthumb,.logo-chip,.refgrid img{border-radius:6px}
figure img,figure video{border:1px solid var(--line);background:#eef3f8}
figcaption{border-left:2px solid var(--line);color:var(--sub)}

/* コードブロックは薄グレー地の箱に。inline code は小さめの薄地チップ */
article .code{background:var(--code);border:1px solid var(--line);border-radius:6px;
  padding:16px 18px;margin:24px 0}
article .code pre{margin:0}
article .code code{background:none;border:0;padding:0;color:var(--code-ink);
  font-size:13.5px;line-height:1.8}
article code{background:#eef3f8;color:#1f2937;border:1px solid #e3ebf3;border-radius:4px}

/* 表：薄い罫線＋ヘッダは薄地 */
.tblwrap{border:1px solid #d8e3ec;border-radius:6px;background:#fff;overflow:hidden;overflow-x:auto}
.tblwrap th{background:#f2f7fb;color:var(--brand-ink);border-bottom:1px solid #d8e3ec}
.tblwrap td{border-bottom:1px solid #e8eef5}
.tblwrap td:first-child{color:var(--ink)}

/* コールアウト：note は accent 薄地、warn は琥珀寄りで役割を残す */
.callout{border-radius:6px;border-width:1px;border-style:solid}
.callout.note{background:rgba(30,160,196,.07);border-color:rgba(30,160,196,.35)}
.callout.warn{background:rgba(180,83,9,.07);border-color:rgba(180,83,9,.38)}

/* 箱もの一式の角丸を 6px に統一 */
.toc,.data-cta,.credit-card,.rcard,.spec,details.spec,.stepflow,.aiflow-tag,
.blogband,.tweetcard,.cat-card{border-radius:6px}
.toc,.data-cta,.stepflow,.spec{background:var(--surface);border:1px solid var(--line)}
.rcard{background:#fff;border:1px solid var(--line);box-shadow:0 10px 30px rgba(15,23,42,.05)}
.rcard:hover{border-color:rgba(30,160,196,.45);box-shadow:0 16px 40px rgba(15,23,42,.10)}
.rthumb{background:#eef3f8 center/cover no-repeat;border-bottom:1px solid var(--line)}

/* ボタン：白地では塗りの方が読みやすい（白文字 on #10586c ＝ 8:1） */
footer .cta,.data-cta .dc-btn,.watchmv,.credit-card .xbtn,.credit-team .xbtn{
  background:var(--brand-ink);border:1px solid var(--brand-ink);color:#fff}
footer .cta:hover,.data-cta .dc-btn:hover,.watchmv:hover,
.credit-card .xbtn:hover,.credit-team .xbtn:hover{
  background:#0c4557;border-color:#0c4557;color:#fff;text-decoration:none}
footer{background:var(--surface);border-top:1px solid var(--line)}

/* 映像の上に重なる UI は暗いまま残すので、アクセントは彩度の高い方を使う */
.case-hero .tag .dot,.ytfacade:hover .play{background:#1ea0c4}
.ytfacade:hover .play{border-color:#1ea0c4}

/* ライトボックスは画像を見る場所なので暗いまま。中の注記だけ白に戻す */
.lightbox .hint{color:rgba(255,255,255,.72)}
"""


def convert(text):
    m = re.search(r"(<style>)(.*?)(</style>)", text, re.S)
    if not m:
        return text, 0
    css = m.group(2)
    if MARK in css:
        return text, 0  # 変換済み（冪等）

    css = GRAIN_RE.sub("", css)                      # フィルムグレイン除去
    css = re.sub(r":root\s*\{(.*?)\}", new_root, css, count=1, flags=re.S)
    css = walk_css(css)
    for a, b in GLOBAL_MAP:
        css = css.replace(a, b)
    css = css.replace("--radius:3px", "--radius:6px")
    css += TAIL

    out = text[:m.start(2)] + css + text[m.end(2):]
    out = out.replace('<meta name="theme-color" content="#000000">',
                      '<meta name="theme-color" content="#ffffff">')
    return out, 1


def strip_style(text):
    """<style> と theme-color を除いた「本文」。これが変換前後で一致すれば内容無変更。"""
    t = text.replace("\r\n", "\n")
    t = re.sub(r"<style>.*?</style>", "<style/>", t, flags=re.S)
    t = t.replace('content="#000000"', 'content="#THEME"').replace('content="#ffffff"', 'content="#THEME"')
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()

    files = targets()
    if a.verify:
        # git の HEAD 版と比べて本文（style 以外）が無傷かを検査
        import subprocess
        bad = 0
        for f in files:
            rel = os.path.relpath(f, ROOT).replace("\\", "/")
            old = subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{rel}"],
                                 capture_output=True).stdout.decode("utf-8")
            new = read(f)
            if strip_style(old) != strip_style(new):
                bad += 1
                print("BODY CHANGED:", rel)
                for line in list(difflib.unified_diff(
                        strip_style(old).splitlines(), strip_style(new).splitlines(),
                        lineterm="", n=0))[:20]:
                    print("   ", line)
        print(f"verify: {len(files)} files, {bad} with body changes")
        return 1 if bad else 0

    n = 0
    for f in files:
        s = read(f)
        out, changed = convert(s)
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        if not changed:
            print(f"  skip (already converted): {rel}")
            continue
        n += 1
        if a.write:
            write(f, out)
            print(f"  wrote {rel}")
        else:
            print(f"  would convert {rel}  ({len(s)} -> {len(out)} bytes)")
    print(f"{'wrote' if a.write else 'would convert'}: {n}/{len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
