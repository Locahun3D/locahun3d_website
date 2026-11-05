#!/usr/bin/env python3
"""Unreal Fest Tokyo 2026 XGRIDS ブース展示の実績記事を作る（2026-11-05 本人指示）。

  python scripts/build_unreal_fest_article.py <写真フォルダ（1.jpg 2.jpg 3.jpg）>

Chevon の実績ページを雛形に JA/EN を書き出す。写真は人が写らない範囲に切り抜く。
"""
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "unreal-fest-tokyo-2026-xgrids-booth"
TEMPLATE = "chevron-rokunowa-mv"
IMG = f"images/{SLUG}"

CSS = """
.case-photo{margin:28px 0 0;aspect-ratio:16/9;overflow:hidden;border:1px solid var(--line);background:#000}
.case-photo img{width:100%;height:100%;object-fit:cover}
.booth{margin:64px 0 0;border-top:1px solid var(--line);padding-top:46px}
.booth .ey{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}
.booth h2{font-family:'Noto Sans JP',sans-serif;font-weight:800;font-size:clamp(19px,3vw,23px);color:#fff;margin:10px 0 24px}
.booth .films{display:grid;gap:26px;margin-bottom:46px}
.booth video{display:block;width:100%;aspect-ratio:16/9;background:#000;border:1px solid var(--line)}
.booth h3{font-family:'Noto Sans JP',sans-serif;font-weight:700;font-size:1em;color:#fff;margin-top:12px}
.booth .films p{margin-top:4px;font-size:.84em;line-height:1.8;color:var(--dim)}
.booth .grid{display:grid;gap:18px}
@media(min-width:720px){.booth .grid{grid-template-columns:1fr 1fr}}
.booth img{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border:1px solid var(--line)}
.booth figcaption{margin-top:10px;font-size:.84em;line-height:1.8;color:var(--dim)}
.official{display:inline-block;margin-top:26px;font-size:.86em;color:var(--accent);border-bottom:1px solid currentColor}
"""

TEXT = {
    "ja": {
        "dir": "works",
        "title": "Unreal Fest Tokyo 2026 XGRIDSブース展示 — ロケハン3D 制作実績",
        "desc": "Unreal Fest Tokyo 2026のXGRIDSブースで、ロケハン3Dの映像が展示されました。サービス紹介と、XGRIDS K2でスキャンした払沢の滝の森をUE5で再現した制作工程の2本です。",
        "heroAlt": "Unreal Fest Tokyo 2026のXGRIDSブース。モニターにロケハン3Dの映像が流れている",
        "badges": "<span class=\"w\">展示</span><span>Unreal Fest Tokyo 2026</span><span>XGRIDS</span>",
        "h1": "Unreal Fest Tokyo 2026<br>XGRIDSブースで<br class=\"sp\">ロケハン3Dが展示されました",
        "sub": "ブース用に制作した映像2本",
        "lead": "Unreal Fest Tokyo 2026のXGRIDSブースで、ロケハン3Dの映像が展示されました。<br>XGRIDSのスキャナーで撮った実在の場所を、ブラウザで歩いて下見できるサービスの紹介と、払沢の滝の森をUE5で再現した制作工程の2本です。",
        "facts": [
            ("Event", "<strong>Unreal Fest Tokyo 2026</strong>"),
            ("Date", "2026年11月3日・4日"),
            ("Venue", "TFTホール（東京・有明）"),
            ("Booth", "XGRIDS"),
            ("Content", "サービス紹介と、払沢の滝（東京都檜原村）の森をUE5で再現した制作工程の映像 各60秒"),
        ],
        "official": "Unreal Fest Tokyo 2026 公式サイト",
        "officialUrl": "https://www.unrealengine.com/ja/events/unreal-fest-tokyo-2026",
        "boothEy": "At the booth / ブースの様子",
        "boothH": "ブースで流れた映像",
        "film1": "ロケハン3D サービス紹介",
        "film1Cap": "XGRIDS K2・PortalCamでスキャンした交差点やスタジオを、ブラウザで歩いて下見できるサービスの紹介です。",
        "film2": "払沢の滝を、UE5で再現する",
        "film2Cap": "XGRIDS K2のスキャンから、フォトリアルなCGの背景に仕上げるまでの制作工程です。",
        "photoH": "会場の写真",
        "photo2Alt": "モニターに映る払沢の滝の森",
        "photo2Cap": "モニターに映る払沢の滝の全景。",
        "photo3Alt": "モニターに映る制作工程の説明",
        "photo3Cap": "地形や岩などを部品ごとに作り、3DGSで採った位置に置いていく工程の場面。",
        "bandH": "3DGSスキャンから<br class=\"pc\"><em>AIで背景制作</em>を行う",
        "bandP": "森の映像の制作工程を、K2の写真との比較と合わせて解説しています。",
        "bandAlt": "払沢の滝の森をUE5で描いた背景",
        "bandCta": "記事を読む →",
        "relMeta": "<span>CG技術</span><span>2026-11-03</span><span>約7分</span>",
        "relTitle": "3DGSスキャンからAIで背景制作を行う",
    },
    "en": {
        "dir": "en/works",
        "title": "XGRIDS booth at Unreal Fest Tokyo 2026 — Locahun 3D production works",
        "desc": "Locahun 3D was exhibited at the XGRIDS booth at Unreal Fest Tokyo 2026, with a service overview and a film on recreating the Hossawa Falls forest in UE5 from an XGRIDS K2 scan.",
        "heroAlt": "The XGRIDS booth at Unreal Fest Tokyo 2026, with Locahun 3D's film on the monitor",
        "badges": "<span class=\"w\">Exhibited</span><span>Unreal Fest Tokyo 2026</span><span>XGRIDS</span>",
        "h1": "Locahun 3D at the XGRIDS booth,<br>Unreal Fest Tokyo 2026",
        "sub": "Two films made for the booth",
        "lead": "Locahun 3D was exhibited at the XGRIDS booth at Unreal Fest Tokyo 2026, with two films: an overview of our service for walking real locations in the browser, and the making of the Hossawa Falls forest in UE5.",
        "facts": [
            ("Event", "<strong>Unreal Fest Tokyo 2026</strong>"),
            ("Date", "November 3–4, 2026"),
            ("Venue", "TFT Hall (Ariake, Tokyo)"),
            ("Booth", "XGRIDS"),
            ("Content", "A service overview and the making of the Hossawa Falls forest (Hinohara, Tokyo) in UE5, 60 seconds each"),
        ],
        "official": "Unreal Fest Tokyo 2026 official site",
        "officialUrl": "https://www.unrealengine.com/events/unreal-fest-tokyo-2026",
        "boothEy": "At the booth",
        "boothH": "The films shown at the booth",
        "film1": "Locahun 3D service overview",
        "film1Cap": "Crossings and studios scanned with the XGRIDS K2 and PortalCam, walkable in the browser for location scouting.",
        "film2": "Recreating Hossawa Falls in UE5",
        "film2Cap": "The production process, from an XGRIDS K2 scan to a photoreal CG background.",
        "photoH": "Photos from the venue",
        "photo2Alt": "The forest at Hossawa Falls on the booth monitor",
        "photo2Cap": "A wide view of Hossawa Falls on the booth monitor.",
        "photo3Alt": "A production step explained on the booth monitor",
        "photo3Cap": "The step where terrain, rocks and other parts are built separately and placed where the 3DGS scan recorded them.",
        "bandH": "Building a background<br class=\"pc\">from a 3DGS scan <em>with AI</em>",
        "bandP": "The article walks through how the forest film was made, with comparisons against K2 photos.",
        "bandAlt": "The Hossawa Falls forest rendered as a UE5 background",
        "bandCta": "Read the article →",
        "relMeta": "<span>CG</span><span>2026-11-03</span><span>7 min</span>",
        "relTitle": "Building a background from a 3DGS scan with AI",
    },
}


def photos(src):
    out = os.path.join(ROOT, "works", IMG)
    os.makedirs(out, exist_ok=True)
    # 1 枚目は左右に来場者が写るので、ブースだけを 16:9 で切り出す
    booth = Image.open(os.path.join(src, "1.jpg")).convert("RGB").crop((300, 380, 1860, 1257))
    booth.save(os.path.join(out, "booth.jpg"), quality=88)
    booth.save(os.path.join(out, "booth.webp"), quality=84)
    for name, fn in (("falls", "2.jpg"), ("process", "3.jpg")):
        im = Image.open(os.path.join(src, fn)).convert("RGB")
        im.thumbnail((1600, 1200))
        im.save(os.path.join(out, name + ".webp"), quality=84)
    print("booth", booth.size)


def find(s, *marks):
    """雛形は JA と EN で目印が違う（EN はコメントも関連記事も無い）。"""
    return next(s.index(m) for m in marks if m in s)


HERO = ("  <!-- Hero", '  <div class="case-hero"')
BAND = ("  <!-- Blog CTA", '  <section class="blogband">')
TAIL = ('  <section class="related"', '</div>\n<div class="filmstrip">')


def between(s, a, b, new):
    i, j = find(s, *a), find(s, *b)
    return s[:i] + new + s[j:]


def page(lang):
    t = TEXT[lang]
    d = os.path.join(ROOT, t["dir"])
    with open(os.path.join(d, TEMPLATE + ".html"), encoding="utf-8", newline="") as f:
        s = f.read().replace("\r\n", "\n")
    s = s.replace(TEMPLATE, SLUG)
    s = re.sub(r"<title>.*?</title>", f"<title>{t['title']}</title>", s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + t["desc"], s, count=1)
    s = s.replace("</style>\n</head>", CSS + "</style>\n</head>", 1)
    base = "images" if lang == "ja" else "/works/images"  # EN は /en/works/ なので相対だと画像が無い
    img = f"{base}/{SLUG}"
    facts = "\n".join(f'      <div class="r"><div class="role">{k}</div><div class="v">{v}</div></div>' for k, v in t["facts"])
    s = between(s, HERO, BAND, f"""  <!-- Hero -->
  <figure class="case-photo">
    <img decoding="async" src="{img}/booth.webp" width="1560" height="877" alt="{t['heroAlt']}">
  </figure>

  <!-- Case body -->
  <div class="case-body">
    <div class="badges">
      {t['badges']}
    </div>
    <h1>{t['h1']}</h1>
    <p class="sub">{t['sub']}</p>
    <p class="lead">{t['lead']}</p>

    <div class="facts">
{facts}
    </div>

    <a class="official" href="{t['officialUrl']}" target="_blank" rel="noopener">{t['official']} ↗</a>
  </div>

  <!-- Booth -->
  <section class="booth">
    <div class="ey">{t['boothEy']}</div>
    <h2>{t['boothH']}</h2>
    <div class="films">
      <div>
        <video controls playsinline preload="metadata" poster="/works/images/{SLUG}/poster_service.webp" src="/works/videos/{SLUG}-service.mp4" aria-label="{t['film1']}"></video>
        <h3>{t['film1']}</h3>
        <p>{t['film1Cap']}</p>
      </div>
      <div>
        <video controls playsinline preload="metadata" poster="/works/images/{SLUG}/poster_forest.webp" src="/works/videos/{SLUG}-forest.mp4" aria-label="{t['film2']}"></video>
        <h3>{t['film2']}</h3>
        <p>{t['film2Cap']}</p>
      </div>
    </div>
    <h2>{t['photoH']}</h2>
    <div class="grid">
      <figure>
        <img loading="lazy" decoding="async" src="{img}/falls.webp" width="1600" height="1200" alt="{t['photo2Alt']}">
        <figcaption>{t['photo2Cap']}</figcaption>
      </figure>
      <figure>
        <img loading="lazy" decoding="async" src="{img}/process.webp" width="1600" height="1200" alt="{t['photo3Alt']}">
        <figcaption>{t['photo3Cap']}</figcaption>
      </figure>
    </div>
  </section>

""")
    s = between(s, BAND, TAIL, f"""  <!-- Blog CTA -->
  <section class="blogband">
    <div class="bb-body">
      <div class="ey">Tech Blog</div>
      <h2>{t['bandH']}</h2>
      <p>{t['bandP']}</p>
      <a class="cta" href="3dgs-scan-ai-background-forest.html">{t['bandCta']}</a>
    </div>
    <div class="bb-img">
      <img loading="lazy" decoding="async" src="{base}/3dgs-scan-ai-background-forest/final.webp" alt="{t['bandAlt']}">
    </div>
  </section>

""")
    # 関連記事の先頭を森の記事に
    s = re.sub(r'<a class="rcard" href="isaacsim-3dgs-import\.html">.*?</a>',
               f'''<a class="rcard" href="3dgs-scan-ai-background-forest.html">
        <div class="rthumb" style="background-image:url('{base}/3dgs-scan-ai-background-forest/final.webp')"></div>
        <div class="rbody">
          <div class="rmeta">{t['relMeta']}</div>
          <h3>{t['relTitle']}</h3>
        </div>
      </a>''', s, count=1, flags=re.S)
    # YouTube の再生スクリプトは使わない
    s = re.sub(r"<script>\s*\(function\(\)\{\s*document\.querySelectorAll\('\.ytfacade'\).*?</script>\s*", "", s, count=1, flags=re.S)
    s = s.replace(".blogband h2,.blogband p,.credit h2,.credit-card p,.credit-team p", ".blogband h2,.blogband p,.booth h2,.booth h3,.booth .films p,.booth figcaption")
    with open(os.path.join(d, SLUG + ".html"), "w", encoding="utf-8", newline="") as f:
        f.write(s)


if __name__ == "__main__":
    photos(sys.argv[1])
    for lang in TEXT:
        page(lang)
    print("ok")
