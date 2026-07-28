#!/usr/bin/env python3
"""
sync_header.py — スキャンサイトのヘッダーを「1つのソース」から全ページへ同期する。

背景: ヘッダーCSS(約60行)とマークアップ(約24行)が全ページにコピペされており、
ページごとに値がdrift（.sh-left gap 28px vs 16px、nav 13px vs 12px 等）していた。
結果「ページによって文字サイズや幅が変わる」。この仕組みで構造的に再発を止める。

  正典CSS      : assets/site-header.css        （全ページが <link> で共有＝物理的にdrift不能）
  正典マークアップ: 本スクリプト内 NAV/HEADER   （--write で全ページへ再生成）

使い方:
  python scripts/sync_header.py --extract   # 現状のヘッダーCSSを抽出（正典CSS作成用）
  python scripts/sync_header.py --check     # driftがあれば exit 1（デプロイ前チェック）
  python scripts/sync_header.py --write     # 全ページへ同期
"""
import re, sys, glob, os, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_CSS = "assets/site-header.css"

# ヘッダーを持つページのみ（リダイレクトスタブ等は対象外）
def target_pages():
    pats = ["locahun3d_*.html", "en/locahun3d_*.html", "works/*.html", "en/works/*.html"]
    out = []
    for p in pats:
        for f in sorted(glob.glob(os.path.join(ROOT, p))):
            t = read(f)
            if '<header class="site-header"' in t:
                out.append(f)
    return out

def nl_of(text):
    """そのファイルの支配的な改行を返す（生成物を混在させると偽のdriftになる）。"""
    crlf = text.count("\r\n")
    return "\r\n" if crlf and crlf * 2 >= text.count("\n") else "\n"

def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()

def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

# ---------- CSS パーサ（波括弧対応・@media入れ子1段） ----------
def split_rules(css):
    """css を [(selector_or_at, body, raw)] に分割。トップレベルのみ。"""
    rules, i, n = [], 0, len(css)
    buf = ""
    while i < n:
        ch = css[i]
        if ch == "{":
            sel = buf.strip()
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{": depth += 1
                elif css[j] == "}": depth -= 1
                j += 1
            body = css[i + 1:j - 1]
            rules.append((sel, body, buf + "{" + body + "}"))
            buf = ""
            i = j
        else:
            buf += ch
            i += 1
    if buf.strip():
        rules.append((None, None, buf))  # 末尾のコメント等
    return rules

def bare(sel):
    """セレクタからコメントを除いた実体。@media判定にも必ずこれを使うこと
       （コメントが前置された @media を見落とすと、その中のヘッダーCSSが
         ページ内に residue として残り『唯一のソース』が破れる — 実際に起きた）。"""
    return re.sub(r"/\*.*?\*/", "", sel or "", flags=re.S).strip()

# .site-header のみに前方一致（.site-header-promo のような別クラスを巻き込まない）
HEADER_PREFIX = re.compile(r"^\.site-header(?![\w-])")

def is_header_sel(sel):
    s = bare(sel)
    if not s or s.startswith("@"): return False
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return bool(parts) and all(HEADER_PREFIX.match(p) for p in parts)

def mixed_header_sels(css):
    """`.site-header` を含むのに除去対象にならないセレクタ（混在リスト・祖先付き等）を列挙。
       残しても壊れはしないが、ページ側からヘッダーを上書きし得る再発チャネルなので警告する。"""
    out = []
    for sel, body, raw in split_rules(css):
        s = bare(sel)
        if not s: continue
        if s.startswith("@"):
            out += mixed_header_sels(body)
        elif ".site-header" in s and not is_header_sel(sel):
            out.append(re.sub(r"\s+", " ", s))
    return out

def partition_css(css):
    """(header_css, rest_css) に分ける。@media / @supports / @container 内も再帰的に。"""
    head, rest = [], []
    for sel, body, raw in split_rules(css):
        if sel is None:
            rest.append(raw); continue
        s = bare(sel)
        if s.startswith(("@media", "@supports", "@container")):
            h, r = partition_css(body)
            if h.strip(): head.append(sel + "{" + h + "}")
            if r.strip(): rest.append(sel + "{" + r + "}")
        elif is_header_sel(sel):
            head.append(raw)
        else:
            rest.append(raw)
    return "".join(head), "".join(rest)

STYLE_RE = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.S)

def extract_header_css(html):
    out = []
    for m in STYLE_RE.finditer(html):
        h, _ = partition_css(m.group(2))
        if h.strip(): out.append(h)
    return "".join(out)

def strip_header_css(html):
    def repl(m):
        head, rest = partition_css(m.group(2))
        # ヘッダーCSSが無い<style>は一切書き換えない。
        # 再構築するとページ固有CSSの空白まで正規化され、ページCSSを手で編集するたび
        # --check が「drift」と誤検知する（driftの検査器が無関係な整形を強制してしまう）。
        if not head.strip():
            return m.group(0)
        return m.group(1) + rest + m.group(3)
    return STYLE_RE.sub(repl, html)

# ---------- 正典マークアップ ----------
BRAND_SVG = ('<svg viewBox="0 0 64 64" width="22" height="22" aria-hidden="true">'
             '<g fill="none" stroke="#f4f1ea" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
             '<path d="M14 23V14H23"/><path d="M41 14H50V23"/><path d="M14 41V50H23"/><path d="M50 41V50H41"/></g>'
             '<circle cx="32" cy="32" r="7" fill="none" stroke="#ffb454" stroke-width="3"/>'
             '<circle cx="32" cy="32" r="2.4" fill="#ffb454"/></svg>')

NAV = {
    "ja": [("0.1", "/locahun3d_manifesto.html", "マニフェスト"),
           ("0.2", "/locahun3d_data.html", "データ活用"),
           ("0.3", "/works/index.html", "実績＆ブログ"),
           ("0.4", "/locahun3d_demo.html", "デモ・お問合せ")],
    "en": [("0.1", "/en/locahun3d_manifesto.html", "Manifesto"),
           ("0.2", "/en/locahun3d_data.html", "Data &amp; Uses"),
           ("0.3", "/en/works/index.html", "Work &amp; Blog"),
           ("0.4", "/en/locahun3d_demo.html", "Demo &amp; Contact")],
}
BRAND_TEXT = {"ja": "ロケハン3D", "en": "Locahun 3D"}
SCAN_LABEL = {"ja": "スキャン", "en": "Scan"}
ONLINE_LABEL = {"ja": "オンライン", "en": "Online"}
ONLINE_URL = {"ja": "https://locahun3d.com/properties", "en": "https://locahun3d.com/en/properties"}
LANG_CHIP = {"ja": "EN", "en": "JA"}
MENU_LABEL = {"ja": "メニュー", "en": "Menu"}

def counterpart(relpath, lang):
    """JA<->EN の対応ページを返す（無ければトップ）。"""
    p = relpath.replace("\\", "/")
    other = ("en/" + p) if lang == "ja" else p[3:]
    return "/" + other if os.path.exists(os.path.join(ROOT, other)) else (
        "/en/locahun3d_manifesto.html" if lang == "ja" else "/locahun3d_manifesto.html")

def header_markup(relpath, lang):
    nav = "\n".join(
        '      <a href="%s"><span class="code">%s</span>%s</a>' % (href, code, label)
        for code, href, label in NAV[lang])
    # ハンバーガー: タブレット縦(720–1023px)でだけ CSS で表示される。
    # 他の帯では .sh-hb{display:none} のまま＝スマホ/PCの見た目は不変。
    # 静的HTMLなので状態は .site-header へ class を付け外しするだけの inline onclick で持つ。
    hb = ('  <button class="sh-hb" type="button" aria-label="%s" aria-expanded="false"'
          ' aria-controls="sh-nav" onclick="var h=this.closest(\'.site-header\');'
          'var o=h.classList.toggle(\'sh-open\');this.setAttribute(\'aria-expanded\',o)">'
          '<i></i><i></i><i></i></button>\n') % MENU_LABEL[lang]
    return (
        '<header class="site-header">\n'
        '%s'
        '  <div class="sh-left" id="sh-nav">\n'
        '    <nav>\n%s\n'
        # 480px未満はバーからENを外すので、代わりに同じリンクをドロワー内へ置く。
        # CSS 側で .sh-drawer-lang は既定 display:none、その帯だけ表示する。
        '      <a class="sh-drawer-lang" href="%s">%s</a>\n'
        '    </nav>\n'
        '  </div>\n'
        '  <div class="sh-center">\n'
        '    <a href="%s" class="sh-brand">\n'
        '      %s\n'
        '      <span class="sh-brand-text">%s</span>\n'
        '    </a>\n'
        '    <div class="sh-toggle">\n'
        '      <span class="sh-active">%s</span>\n'
        '      <a href="%s">%s</a>\n'
        '    </div>\n'
        '    <div class="sh-toggle sh-lang">\n'
        '      <a href="%s">%s</a>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="sh-right" aria-hidden="true"></div>\n'
        '</header>'
    ) % (hb, nav, counterpart(relpath, lang), LANG_CHIP[lang],
         ONLINE_URL[lang], BRAND_SVG, BRAND_TEXT[lang], SCAN_LABEL[lang],
         ONLINE_URL[lang], ONLINE_LABEL[lang], counterpart(relpath, lang), LANG_CHIP[lang])

HEADER_RE = re.compile(r'<header class="site-header">.*?</header>', re.S)
LINK_RE = re.compile(r'<link rel="stylesheet" href="/%s(?:\?v=[0-9a-f]+)?">' % re.escape(SHARED_CSS))

def css_version():
    """共有CSSの内容ハッシュ。CSSを変更すると自動でURLが変わりキャッシュを破棄できる
       （サイト既存の favicon.svg?v=3 と同じ規約。バージョン手動更新は忘れるので内容から導出する）。"""
    with open(os.path.join(ROOT, SHARED_CSS), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def link_tag():
    return '<link rel="stylesheet" href="/%s?v=%s">' % (SHARED_CSS, css_version())

def ensure_link(html):
    tag = link_tag()
    if LINK_RE.search(html):
        return LINK_RE.sub(lambda _: tag, html, count=1)  # 版が古ければ貼り替え
    # 既存のフォント <link> の直後、無ければ </head> の直前に差し込む
    m = list(re.finditer(r'<link[^>]+fonts\.googleapis[^>]*>', html))
    if m:
        i = m[-1].end()
        return html[:i] + "\n" + tag + html[i:]
    return html.replace("</head>", tag + "\n</head>", 1)

def process(path, mode):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    lang = "en" if rel.startswith("en/") else "ja"
    src = read(path)
    out = strip_header_css(src)
    out = ensure_link(out)
    nl = nl_of(src)
    out = HEADER_RE.sub(lambda m: header_markup(rel, lang).replace("\n", nl), out, count=1)
    changed = out != src
    if changed and mode == "write":
        write(path, out)
    return rel, changed

def main():
    mode = ("extract" if "--extract" in sys.argv else
            "write" if "--write" in sys.argv else "check")
    pages = target_pages()
    if mode == "extract":
        for p in pages:
            css = extract_header_css(read(p))
            print("/* ===== %s (%d chars, md5 %s) ===== */"
                  % (os.path.relpath(p, ROOT), len(css), hashlib.md5(css.encode()).hexdigest()[:8]))
        return 0
    drifted = [rel for rel, ch in (process(p, mode) for p in pages) if ch]
    print("%s: %d pages, %d %s" % (mode, len(pages), len(drifted),
                                   "drifted" if mode == "check" else "updated"))
    for d in drifted: print("   ", d)
    return 1 if (mode == "check" and drifted) else 0

if __name__ == "__main__":
    sys.exit(main())
