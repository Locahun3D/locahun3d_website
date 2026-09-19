#!/usr/bin/env python3
"""Generate works/blender-53-native-3dgs.html (JA) and en/works/... (EN).

Layout follows works/3dgs-lidar-denoise.html (the reference article): badges +
lead + hero figure, table of contents, step flow, "what you get" callout,
numbered sections, summary list, data CTA and related cards. The committed
reference page provides <head> styles, site header, credits and footer; only
meta tags and the region from <header class="post"> to the related section are
replaced."""
import re, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "blender-53-native-3dgs"
REF = "3dgs-lidar-denoise"
IMG = f"/works/images/{SLUG}"
SITE = "https://web.locahun3d.com"


def tpl(path):
    return subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def fig(name, alt, lead, rest=""):
    return (f'  <figure>\n    <a href="{IMG}/{name}.jpg"><img loading="lazy" src="{IMG}/{name}.jpg" alt="{alt}"></a>\n'
            f'    <figcaption><b>{lead}</b>{rest}</figcaption>\n  </figure>')


def table(rows):
    """First row is the header. The template hides <thead> on phones, so each value
    cell also carries its column name, shown only at phone width."""
    head, body = rows[0], rows[1:]
    out = ['  <div class="tblwrap"><table><thead><tr>' + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"]
    for r in body:
        out.append("<tr>" + f"<td>{r[0]}</td>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


MOBILE_LABEL_CSS = ('  <style>.tblwrap td .ml{display:none}@media(max-width:600px){.tblwrap td .ml{display:block;'
                    'font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--sub);margin-bottom:2px}}</style>')


def p(*lines):
    return "  <p>" + "<br>".join(lines) + "</p>"


def ul(*items):
    return "  <ul>\n" + "\n".join(f"    <li>{i}</li>" for i in items) + "\n  </ul>"


def callout(title, text):
    return f'  <div class="callout note"><b>{title}</b>{text}</div>'


def h2(i, id_, text):
    return f'  <h2 id="{id_}"><span class="n">{i:02d}</span> {text}</h2>'


def rcard(href, thumb, tag, date, read, title):
    return (f'      <a class="rcard" href="{href}">\n        <div class="rthumb" style="background-image:url(\'{thumb}\')"></div>\n'
            f'        <div class="rbody">\n          <div class="rmeta"><span>{tag}</span><span>{date}</span><span>{read}</span></div>\n'
            f'          <h3>{title}</h3>\n        </div>\n      </a>')


# ───────────────────────────── 日本語 ─────────────────────────────
JA = dict(
    lang="ja", brand="ロケハン3D",
    title="Blender 5.3の3DGSネイティブ対応を1,720万粒の渋谷で検証する",
    desc="Blender 5.3アルファ版の3D Gaussian Splatting対応を、渋谷スクランブル交差点の全景で検証。読み込み・描画速度・メモリと、透過・パス・CG合成・書き出しまで、VFXで使える範囲と止まる点をまとめます。",
    alt="Blender 5.3のEEVEEで描画した渋谷スクランブル交差点の3DGS",
    badges=["3DGS", "Blender 5.3", "VFX", "検証"], date="2026-09-19", read="読了 約6分",
    h1='Blender 5.3の<br class="pc">3DGSネイティブ対応を<br class="pc">1,720万粒の渋谷で検証する',
    lead=("ロケハン3Dの中村です。<br>Blender 5.3で、3D Gaussian Splatting（3DGS）が<strong>アドオンなしで読み込み・描画</strong>できるようになります。<br>"
          "渋谷スクランブル交差点の1,720万粒の全景データで、<strong>描画速度とメモリ、VFXの素材としてどこまで出せるか</strong>を確かめました。<br>"
          "結論は、<strong>背景プレートとプリビズには十分使える一方、ライト・深度・書き出しの3点で止まる</strong>です。"),
    hero=("eevee-17m", "Blender 5.3のEEVEEで描画した渋谷スクランブル交差点の3DGS",
          "EEVEEで描画した1,720万粒の渋谷です。", "1920×1080・64サンプルで1枚1.7秒。看板の文字や横断歩道まで、アドオンなしでここまで出ます。"),
    toc_h="目次",
    toc=[("import", "何が変わったか──PLYを読み込むだけで3DGSになる"), ("env", "検証環境"),
         ("performance", "描画性能──1,720万粒でも1枚2秒前後"), ("vfx", "合成の基本はそのまま使える"),
         ("limits", "本番で止まる4つの点"), ("summary", "まとめ")],
    steps=["PLYを読み込む", "カメラを決める", "EEVEE / Cyclesで描画", "EXRで合成へ"],
    related_h="関連する記事", back="実績とブログの一覧へ戻る",
    related=[("3dgs-software-comparison.html", "/works/images/dcc-og-cover.jpg", "技術", "2026-08-04", "約7分", "3DGSを扱えるソフト・ツール比較"),
             ("3dgs-file-formats.html", "/works/images/format-og-cover.jpg", "技術", "2026-08-09", "約9分", "3DGSのファイルフォーマットを整理する"),
             ("houdini-comfyui-gsplat-workflow.html", "/works/images/hectorvfx_shibuya_ai_render.jpg", "技術", "2026-07-23", "約7分",
              "Houdini 22 × ComfyUI ── Gaussian SplatsによるVFX × AIハイブリッドワークフロー")],
)
JA["body"] = [
    callout("この記事で得られるもの",
            "Blender 5.3の3DGS対応で<strong>何ができて、どこで止まるか</strong>を、実データの数値と画像で判断できます。"
            "対象は公式デイリービルド（5.3.0 Alpha、2026年9月18日版）です。正式リリースは11月10日の予定で、それまでに挙動や数値が変わる可能性があります。"),
    h2(1, "import", "何が変わったか──PLYを読み込むだけで3DGSになる"),
    p("<strong>File &gt; Import からPLYかSPZを選ぶだけ</strong>で、Point Cloudオブジェクトとして読み込まれます。",
      "種類は「3D Gaussian Splats」になり、Workbench・EEVEE・Cyclesのすべてで描画できます。",
      "1粒ごとに次の属性を持ちます。"),
    table([["属性", "内容"], ["position", "位置"], ["scale", "大きさ"], ["rotation", "向き（Quaternion）"],
           ["radiance:base", "基本色と不透明度"], ["radiance:sh_0〜", "球面調和の係数（視点で変わる色）"]]),
    ul("<strong>球面調和は3次（45係数）まで</strong>読み込まれ、描画にも反映されます。",
       "<strong>座標は自動で変換</strong>され、Zが上の状態で配置されます。",
       "ジオメトリーノードのDelete Geometryで範囲外を消すと、<strong>3DGSのまま切り抜けます</strong>。",
       "Set Point Cloud Typeノードで、普通のポイントとの切り替えもできます。"),
    h2(2, "env", "検証環境"),
    table([["項目", "内容"], ["Blender", "5.3.0 Alpha（main.1a542e41319f / 2026-09-18）"],
           ["GPU", "RTX 5090 32GB / driver 610.47"], ["データ", "渋谷スクランブル交差点 PLY / 17,201,445粒 / 1.17GB"],
           ["比較用", "等間隔に間引いた10万・100万・400万粒"], ["出力", "1920×1080 / 64サンプル / Cyclesはノイズ除去なし"]]),
    p("数値は3回測った中央値です。", "初回はシェーダーの準備を含むため、別に記載します。"),
    h2(3, "performance", "描画性能──1,720万粒でも1枚2秒前後"),
    table([["粒数", "読み込み", "EEVEE（初回／2回目以降）", "Cycles GPU（初回／2回目以降）"],
           ["10万", "0.01秒", "0.69／0.19秒", "1.26／0.48秒"], ["100万", "0.08秒", "0.75／0.32秒", "0.80／0.65秒"],
           ["400万", "0.31秒", "1.08／0.59秒", "1.23／1.04秒"], ["1,720万", "1.6秒", "2.41／1.73秒", "2.78／2.57秒"]]),
    p("<strong>1,720万粒でも、EEVEEで1枚1.7秒、Cyclesで2.6秒</strong>です。",
      "カメラを回す24フレームの連番は、EEVEEで1枚1.52秒、Cyclesで2.47秒でした。",
      "メモリは<strong>RAMが3.2GB、GPUメモリの増加が約5GB</strong>に収まります。",
      "1,720万粒の.blendは919MBで、保存0.34秒、開き直し0.6秒で扱えます。"),
    fig("cycles-17m", "Cyclesで描画した渋谷の全景", "Cycles（GPU・64サンプル）で描画した同じ画角です。",
        "EEVEEとほぼ同じ見た目で、ネオンなど明るい部分がやや鮮やかに出ます。"),
    p("リリースノートには「性能は理想的ではない」とありますが、<strong>この環境では実用的な速さ</strong>です。",
      "GPUが弱い環境や、球面調和を多く持つデータでは結果が変わります。",
      "また、間引いたデータは粒のすき間が目立つため、<strong>実案件では全量で使います</strong>。"),
    h2(4, "vfx", "合成の基本はそのまま使える"),
    table([["機能", "EEVEE", "Cycles", "使い方"],
           ["透過背景", "○", "○", "アルファ付きで合成へ渡せます"],
           ["CGとの前後関係", "○", "○", "手前のCGが正しく重なります"],
           ["ホールドアウト", "○", "○", "CGでスプラットをくり抜けます"],
           ["シャドウキャッチャー", "—", "○", "CGの影だけを取り出せます"],
           ["被写界深度", "○", "○", "レンダー時にかけます"],
           ["モーションブラー", "○", "△", "Cyclesは今回の設定で多重像になりました"],
           ["Depth・Normalパス", "△", "△", "値は出ますが穴とノイズがあります"],
           ["Mist・Position・Vector・Cryptomatte", "○", "○", "値が出ます"]]),
    fig("cg-occlusion", "渋谷の交差点に置いた赤い箱のCG", "交差点に置いたCGの箱です。", "手前のCGはスプラットより前に正しく描画されます。"),
    fig("shadow-catcher", "Cyclesのシャドウキャッチャーで取り出したCGの影", "Cyclesのシャドウキャッチャーを地面に置いたところです。",
        "スプラットはCGの影を受けませんが、影だけを取り出して合成すれば地面に落とせます。"),
    fig("dof", "被写界深度で背景をぼかした渋谷", "被写界深度をかけたところです。", "手前の箱にピントを合わせ、背景のスプラットが自然にぼけます。"),
    h2(5, "limits", "本番で止まる4つの点"),
    p("<strong>1つ目は、ライトが効かないこと</strong>です。",
      "スプラットは光を出す素材として描画され、撮影時の光が色に焼き込まれています。",
      "強いライトを当てても色は変わらないため、<strong>夜景に変えるような背景のライティング変更はできません</strong>。",
      "CGを置くときは、撮影時の光の向きにCG側のライトを合わせます。"),
    p("<strong>2つ目は、深度パスに穴があること</strong>です。",
      "スプラットのある画素のうち<strong>7.5〜8.4%で深度が記録されません</strong>。",
      "粒が半透明の部分で、深度が無限遠になるためです。"),
    fig("depth-holes", "黒い点が散らばった深度パス", "深度パスを可視化したところです。",
        "黒い点が深度の記録されていない画素です。深度を使ったフォグやポストの被写界深度ではノイズになるため、被写界深度はレンダー時にかけます。"),
    p("<strong>3つ目は、書き出すと色が消えること</strong>です。",
      "PLYに書き出すと中身が0粒のファイルになり、USDでは位置・大きさ・向きは出ますが<strong>色と不透明度が入りません</strong>。",
      "HoudiniやNukeへ3DGSのまま渡すことはできないため、<strong>Blenderで描画してEXRで渡します</strong>。"),
    p("<strong>4つ目は、Apply Transformで見た目が崩れること</strong>です。",
      "オブジェクトの変形のままなら崩れませんが、変形を適用すると<strong>粒の大きさが元のまま位置だけ広がり</strong>、すき間だらけになります。"),
    fig("transform-applied", "Apply Transformで粒の大きさが残ったまま広がった3DGS", "1.5倍に拡大してApply Transformしたところです。",
        "マッチムーブで位置を合わせたあとも、変形は適用せずオブジェクトのまま残します。"),
    callout("マルチレイヤーEXRは1パス1ファイルで出す",
            "今回のアルファ版では、複数のパスを1つのEXRにまとめると<strong>Combinedしか入りません</strong>。メッシュだけのシーンでも同じなので、3DGSの問題ではありません。"
            "コンポジターのFile Outputノードで<strong>パスごとに別のEXR</strong>にすると、深度や法線も書き出せます。"),
    h2(6, "summary", "まとめ"),
    p("Blender 5.3の3DGS対応で、制作に使える範囲はこの3行に収まります。"),
    ul("<strong>背景プレート・プリビズ：</strong>1,720万粒でも1枚2秒前後で描画でき、画質も十分です。",
       "<strong>CGとの合成：</strong>前後関係・ホールドアウト・被写界深度はそのまま使えます。影はシャドウキャッチャーで取り出します。",
       "<strong>本番の壁：</strong>ライトが効かない、深度に穴がある、書き出すと色が消える、Apply Transformで崩れる、の4点です。"),
    p("SPZの読み込みと、本物の球面調和を持つデータでの見た目は、正式リリース後に改めて確かめます。"),
    ('  <div class="data-cta">\n    <span class="dc-tag">SCAN / 3DGS</span>\n'
     '    <h3>ロケハン3Dでは、実在の空間を<br class="pc">VFXの背景として使える形でスキャンします</h3>\n'
     '    <p>撮影に使えるロケ地を3DGSで記録し、BlenderやUnreal Engineで扱える形式でお渡しします。<br>背景プレート・プリビズ・VFX合成まで、用途に合わせてご相談ください。</p>\n'
     '    <a class="dc-btn" href="https://locahun3d.com/contact">スキャンの相談をする →</a>\n  </div>'),
]

# ───────────────────────────── English ─────────────────────────────
EN = dict(
    lang="en", brand="Locahun3D",
    title="Testing Blender 5.3's native 3DGS on a 17.2M-splat Shibuya scan",
    desc="Testing Blender 5.3 alpha's built-in 3D Gaussian Splatting on a full scan of Shibuya Scramble Crossing: import, render speed and memory, plus transparency, passes, CG compositing and export — what works for VFX and where it stops.",
    alt="Shibuya Scramble Crossing 3DGS rendered in Blender 5.3 EEVEE",
    badges=["3DGS", "Blender 5.3", "VFX", "Test"], date="2026-09-19", read="~6 min read",
    h1='Testing Blender 5.3&rsquo;s <br class="pc">native 3DGS on a <br class="pc">17.2M-splat Shibuya scan',
    lead=("This is Nakamura from LOCAHUN 3D. Blender 5.3 can <strong>import and render 3D Gaussian Splatting (3DGS) without an add-on</strong>. "
          "Using a full 17.2-million-splat scan of Shibuya Scramble Crossing, I measured <strong>render speed, memory, and how far it goes as VFX material</strong>. "
          "The short answer: <strong>ready for background plates and previs, but it stops at lighting, depth and export</strong>."),
    hero=("eevee-17m", "Shibuya Scramble Crossing 3DGS rendered in Blender 5.3 EEVEE",
          "The 17.2M-splat Shibuya scan rendered in EEVEE.", "1920×1080 at 64 samples in 1.7 seconds per frame. Sign lettering and crosswalk stripes hold up with no add-on."),
    toc_h="Contents",
    toc=[("import", "What changed &mdash; a PLY import gives you 3DGS"), ("env", "Test setup"),
         ("performance", "Performance &mdash; about two seconds per frame at 17.2M splats"), ("vfx", "Compositing basics work as they are"),
         ("limits", "Four things that stop production use"), ("summary", "Summary")],
    steps=["Import the PLY", "Set the camera", "Render in EEVEE / Cycles", "EXR to compositing"],
    related_h="Related articles", back="Back to Work &amp; Blog",
    related=[("3dgs-software-comparison.html", "/works/images/dcc-og-cover.jpg", "Tech", "2026-08-04", "~8 min", "Software &amp; Tools That Handle 3DGS, Compared"),
             ("3dgs-file-formats.html", "/works/images/format-og-cover.jpg", "Tech", "2026-08-09", "~10 min", "A Field Guide to 3DGS File Formats"),
             ("houdini-comfyui-gsplat-workflow.html", "/works/images/hectorvfx_shibuya_ai_render.jpg", "Tech", "2026-07-23", "~7 min",
              "Houdini 22 × ComfyUI &mdash; A VFX × AI hybrid workflow with Gaussian Splats")],
)
EN["body"] = [
    callout("What you get from this article",
            "You can judge <strong>what Blender 5.3's 3DGS support can do and where it stops</strong>, from real-data numbers and images. "
            "I used the official daily build (5.3.0 Alpha, September 18, 2026). The stable release is planned for November 10, and behavior or numbers may change before then."),
    h2(1, "import", "What changed &mdash; a PLY import gives you 3DGS"),
    p("<strong>Just pick a PLY or SPZ from File &gt; Import</strong> and it arrives as a Point Cloud object.",
      "Its type is \"3D Gaussian Splats\", and it renders in Workbench, EEVEE and Cycles.",
      "Every splat carries these attributes."),
    table([["Attribute", "Content"], ["position", "Position"], ["scale", "Size"], ["rotation", "Orientation (quaternion)"],
           ["radiance:base", "Base color and opacity"], ["radiance:sh_0…", "Spherical harmonics (view-dependent color)"]]),
    ul("<strong>Spherical harmonics up to degree 3 (45 coefficients)</strong> are imported and rendered.",
       "<strong>Coordinates are converted automatically</strong>, so the scene lands Z-up.",
       "Delete Geometry in Geometry Nodes <strong>crops a region while keeping it 3DGS</strong>.",
       "The Set Point Cloud Type node switches between splats and plain points."),
    h2(2, "env", "Test setup"),
    table([["Item", "Detail"], ["Blender", "5.3.0 Alpha (main.1a542e41319f / 2026-09-18)"],
           ["GPU", "RTX 5090 32GB / driver 610.47"], ["Data", "Shibuya Scramble PLY / 17,201,445 splats / 1.17GB"],
           ["Subsets", "Evenly thinned 100K, 1M and 4M splats"], ["Output", "1920×1080 / 64 samples / Cycles without denoising"]]),
    p("Figures are medians of three runs.", "The first render includes shader preparation and is listed separately."),
    h2(3, "performance", "Performance &mdash; about two seconds per frame at 17.2M splats"),
    table([["Splats", "Import", "EEVEE (first / after)", "Cycles GPU (first / after)"],
           ["100K", "0.01s", "0.69 / 0.19s", "1.26 / 0.48s"], ["1M", "0.08s", "0.75 / 0.32s", "0.80 / 0.65s"],
           ["4M", "0.31s", "1.08 / 0.59s", "1.23 / 1.04s"], ["17.2M", "1.6s", "2.41 / 1.73s", "2.78 / 2.57s"]]),
    p("<strong>Even at 17.2M splats, a frame takes 1.7s in EEVEE and 2.6s in Cycles</strong>.",
      "A 24-frame camera move rendered at 1.52s per frame in EEVEE and 2.47s in Cycles.",
      "Memory stays at <strong>3.2GB of RAM and about 5GB of added VRAM</strong>.",
      "The 17.2M-splat .blend is 919MB; it saves in 0.34s and reopens in 0.6s."),
    fig("cycles-17m", "Full Shibuya scan rendered in Cycles", "The same view rendered in Cycles (GPU, 64 samples).",
        "Nearly identical to EEVEE, with slightly more saturated bright areas such as neon."),
    p("The release notes say performance is not ideal yet, but <strong>on this machine it is practical</strong>.",
      "Results will differ on weaker GPUs or on data with many spherical harmonics.",
      "Thinned data shows gaps between splats, so <strong>use the full scan for production</strong>."),
    h2(4, "vfx", "Compositing basics work as they are"),
    table([["Feature", "EEVEE", "Cycles", "Use"],
           ["Transparent background", "○", "○", "Hand off with alpha"],
           ["Occlusion with CG", "○", "○", "Foreground CG layers correctly"],
           ["Holdout", "○", "○", "Cut splats out with CG"],
           ["Shadow catcher", "—", "○", "Extract CG shadows only"],
           ["Depth of field", "○", "○", "Apply at render time"],
           ["Motion blur", "○", "△", "Cycles produced ghosting with these settings"],
           ["Depth / Normal passes", "△", "△", "Values exist, with holes and noise"],
           ["Mist / Position / Vector / Cryptomatte", "○", "○", "Values are written"]]),
    fig("cg-occlusion", "Red CG box placed in the Shibuya crossing", "A CG box placed in the crossing.", "Foreground CG renders correctly in front of the splats."),
    fig("shadow-catcher", "CG shadow extracted with the Cycles shadow catcher", "A Cycles shadow catcher on the ground.",
        "Splats do not receive CG shadows, but you can extract the shadow alone and composite it onto the ground."),
    fig("dof", "Shibuya with background blurred by depth of field", "Depth of field applied.", "Focus on the foreground box and the splat background blurs naturally."),
    h2(5, "limits", "Four things that stop production use"),
    p("<strong>First, lights have no effect.</strong>",
      "Splats render as emissive material, with the capture lighting baked into their color.",
      "Even a strong light leaves the color unchanged, so <strong>relighting the background, such as turning it into night, is not possible</strong>.",
      "Match your CG lighting to the direction of the captured light."),
    p("<strong>Second, the depth pass has holes.</strong>",
      "<strong>7.5–8.4% of splat pixels have no depth value</strong>.",
      "Semi-transparent splats leave the depth at infinity."),
    fig("depth-holes", "Depth pass speckled with black dots", "The depth pass, visualized.",
        "Black dots are pixels with no recorded depth. Depth-based fog or post depth of field gets noisy, so apply depth of field at render time."),
    p("<strong>Third, export drops the color.</strong>",
      "PLY export writes a file with zero splats, and USD keeps position, scale and rotation but <strong>loses color and opacity</strong>.",
      "You cannot pass 3DGS to Houdini or Nuke as-is, so <strong>render in Blender and deliver EXRs</strong>."),
    p("<strong>Fourth, Apply Transform breaks the look.</strong>",
      "With an object transform nothing breaks, but applying it <strong>spreads positions while splat sizes stay the same</strong>, leaving gaps."),
    fig("transform-applied", "3DGS after Apply Transform with unscaled splats", "Scaled 1.5× and then Apply Transform.",
        "After matchmoving, keep the object transform and do not apply it."),
    callout("Write one EXR per pass",
            "In this alpha, a multilayer EXR <strong>only contains Combined</strong>. Mesh-only scenes behave the same, so this is not a 3DGS issue. "
            "Use the compositor File Output node with <strong>one EXR per pass</strong> to get depth and normals."),
    h2(6, "summary", "Summary"),
    p("What Blender 5.3's 3DGS support can do in production fits in three lines."),
    ul("<strong>Background plates and previs:</strong> about two seconds per frame at 17.2M splats, with enough quality.",
       "<strong>Compositing with CG:</strong> occlusion, holdout and depth of field work as they are; extract shadows with the shadow catcher.",
       "<strong>Production walls:</strong> no lighting response, holes in depth, color lost on export, and Apply Transform breaking the look."),
    p("I will revisit SPZ import and real spherical-harmonics data after the stable release."),
    ('  <div class="data-cta">\n    <span class="dc-tag">SCAN / 3DGS</span>\n'
     '    <h3>LOCAHUN 3D scans real places <br class="pc">in a form ready for VFX backgrounds</h3>\n'
     '    <p>We capture filmable locations as 3DGS and deliver them in formats you can use in Blender or Unreal Engine.<br>From background plates and previs to VFX compositing, tell us what you need.</p>\n'
     '    <a class="dc-btn" href="https://locahun3d.com/en/contact">Talk to us about a scan →</a>\n  </div>'),
]


def build(cfg, ref_path, out_path, lang_prefix):
    s = tpl(ref_path)
    s = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}｜{cfg['brand']}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{cfg["desc"]}">', s, count=1)
    head_end = s.index("</head>")
    s = s[:head_end].replace(f"{REF}.html", f"{SLUG}.html") + s[head_end:]  # canonical / hreflang / og:url
    og = re.search(r"<!-- OGP:START.*?<!-- OGP:END -->", s, re.S).group(0)
    new_og = og
    for prop, val in (("og:title", cfg["title"]), ("og:description", cfg["desc"]), ("og:image:alt", cfg["alt"]),
                      ("og:image", f"{SITE}{IMG}/poster.jpg"), ("og:image:width", "1600"), ("og:image:height", "900")):
        new_og = re.sub(rf'<meta property="{re.escape(prop)}" content="[^"]*">', f'<meta property="{prop}" content="{val}">', new_og, count=1)
    for name, val in (("twitter:title", cfg["title"]), ("twitter:description", cfg["desc"]), ("twitter:image", f"{SITE}{IMG}/poster.jpg")):
        new_og = re.sub(rf'<meta name="{name}" content="[^"]*">', f'<meta name="{name}" content="{val}">', new_og, count=1)
    s = s.replace(og, new_og)
    # Language switch in the site header points to the counterpart page.
    s = s.replace(f"/works/{REF}.html", f"/works/{SLUG}.html").replace(f"/en/works/{REF}.html", f"/en/works/{SLUG}.html")
    img, alt, lead, rest = cfg["hero"]
    header = (f'<header class="post">\n  <div class="meta">\n    ' + "".join(f'<span class="badge">{b}</span>' for b in cfg["badges"])
              + f'\n    <span>{cfg["date"]}</span><span>・</span><span>{cfg["read"]}</span>\n  </div>\n'
              f'  <h1>{cfg["h1"]}</h1>\n  <p class="lead">{cfg["lead"]}</p>\n\n'
              f'  <figure>\n    <img src="{IMG}/{img}.jpg" alt="{alt}">\n    <figcaption><b>{lead}</b>{rest}</figcaption>\n  </figure>\n</header>\n\n'
              f'<nav class="toc">\n  <h2>{cfg["toc_h"]}</h2>\n  <ol>\n'
              + "".join(f'    <li><a href="#{a}">{t}</a></li>\n' for a, t in cfg["toc"]) + "  </ol>\n</nav>\n\n")
    steps = '  <div class="stepflow">\n    ' + '<span class="a">→</span>\n    '.join(f"<b>{x}</b>" for x in cfg["steps"]) + "\n  </div>"
    article = "<article>\n" + steps + "\n\n" + "\n\n".join(cfg["body"]) + "\n</article>\n\n"
    related = (f'<section class="related" aria-labelledby="related-h">\n  <h2 id="related-h">{cfg["related_h"]}</h2>\n  <div class="rgrid">\n'
               + "\n".join(rcard(*r) for r in cfg["related"]) + "\n  </div>\n  <div class=\"backwrap\">\n"
               '    <a class="backlink" href="index.html#blog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg> '
               + cfg["back"] + "</a>\n  </div>\n</section>\n\n")
    s = re.sub(r"WORKFLOW: [^<]*", "WORKFLOW: 3DGS SCAN → PLY → BLENDER 5.3 IMPORT → EEVEE / CYCLES → EXR PER PASS → COMPOSITE", s, count=1)
    start = s.index('<header class="post">')
    end = s.index('<section class="credit">')
    s = s[:start] + header + article + related + "\n" + s[end:]
    body = s[start:s.index('<section class="credit">')]
    assert REF not in body and "isaacsim" not in body.lower(), "reference article content leaked into the new body"
    with open(os.path.join(ROOT, out_path), "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("wrote", out_path, len(s))


build(JA, f"works/{REF}.html", f"works/{SLUG}.html", "")
build(EN, f"en/works/{REF}.html", f"en/works/{SLUG}.html", "/en")
