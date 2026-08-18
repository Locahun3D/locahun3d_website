#!/usr/bin/env python3
"""
sync_ogp.py — works配下（実績＆技術ブログ）のOGP/Twitterカードを生成・同期する。

背景: works の記事・一覧には OGP が1つも無く、SNSやチャットにURLを貼っても
og:image が無いため「画像なしの小さいテキスト型プレビュー」になっていた
（本体ページ locahun3d_*.html には元からOGPがある）。営業・PRで共有するURLなので
記事ごとにアイキャッチを持たせて大きなカードで出す。

  python scripts/sync_ogp.py --check   # 差分があれば exit 1
  python scripts/sync_ogp.py --write   # 反映

新しい記事を足したら EYECATCH に1行足すだけ。指定が無ければブランド共通画像になる。
"""
import os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://web.locahun3d.com"
BRAND_OG = ("/assets/Digiloke_OG_Cover.jpg", 1200, 630)

# slug -> (画像パス, 幅, 高さ)。記事本文の代表画像を使う（自前ホストのみ／外部ホットリンク禁止）
EYECATCH = {
    "chevron-rokunowa-mv":            ("/works/images/work04_bgfix.jpg", 1500, 844),
    "houdini-comfyui-gsplat-workflow":("/works/images/hectorvfx_shibuya_ai_render.jpg", 2764, 1536),
    "portalcam-drone-ai-workflow":    ("/works/images/work03_poster.jpg", 1280, 720),
    "ue5-xgrids-3dgs-aerial-ai":      ("/works/images/ue5_shibuya_ground_day.jpg", 1575, 824),
    "isaacsim-3dgs-import":           ("/works/images/isaacsim_shibuya_walk.jpg", 1920, 1080),
    "3dgs-lidar-denoise":             ("/works/images/shibuya_hero.jpg", 1280, 720),
    "isaacsim-3dgs-robot-demos":      ("/works/images/shibuya_lidar_hero.jpg", 1280, 720),
    "shibuya-ten-simulations":        ("/works/images/shibuya_sim06_visibility_v1.jpg", 1040, 680),
    "3dgs-file-formats":              ("/works/images/format-og-cover.jpg", 1200, 630),
    "3dgs-software-comparison":       ("/works/images/dcc-og-cover.jpg", 1200, 630),
    "portalcam-xbin-raw-extraction":  ("/works/images/xbin_cam_pinholeA.jpg", 1100, 825),
}

START, END = "<!-- OGP:START (scripts/sync_ogp.py が生成。直接編集しない) -->", "<!-- OGP:END -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)

def nl_of(text):
    """そのファイルの支配的な改行を返す。生成ブロックを混在させると
       ファイルは同一内容なのに --check が毎回 drift と報告する。"""
    crlf = text.count("\r\n")
    return "\r\n" if crlf and crlf * 2 >= text.count("\n") else "\n"

def read(p):
    with open(p, encoding="utf-8", newline="") as f: return f.read()

def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(s)

def pages():
    out = []
    for d in ("works", "en/works"):
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if not name.endswith(".html") or name in ("blog.html", "admin.html"):
                continue
            out.append(f"{d}/{name}")
    return out

def meta(htm, name=None, prop=None):
    pat = (r'<meta[^>]+name=["\']%s["\'][^>]*content=["\']([^"\']*)["\']' % name if name
           else r'<meta[^>]+property=["\']%s["\'][^>]*content=["\']([^"\']*)["\']' % prop)
    m = re.search(pat, htm, re.I)
    return m.group(1).strip() if m else ""

def first_img_alt(htm):
    m = re.search(r'<img[^>]+alt=["\']([^"\']+)["\']', htm, re.I)
    return m.group(1).strip() if m else ""

BRANDS = ("ロケハン3D", "Locahun 3D", "LOCAHUN 3D")

def short_title(htm):
    """<title> からサイト名を落とし、プレビュー用の短い見出しにする。
       <title> はSEO用に長く、そのままだとチャット側で途中切れするため。
       JAは「記事名｜ロケハン3D …」、ENは「Locahun 3D｜Works …」と語順が逆なので
       位置ではなく『ブランド名を含む区画を捨てる』方式にする（先頭決め打ちは誤る）。"""
    m = re.search(r"<title>(.*?)</title>", htm, re.S | re.I)
    t = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    parts = [p.strip() for p in re.split(r"\s*[｜|]\s*", t) if p.strip()]
    keep = [p for p in parts if not any(b in p for b in BRANDS)]
    out = " ｜ ".join(keep) if keep else t
    # 「記事名 — ロケハン3D 制作実績」のようにダッシュ以降がブランド説明の場合も落とす
    out = re.sub(r"\s*[—–―ー]+\s*(?:%s)\b.*$" % "|".join(map(re.escape, BRANDS)), "", out).strip()
    return out or t

def canonical(htm, rel):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', htm, re.I)
    return m.group(1) if m else f"{SITE}/{rel}"

def build(rel, htm):
    slug = os.path.basename(rel)[:-5]
    en = rel.startswith("en/")
    img, w, h = EYECATCH.get(slug, BRAND_OG)
    is_index = slug == "index"
    # 抽出元は既にHTMLエスケープ済みなので、必ず一度戻してから出力する
    # （戻さないと "&amp;" が "&amp;amp;" になり、プレビューに &amp; と表示される）
    title = html.unescape(short_title(htm))
    desc = html.unescape(meta(htm, name="description"))
    alt = "" if is_index else html.unescape(first_img_alt(htm))
    e = lambda s: html.escape(s, quote=True)
    rows = [
        ("property", "og:type", "website" if is_index else "article"),
        ("property", "og:site_name", "Locahun 3D" if en else "ロケハン3D"),
        ("property", "og:locale", "en_US" if en else "ja_JP"),
        ("property", "og:locale:alternate", "ja_JP" if en else "en_US"),
        ("property", "og:title", title),
        ("property", "og:description", desc),
        ("property", "og:url", canonical(htm, rel)),
        ("property", "og:image", SITE + img),
        ("property", "og:image:width", str(w)),
        ("property", "og:image:height", str(h)),
    ]
    if alt:
        rows.append(("property", "og:image:alt", alt))
    rows += [
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", title),
        ("name", "twitter:description", desc),
        ("name", "twitter:image", SITE + img),
    ]
    body = "\n".join('<meta %s="%s" content="%s">' % (k, n, e(v)) for k, n, v in rows if v)
    return START + "\n" + body + "\n" + END

def apply(rel, mode):
    path = os.path.join(ROOT, rel)
    src = read(path)
    block = build(rel, src).replace("\n", nl_of(src))
    if BLOCK_RE.search(src):
        out = BLOCK_RE.sub(lambda _: block, src, count=1)
    else:
        # canonical/hreflang の直後、無ければ </head> 直前
        anchors = list(re.finditer(r'<link[^>]+rel=["\'](?:canonical|alternate)["\'][^>]*>', src, re.I))
        if anchors:
            i = anchors[-1].end()
            out = src[:i] + "\n" + block + src[i:]
        else:
            out = src.replace("</head>", block + "\n</head>", 1)
    changed = out != src
    if changed and mode == "write":
        write(path, out)
    return changed

def main():
    mode = "write" if "--write" in sys.argv else "check"
    ps = pages()
    changed = [p for p in ps if apply(p, mode)]
    print("%s: %d pages, %d %s" % (mode, len(ps), len(changed),
                                   "drifted" if mode == "check" else "updated"))
    for c in changed: print("   ", c)
    return 1 if (mode == "check" and changed) else 0

if __name__ == "__main__":
    sys.exit(main())
