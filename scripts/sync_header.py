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
# works 系だけ白基調ヘッダー（2026-08-16 サイト統合）。
# manifesto/data/demo 等は後日301で消えるまで従来の黒ヘッダーのまま据え置くため、
# CSSもマークアップも系統ごと分ける（1ファイルに同居させない）。
WORKS_CSS = "assets/works-header.css"

def is_works(rel):
    """works/ と en/works/ 配下か。ヘッダーの系統はこれだけで決まる。"""
    return rel.startswith("works/") or rel.startswith("en/works/")

# ヘッダーを持つページのみ（リダイレクトスタブ等は対象外）
def target_pages():
    pats = ["locahun3d_*.html", "en/locahun3d_*.html", "works/*.html", "en/works/*.html"]
    out = []
    for p in pats:
        for f in sorted(glob.glob(os.path.join(ROOT, p))):
            t = read(f)
            # クラスは前方一致で拾う（"site-header" / "site-header sh-works" の両系統）
            if '<header class="site-header' in t:
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
# ⚠ 「オンライン」トグルの飛び先は**オンライン版のトップ**にする（2026-08-13）。
#    以前は /properties(カタログ)直行だったため、スキャンサイトのどこからも
#    https://locahun3d.com/ のトップページへ行けなかった（ユーザー報告）。
#    カタログはトップからも上部ナビからも1クリックで届く。
ONLINE_URL = {"ja": "https://locahun3d.com/", "en": "https://locahun3d.com/en"}
# ⚠ ブランドロゴのリンク先は「自サイトのトップ」。以前は ONLINE_URL を使っており、
#    スキャンサイトでロゴを押すとオンライン版へ飛んでしまっていた（ユーザー報告）。
#    サイト間の移動はスキャン/オンラインのトグルが担当する役割分担。
BRAND_HOME = {"ja": "/", "en": "/en/"}
LANG_CHIP = {"ja": "EN", "en": "JA"}
MENU_LABEL = {"ja": "メニュー", "en": "Menu"}
ACCT_LABEL = {"ja": "言語・アカウント", "en": "Language & account"}

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
    # ● (言語・アカウント) ボタンは 2026-08-12 に廃止。スキャンサイトには
    # ログイン機能が無く「押しても意味のないボタン」だったため（ユーザー指摘）。
    # EN チップは .sh-center 列4 に常時表示へ変更（CSS 側の <1024px 非表示を撤去）。
    return (
        '<header class="site-header">\n'
        '%s'
        '  <div class="sh-left" id="sh-nav">\n'
        '    <nav>\n%s\n'
        '    </nav>\n'
        # 375px未満はバーにスキャン/オンラインのトグルが入らない（実測360pxで☰×ブランド-6.9px）。
        # ●パネル廃止後の退避先はこのドロワー内。CSSの .sh-drawer-toggle が
        # ≤374px かつ sh-open の時だけ表示する。
        '    <div class="sh-toggle sh-drawer-toggle">\n'
        '      <span class="sh-active">%s</span>\n'
        '      <a href="%s">%s</a>\n'
        '    </div>\n'
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
        '  <div class="sh-right"></div>\n'
        '</header>'
    ) % (hb, nav,
         SCAN_LABEL[lang], ONLINE_URL[lang], ONLINE_LABEL[lang],
         BRAND_HOME[lang], BRAND_SVG, BRAND_TEXT[lang], SCAN_LABEL[lang],
         ONLINE_URL[lang], ONLINE_LABEL[lang], counterpart(relpath, lang), LANG_CHIP[lang])

# ---------- 白基調ヘッダー（works 専用マークアップ） ----------
# ブランドマークは黒ヘッダーと同じ形。色だけ白地用（枠=ink / 中心=accent）へ。
WORKS_BRAND_SVG = ('<svg viewBox="0 0 64 64" width="20" height="20" aria-hidden="true">'
                   '<g fill="none" stroke="#14181c" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
                   '<path d="M14 23V14H23"/><path d="M41 14H50V23"/><path d="M14 41V50H23"/><path d="M50 41V50H41"/></g>'
                   '<circle cx="32" cy="32" r="7" fill="none" stroke="#1ea0c4" stroke-width="3"/>'
                   '<circle cx="32" cy="32" r="2.4" fill="#1ea0c4"/></svg>')

# ⚠ works のヘッダーは「オンライン版 locahun3d.com のナビ」を絶対URLで指す。
#    スキャン/オンラインのトグルは置かない（分岐そのものを廃止するため）。
WORKS_NAV = {
    "ja": [("https://locahun3d.com/properties", "物件を探す"),
           ("https://locahun3d.com/pricing", "料金"),
           ("https://locahun3d.com/about", "サービスについて"),
           ("https://locahun3d.com/demo", "デモ"),
           ("https://locahun3d.com/contact", "お問い合わせ")],
    "en": [("https://locahun3d.com/en/properties", "Locations"),
           ("https://locahun3d.com/en/pricing", "Pricing"),
           ("https://locahun3d.com/en/about", "About"),
           ("https://locahun3d.com/en/demo", "Demo"),
           ("https://locahun3d.com/en/contact", "Contact")],
}
# ブランドの飛び先はオンライン版のトップ（works は locahun3d.com の一部として振る舞う）。
WORKS_BRAND_HOME = {"ja": "https://locahun3d.com/", "en": "https://locahun3d.com/en"}
WORKS_BRAND_SUB = {"ja": "実績＆ブログ", "en": "Work &amp; Blog"}

def works_header_markup(relpath, lang):
    nav = "\n".join('        <a href="%s">%s</a>' % (href, label)
                    for href, label in WORKS_NAV[lang])
    return (
        '<header class="site-header sh-works">\n'
        '  <a href="%s" class="sh-brand">\n'
        '    %s\n'
        '    <span class="sh-brand-text">%s</span>\n'
        '    <span class="sh-brand-sub">%s</span>\n'
        '  </a>\n'
        # 静的HTMLなので開閉状態は .site-header への class 付け外し（inline onclick）で持つ。
        '  <button class="sh-hb" type="button" aria-label="%s" aria-expanded="false"'
        ' aria-controls="sh-nav" onclick="var h=this.closest(\'.site-header\');'
        'var o=h.classList.toggle(\'sh-open\');this.setAttribute(\'aria-expanded\',o)">'
        '<i></i><i></i><i></i></button>\n'
        '  <div class="sh-nav" id="sh-nav">\n'
        '    <nav>\n%s\n'
        '    </nav>\n'
        '    <a class="sh-lang" href="%s">%s</a>\n'
        '  </div>\n'
        '</header>'
    ) % (WORKS_BRAND_HOME[lang], WORKS_BRAND_SVG, BRAND_TEXT[lang], WORKS_BRAND_SUB[lang],
         MENU_LABEL[lang], nav, counterpart(relpath, lang), LANG_CHIP[lang])

# クラスは "site-header" 前方一致（"site-header sh-works" も拾う）。
HEADER_RE = re.compile(r'<header class="site-header[^"]*">.*?</header>', re.S)

def link_re(css):
    return re.compile(r'<link rel="stylesheet" href="/%s(?:\?v=[0-9a-f]+)?">' % re.escape(css))

def css_version(css):
    """共有CSSの内容ハッシュ。CSSを変更すると自動でURLが変わりキャッシュを破棄できる
       （サイト既存の favicon.svg?v=3 と同じ規約。バージョン手動更新は忘れるので内容から導出する）。"""
    with open(os.path.join(ROOT, css), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def link_tag(css):
    return '<link rel="stylesheet" href="/%s?v=%s">' % (css, css_version(css))

def ensure_link(html, css):
    # 相手系統のCSSリンクは剥がす（works へ切り替えたページに黒ヘッダーCSSを残さない）。
    other = SHARED_CSS if css == WORKS_CSS else WORKS_CSS
    html = re.sub(link_re(other).pattern + r'\r?\n?', "", html)
    tag = link_tag(css)
    if link_re(css).search(html):
        return link_re(css).sub(lambda _: tag, html, count=1)  # 版が古ければ貼り替え
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
    works = is_works(rel)
    out = strip_header_css(src)
    out = ensure_link(out, WORKS_CSS if works else SHARED_CSS)
    nl = nl_of(src)
    markup = (works_header_markup if works else header_markup)(rel, lang)
    out = HEADER_RE.sub(lambda m: markup.replace("\n", nl), out, count=1)
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
