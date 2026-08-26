#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
works_dark_blue.py — works（実績＆ブログ）を「以前のダーク配色」へ戻し、
                     アンバー（黄〜オレンジ）だけテーマカラーの青 #1ea0c4 へ置き換える。

背景（本人指示 2026-08-16）:
  works は白青へ全面リデザインした（index=b418e26 / 記事22本=7a3ff41）。
  実物を見た本人の判断は「白色が見づらかった。以前の色構成に戻して、
  黄色だけテーマカラーの青に変更しよう」。よって:
    - 配色は元のダーク（黒地・白文字）。デザインそのものを履歴から戻す。
    - アクセントだけ 旧アンバー #ffb454 系 → 青 #1ea0c4 系。
    - URL・ファイル名・記事内容は一切変えない。

やり方（ここが本スクリプトの契約）:
  A) 記事22本 + blog スタブ2本
       白青化（7a3ff41）の直前の <style> ブロックだけを git から取り出して差し戻す。
       ⚠ファイル丸ごと checkout はしない。7a3ff41 より後の本文修正
         （d8733f2 = EN記事の画像パス404修正）が消えるため。
         触るのは <style>…</style> の中身と <meta name="theme-color"> だけ。
  B) index 2本（works/index.html, en/works/index.html）
       b418e26 はマークアップごと作り替えている（.cta-panel / .site-foot /
       .b.work / .more は旧CSSに存在せず、逆に .tcr / .kick / .big /
       .filmstrip は新マークアップに存在しない）。よって style だけ戻すと
       壊れる。ここだけは b418e26 の親からファイル全体を戻す。
       ヘッダーは戻したあとに scripts/sync_header.py --write が正規版を再生成する。
  最後に、戻した CSS へ「アンバー→青」の色マップを一括で当てる。

色マップ:
    #ffb454              → #1ea0c4   ブランド/アクセント（黒地でコントラスト 6.9:1）
    #ff9f1c              → #5ec8e8   アンバーの派生（進捗バーのグラデ終端など）
    #ff8a4c (accent2)    → #5ec8e8   第2アクセント（site-header.css の hover 色と同値）
    #ffd9a8              → #bfe6f2   淡いアンバー文字 → 淡い青
    rgba(255,180,84,α)   → rgba(30,160,196,α)
    rgba(255,138,76,α)   → rgba(94,200,232,α)
  据え置き（アンバーではなく「役割」の色なので変えない）:
    rgba(255,120,80,α)   警告コールアウト（--warn-bg / --warn-line）
    #f87171 / rgba(248,113,113,α)   エラー・否定の赤

使い方:
  python scripts/works_dark_blue.py --check    # 変換対象と差分規模（書き込まない）
  python scripts/works_dark_blue.py --write    # 書き込む
  python scripts/works_dark_blue.py --verify   # 本文（style 以外）が HEAD と同一か検査
  python scripts/works_dark_blue.py --audit    # 変換後ファイルにアンバーが残っていないか
"""
import re, os, sys, glob, argparse, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 記事の白青化コミット 7a3ff41 の直前 / index の白青化コミット b418e26 の直前
REV_ARTICLE = "7a3ff41^"
REV_INDEX = "b418e26^"

# 記事ではないページ。admin はサイト非公開の管理画面、shibuya-* は <style> の無い
# リダイレクトスタブなので触らない。
SKIP = {"admin.html", "shibuya-ten-simulations.html"}
INDEX_FILES = {"works/index.html", "en/works/index.html"}

# 白青化スクリプトが CSS 末尾に書き込んだ目印。残っていたら戻し損ねている。
LIGHT_MARK = "白青リデザイン: 記事共通オーバーライド"

# index がすでにダーク（＝b418e26^ 由来のマークアップ）であることの目印。
# 白青版には .filmstrip が無い（代わりに .site-foot）。
DARK_INDEX_MARK = '<div class="filmstrip"></div>'

# ── アンバー → 青 ─────────────────────────────────────────────────
COLOR_MAP = [
    (r"rgba\(\s*255\s*,\s*180\s*,\s*84\s*,", "rgba(30,160,196,"),
    (r"rgba\(\s*255\s*,\s*138\s*,\s*76\s*,", "rgba(94,200,232,"),
    (r"#ffb454\b", "#1ea0c4"),
    (r"#ff9f1c\b", "#5ec8e8"),
    (r"#ff8a4c\b", "#5ec8e8"),
    (r"#ffd9a8\b", "#bfe6f2"),

    # ── 極小メタ文字の明度（2026-08-16 本人指示「極小メタ文字を明るく」） ──
    # 日付・所要時間・COMING SOON・WORKFLOW帯など 10〜11px のメタ文字が黒地で
    # 3.06〜3.28:1 しかなく AA(4.5:1) を割っていた。白 55% ＝ 約6.2:1 へ。
    (r"(--faint\s*:\s*)rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*\.36\s*\)",
     r"\g<1>rgba(255,255,255,.55)"),                       # 記事22本の --faint
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*\.35\s*\)",
     "rgba(255,255,255,.55)"),                             # index: .thumb のプレースホルダ文字
    (r"(text-transform:uppercase;)opacity:\.4;",
     r"\g<1>opacity:.55;"),                                # index: .tcr / .foot の帯
]
# 変換後に 1 つでも残っていたら失敗とみなす色
FORBIDDEN = [r"#ffb454\b", r"#ff9f1c\b", r"#ff8a4c\b", r"#ffd9a8\b",
             r"rgba\(\s*255\s*,\s*180\s*,\s*84\s*,", r"rgba\(\s*255\s*,\s*138\s*,\s*76\s*,",
             # AA を割る旧メタ文字の明度（上の色マップで潰したもの）
             r"--faint\s*:\s*rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*\.36\s*\)",
             r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*\.35\s*\)",
             r"text-transform:uppercase;opacity:\.4;"]


def rel_targets():
    out = []
    for pat in ("works/*.html", "en/works/*.html"):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.basename(f) in SKIP:
                continue
            rel = os.path.relpath(f, ROOT).replace("\\", "/")
            out.append(rel)
    return out


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as f:
        return f.read()


def write(rel, s):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as f:
        f.write(s)


def git_show(rev, rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, rel)],
                       capture_output=True)
    if r.returncode:
        raise SystemExit("git show %s:%s failed: %s" % (rev, rel, r.stderr.decode()))
    return r.stdout.decode("utf-8")


def nl_of(text):
    """そのファイルの支配的な改行（sync_header.py と同じ規則）。"""
    crlf = text.count("\r\n")
    return "\r\n" if crlf and crlf * 2 >= text.count("\n") else "\n"


def recolor(css):
    for pat, rep in COLOR_MAP:
        css = re.sub(pat, rep, css, flags=re.I)
    return css


STYLE_RE = re.compile(r"(<style>)(.*?)(</style>)", re.S)


def convert(rel, cur):
    """戻したあとの全文を返す。"""
    if rel in INDEX_FILES:
        # index はマークアップごと戻す（style だけ戻すと旧CSS↔新マークアップで壊れる）。
        # ただし「すでにダーク」なら現物を使う。戻したあとに入れた手入れ
        # （CTAパネル／実績カードの「実績を見る →」= 2026-08-16）を消さないため。
        out = cur if DARK_INDEX_MARK in cur else git_show(REV_INDEX, rel)
        out = STYLE_RE.sub(lambda m: m.group(1) + recolor(m.group(2)) + m.group(3), out, count=1)
    else:
        old = git_show(REV_ARTICLE, rel)
        mo = STYLE_RE.search(old)
        mc = STYLE_RE.search(cur)
        if not mo or not mc:
            raise SystemExit("no <style> in %s" % rel)
        css = recolor(mo.group(2))
        css = css.replace("\r\n", "\n").replace("\n", nl_of(cur))
        out = cur[:mc.start(2)] + css + cur[mc.end(2):]
    out = out.replace('<meta name="theme-color" content="#ffffff">',
                      '<meta name="theme-color" content="#000000">')
    return out


# ── 検査 ───────────────────────────────────────────────────────────
HEADER_RE = re.compile(r'<header class="site-header[^"]*">.*?</header>', re.S)
HEADERLINK_RE = re.compile(r'<link rel="stylesheet" href="/assets/[a-z-]+\.css(?:\?v=[0-9a-f]+)?">')


def strip_style(text):
    """<style> / theme-color / ヘッダーを除いた「本文」。
       ここが変換前後で一致すれば、記事の中身（テキスト・画像・動画・リンク・表・
       コード・OGP/meta/noindex/canonical/hreflang・<script>）は無変更。
       ヘッダーと共有CSSリンクは scripts/sync_header.py が生成する機械の領分なので
       除外する（そちらは sync_header.py --check が 0 drifted で担保する）。"""
    t = text.replace("\r\n", "\n")
    t = STYLE_RE.sub("<style/>", t)
    t = HEADER_RE.sub("<header/>", t)
    t = HEADERLINK_RE.sub("<headerlink/>", t)
    t = t.replace('content="#000000"', 'content="#THEME"').replace('content="#ffffff"', 'content="#THEME"')
    return t


def cmd_verify():
    bad = 0
    for rel in rel_targets():
        if rel in INDEX_FILES:
            continue  # index はマークアップごと戻すので対象外（意図的な本文変更）
        old = git_show("HEAD", rel)
        new = read(rel)
        a, b = strip_style(old), strip_style(new)
        if a != b:
            bad += 1
            print("BODY CHANGED:", rel)
            import difflib
            for line in list(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                                  lineterm="", n=0))[:20]:
                print("   ", line)
    print("verify: %d files (index 2本を除く), %d with body changes"
          % (len(rel_targets()) - len(INDEX_FILES), bad))
    return 1 if bad else 0


def cmd_audit():
    bad = 0
    for rel in rel_targets():
        t = read(rel)
        hits = []
        for pat in FORBIDDEN:
            hits += re.findall(pat, t, flags=re.I)
        if LIGHT_MARK in t:
            hits.append("<白青オーバーライドが残存>")
        if hits:
            bad += 1
            print("AMBER LEFT:", rel, hits[:6])
    # ヘッダーCSSも見る（works 系のみ）
    hp = os.path.join(ROOT, "assets", "works-header.css")
    hcss = re.sub(r"/\*.*?\*/", "", open(hp, encoding="utf-8").read(), flags=re.S)
    for pat in FORBIDDEN:
        if re.search(pat, hcss, flags=re.I):
            bad += 1
            print("AMBER LEFT: assets/works-header.css", pat)
    print("audit: %d files, %d with amber residue" % (len(rel_targets()), bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--audit", action="store_true")
    a = ap.parse_args()
    if a.verify:
        return cmd_verify()
    if a.audit:
        return cmd_audit()

    n = 0
    for rel in rel_targets():
        cur = read(rel)
        out = convert(rel, cur)
        if out == cur:
            print("  skip (already dark): %s" % rel)
            continue
        n += 1
        if a.write:
            write(rel, out)
            print("  wrote %s  (%d -> %d bytes)" % (rel, len(cur), len(out)))
        else:
            print("  would convert %s  (%d -> %d bytes)" % (rel, len(cur), len(out)))
    print("%s: %d/%d files" % ("wrote" if a.write else "would convert", n, len(rel_targets())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
