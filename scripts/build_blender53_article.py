#!/usr/bin/env python3
"""Generate works/blender-53-native-3dgs.html (JA) and en/works/... (EN)
from the committed blender-lcc2-vfx article template (head styles, header,
credits and footer are reused; only meta, body and related links change)."""
import re, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "blender-53-native-3dgs"
IMG = f"/works/images/{SLUG}"
SITE = "https://web.locahun3d.com"

def tpl(path):
    return subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{path}"], capture_output=True, check=True).stdout.decode("utf-8")

def fig(name, alt, cap):
    return (f'<figure><a href="{IMG}/{name}.jpg"><img loading="lazy" src="{IMG}/{name}.jpg" alt="{alt}"></a>'
            f'<figcaption>{cap}</figcaption></figure>')

def table(rows):
    """First row is the header. On phones the header row is hidden by the template CSS,
    so every value cell also carries its column name, shown only at phone width."""
    head, body = rows[0], rows[1:]
    out = ['<div class="tblwrap"><table><thead><tr>' + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"]
    for r in body:
        cells = [f"<td>{r[0]}</td>"] + [f'<td><span class="ml">{head[i]}</span>{c}</td>' for i, c in enumerate(r) if i > 0]
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

MOBILE_LABEL_CSS = ('<style>.tblwrap td .ml{display:none}@media(max-width:600px){.tblwrap td .ml{display:block;'
                    'font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--sub);margin-bottom:2px}}</style>')

def br(*lines):
    return "".join(f"{l}<br />\n" for l in lines)

JA = dict(
    lang="ja",
    title="Blender 5.3で3DGSがネイティブ対応。1,720万粒の渋谷で性能とVFX出力を検証",
    h1="Blender 5.3で3DGSがネイティブ対応。<br />1,720万粒の渋谷で性能とVFX出力を検証",
    desc="Blender 5.3アルファ版の3D Gaussian Splatting対応を、渋谷の全景データで検証。読み込み・描画速度・メモリと、透過・パス・CG合成・書き出しまで、VFXで使える範囲と止まる点をまとめます。",
    meta="BLENDER 5.3 / 3DGS / VFX · 2026-09-19",
    lead="アドオンなしでPLYを読み込み、EEVEEとCyclesで描画できるようになりました。<br />実データで速度を測り、合成の素材としてどこまで出せるかを確かめます。<br />",
    alt="Blender 5.3のEEVEEで描画した渋谷スクランブル交差点の3DGS",
    back="実績とブログの一覧へ戻る",
    related_h="関連する記事",
    related=[("/works/3dgs-blender-workflow.html", "Blenderで3DGSを使うなら？ 描画品質・処理時間・動画で比較"),
             ("/works/blender-lcc2-vfx.html", "LCC2をそのままBlenderへ。3DGSをVFXの素材として使う"),
             ("/works/3dgs-file-formats.html", "3DGSのファイル形式を整理する")],
)
JA["body"] = "\n".join([
    "<p>" + br("ロケハン3Dの中村です。",
               "Blender 5.3で、3D Gaussian Splatting（3DGS）がアドオンなしで扱えるようになります。",
               "PLYとSPZを読み込み、Workbench・EEVEE・Cyclesのすべてで描画できます。",
               "5.3は現在アルファ版で、正式リリースは11月10日の予定です。",
               "渋谷スクランブル交差点の1,720万粒の全景データで、性能とVFXでの使いどころを検証しました。") + "</p>",
    '<aside class="callout note"><b>アルファ版での検証です</b>' + br(
        "公式デイリービルド（5.3.0 Alpha、2026年9月18日版）を使っています。",
        "正式リリースまでに挙動や数値が変わる可能性があります。") + "</aside>",
    '<h2 id="import"><span class="n">01</span> PLYを読み込むだけで3DGSになる</h2>',
    "<p>" + br("File &gt; Import からPLYかSPZを選ぶと、Point Cloudオブジェクトとして読み込まれます。",
               "種類は「3D Gaussian Splats」になり、1粒ごとに次の属性を持ちます。") + "</p>",
    table([["属性", "内容"], ["position", "位置"], ["scale", "大きさ"], ["rotation", "向き（Quaternion）"],
           ["radiance:base", "基本色と不透明度"], ["radiance:sh_0〜", "球面調和の係数（視点で変わる色）"]]),
    "<p>" + br("球面調和は3次（45係数）まで読み込まれ、描画にも反映されます。",
               "座標はBlenderの向きへ自動で変換され、Zが上の状態で配置されます。",
               "ジオメトリーノードのDelete Geometryで範囲外を消すと、3DGSのまま切り抜けます。",
               "Set Point Cloud Typeノードを使うと、普通のポイントとの切り替えもできます。") + "</p>",
    '<h2 id="env"><span class="n">02</span> 検証環境</h2>',
    table([["項目", "内容"], ["Blender", "5.3.0 Alpha（main.1a542e41319f / 2026-09-18）"],
           ["GPU", "RTX 5090 32GB / driver 610.47"], ["データ", "渋谷スクランブル交差点 PLY / 17,201,445粒 / 1.17GB"],
           ["比較用", "等間隔に間引いた10万・100万・400万粒"], ["出力", "1920×1080 / 64サンプル / Cyclesはノイズ除去なし"]]),
    "<p>" + br("数値は3回測った中央値です。",
               "初回はシェーダーの準備を含むため、別に記載します。") + "</p>",
    '<h2 id="performance"><span class="n">03</span> 1,720万粒でも1枚2秒前後で描画できる</h2>',
    fig("eevee-17m", "EEVEEで描画した渋谷の全景", br("EEVEE / 1,720万粒 / 1920×1080。", "看板の文字や横断歩道まで再現されます。")),
    table([["粒数", "読み込み", "EEVEE（初回／2回目以降）", "Cycles GPU（初回／2回目以降）"],
           ["10万", "0.01秒", "0.69／0.19秒", "1.26／0.48秒"], ["100万", "0.08秒", "0.75／0.32秒", "0.80／0.65秒"],
           ["400万", "0.31秒", "1.08／0.59秒", "1.23／1.04秒"], ["1,720万", "1.6秒", "2.41／1.73秒", "2.78／2.57秒"]]),
    table([["粒数", "RAMピーク（EEVEE／Cycles）", "VRAM増加（EEVEE／Cycles）"],
           ["100万", "1.0／0.8GB", "+1.6／+3.5GB"], ["1,720万", "3.2／3.0GB", "+4.5／+4.9GB"]]),
    "<p>" + br("カメラを回す24フレームの連番は、EEVEEで1枚1.52秒、Cyclesで2.47秒です。",
               "1,720万粒の.blendは919MBで、保存0.34秒、開き直し0.6秒で扱えます。",
               "リリースノートには「性能は理想的ではない」とありますが、この環境では実用的な速さです。",
               "GPUが弱い環境や、球面調和を多く持つデータでは結果が変わります。") + "</p>",
    fig("cycles-17m", "Cyclesで描画した渋谷の全景", br("Cycles GPU / 64サンプル。", "EEVEEとほぼ同じ見た目で、ネオンなど明るい部分がやや鮮やかに出ます。")),
    "<p>" + br("間引いたデータは粒のすき間が目立つため、実案件では全量で使います。") + "</p>",
    '<h2 id="vfx"><span class="n">04</span> 合成の基本はそのまま使える</h2>',
    table([["項目", "EEVEE", "Cycles", "使い方"],
           ["透過背景", "○", "○", "アルファ付きで合成へ渡せます"],
           ["CGとの前後関係", "○", "○", "手前のCGが正しく重なります"],
           ["ホールドアウト", "○", "○", "CGでスプラットをくり抜けます"],
           ["シャドウキャッチャー", "—", "○", "CGの影だけを取り出せます"],
           ["被写界深度", "○", "○", "レンダー時にかけます"],
           ["モーションブラー", "○", "△", "Cyclesは今回の設定で多重像になりました"],
           ["Depth・Normalパス", "△", "△", "値は出ますが穴とノイズがあります"],
           ["Mist・Position・Vector・Cryptomatte", "○", "○", "値が出ます"]]),
    fig("cg-occlusion", "渋谷の交差点に置いた赤い箱のCG", "手前に置いたCGの箱は、スプラットより前に正しく描画されます。<br />\n"),
    fig("holdout", "CGの箱でスプラットをくり抜いたホールドアウト", "ホールドアウトを設定したCGで、背景のスプラットをくり抜きます。<br />\n"),
    fig("shadow-catcher", "Cyclesのシャドウキャッチャーで取り出したCGの影", br("Cyclesのシャドウキャッチャーを地面に置くと、CGの影だけを合成用に取り出せます。")),
    fig("dof", "被写界深度で背景をぼかした渋谷", "被写界深度はスプラットにも自然にかかります。<br />\n"),
    fig("mblur-eevee", "EEVEEでカメラを振ったモーションブラー", "EEVEEのモーションブラーは滑らかに流れます。<br />\n"),
    '<h2 id="limits"><span class="n">05</span> 本番で止まる4つの点</h2>',
    "<h3>ライトが効かない</h3>",
    "<p>" + br("スプラットは光を出す素材として描画され、撮影時の光が色に焼き込まれています。",
               "強いライトを当てても、スプラットの色は変わりません。",
               "スプラットはCGの影も受けません。",
               "CGを置くときは、撮影時の光の向きにCG側のライトを合わせます。",
               "夜景に変えるような背景のライティング変更には使えません。") + "</p>",
    "<h3>深度パスに穴がある</h3>",
    fig("depth-holes", "黒い点が散らばった深度パス", br("深度パスの可視化。", "黒い点は深度が記録されていない画素です。")),
    "<p>" + br("スプラットのある画素のうち、7.5〜8.4%で深度が記録されません。",
               "粒が半透明の部分で、深度が無限遠になるためです。",
               "深度を使ったフォグやポストの被写界深度ではノイズが出るため、被写界深度はレンダー時にかけます。",
               "法線パスも面の向きがそろわないため、リライティングには使えません。") + "</p>",
    "<h3>書き出すと色が消える</h3>",
    "<p>" + br("PLYに書き出すと、中身が0粒のファイルになります。",
               "USDでは位置・大きさ・向きは出ますが、色と不透明度が入りません。",
               "HoudiniやNukeへ3DGSのまま渡すことはできないため、Blenderで描画してEXRで渡します。") + "</p>",
    "<h3>Apply Transformで崩れる</h3>",
    fig("transform-object", "オブジェクトの変形のまま拡大した3DGS", "オブジェクトの変形のままなら、拡大しても見た目は崩れません。<br />\n"),
    fig("transform-applied", "Apply Transformで粒の大きさが残ったまま広がった3DGS", br("Apply Transformをすると、粒の大きさが元のまま位置だけ広がり、すき間だらけになります。")),
    "<p>" + br("マッチムーブで位置を合わせたあとも、Apply Transformは使わず、オブジェクトの変形のまま残します。") + "</p>",
    '<aside class="callout note"><b>マルチレイヤーEXRは1パス1ファイルで出す</b>' + br(
        "今回のアルファ版では、複数のパスを1つのEXRにまとめるとCombinedしか入りません。",
        "メッシュだけのシーンでも同じなので、3DGSの問題ではありません。",
        "コンポジターのFile Outputノードでパスごとに別のEXRにすると、深度や法線も書き出せます。") + "</aside>",
    '<h2 id="summary"><span class="n">06</span> 背景プレートとプリビズから使い始める</h2>',
    table([["用途", "向いているか"],
           ["実写の背景を3DGSで差し替える", "◎ 画質・速度ともに十分"],
           ["3DGSの背景の前にCGを置く", "○ ライトはCG側で合わせる"],
           ["プリビズ・ロケハン・カメラワークの検討", "◎ 読み込みが速く軽い"],
           ["背景のライティング変更", "× できない"],
           ["深度を使ったポスト処理", "△ ノイズが出る"],
           ["他のソフトへ3DGSのまま渡す", "× 色が消える"]]),
    "<p>" + br("Blender 5.3の3DGS対応は、読み込んでカメラを動かし、画像にするまでならすでに実用的です。",
               "一方で、ライトが効かない、深度に穴がある、書き出すと色が消えるという3つの壁があります。",
               "まずは背景プレートやプリビズで使い、CGとの合成はシャドウキャッチャーと1パス1ファイルのEXRで組みます。",
               "SPZの読み込みと、本物の球面調和を持つデータでの見た目は、正式リリース後に改めて確かめます。") + "</p>",
])

EN = dict(
    lang="en",
    title="Native 3DGS in Blender 5.3: performance and VFX output on a 17.2M-splat Shibuya scan",
    h1="Native 3DGS in Blender 5.3:<br />performance and VFX output on a 17.2M-splat scan",
    desc="Testing Blender 5.3 alpha's built-in 3D Gaussian Splatting with a full Shibuya scan: import, render speed and memory, plus transparency, passes, CG compositing and export — what works for VFX and where it stops.",
    meta="BLENDER 5.3 / 3DGS / VFX · 2026-09-19",
    lead="Blender now imports PLY splats without an add-on and renders them in EEVEE and Cycles.<br />I measured the speed on real data and checked how far it goes as compositing material.<br />",
    alt="Shibuya Scramble Crossing 3DGS rendered in Blender 5.3 EEVEE",
    back="Back to works and blog",
    related_h="Related articles",
    related=[("/en/works/3dgs-blender-workflow.html", "Using 3DGS in Blender: quality, render time and video compared"),
             ("/en/works/blender-lcc2-vfx.html", "Direct from LCC2 to Blender: using 3DGS for VFX"),
             ("/en/works/3dgs-file-formats.html", "A guide to 3DGS file formats")],
)
EN["body"] = "\n".join([
    "<p>" + br("I'm Kou Nakamura from Locahun 3D.",
               "Blender 5.3 handles 3D Gaussian Splatting (3DGS) natively, with no add-on.",
               "It imports PLY and SPZ and renders splats in Workbench, EEVEE and Cycles.",
               "5.3 is in alpha now; the stable release is planned for November 10.",
               "I tested performance and VFX use with a full 17.2-million-splat scan of Shibuya Scramble Crossing.") + "</p>",
    '<aside class="callout note"><b>Tested on an alpha build</b>' + br(
        "I used the official daily build (5.3.0 Alpha, September 18, 2026).",
        "Behavior and numbers may change before the stable release.") + "</aside>",
    '<h2 id="import"><span class="n">01</span> Importing a PLY gives you 3DGS directly</h2>',
    "<p>" + br("Choose a PLY or SPZ from File &gt; Import and it arrives as a Point Cloud object.",
               "Its type is \"3D Gaussian Splats\", and every splat carries these attributes.") + "</p>",
    table([["Attribute", "Content"], ["position", "Position"], ["scale", "Size"], ["rotation", "Orientation (quaternion)"],
           ["radiance:base", "Base color and opacity"], ["radiance:sh_0…", "Spherical harmonics (view-dependent color)"]]),
    "<p>" + br("Spherical harmonics up to degree 3 (45 coefficients) are imported and rendered.",
               "Coordinates are converted to Blender's orientation, so the scene lands Z-up.",
               "Delete Geometry in Geometry Nodes crops a region while keeping it 3DGS.",
               "The Set Point Cloud Type node switches between splats and plain points.") + "</p>",
    '<h2 id="env"><span class="n">02</span> Test setup</h2>',
    table([["Item", "Detail"], ["Blender", "5.3.0 Alpha (main.1a542e41319f / 2026-09-18)"],
           ["GPU", "RTX 5090 32GB / driver 610.47"], ["Data", "Shibuya Scramble PLY / 17,201,445 splats / 1.17GB"],
           ["Subsets", "Evenly thinned 100K, 1M and 4M splats"], ["Output", "1920×1080 / 64 samples / Cycles without denoising"]]),
    "<p>" + br("Figures are medians of three runs.",
               "The first render includes shader preparation and is listed separately.") + "</p>",
    '<h2 id="performance"><span class="n">03</span> About two seconds per frame at 17.2M splats</h2>',
    fig("eevee-17m", "Full Shibuya scan rendered in EEVEE", br("EEVEE / 17.2M splats / 1920×1080.", "Sign lettering and crosswalk stripes hold up.")),
    table([["Splats", "Import", "EEVEE (first / after)", "Cycles GPU (first / after)"],
           ["100K", "0.01s", "0.69 / 0.19s", "1.26 / 0.48s"], ["1M", "0.08s", "0.75 / 0.32s", "0.80 / 0.65s"],
           ["4M", "0.31s", "1.08 / 0.59s", "1.23 / 1.04s"], ["17.2M", "1.6s", "2.41 / 1.73s", "2.78 / 2.57s"]]),
    table([["Splats", "Peak RAM (EEVEE / Cycles)", "Added VRAM (EEVEE / Cycles)"],
           ["1M", "1.0 / 0.8GB", "+1.6 / +3.5GB"], ["17.2M", "3.2 / 3.0GB", "+4.5 / +4.9GB"]]),
    "<p>" + br("A 24-frame camera move renders at 1.52s per frame in EEVEE and 2.47s in Cycles.",
               "The 17.2M-splat .blend is 919MB; it saves in 0.34s and reopens in 0.6s.",
               "The release notes say performance is not ideal yet, but on this machine it is practical.",
               "Results will differ on weaker GPUs or on data with many spherical harmonics.") + "</p>",
    fig("cycles-17m", "Full Shibuya scan rendered in Cycles", br("Cycles GPU / 64 samples.", "Nearly identical to EEVEE, with slightly more saturated bright areas such as neon.")),
    "<p>" + br("Thinned data shows gaps between splats, so use the full scan for production.") + "</p>",
    '<h2 id="vfx"><span class="n">04</span> Compositing basics work as they are</h2>',
    table([["Feature", "EEVEE", "Cycles", "Use"],
           ["Transparent background", "○", "○", "Hand off with alpha"],
           ["Occlusion with CG", "○", "○", "Foreground CG layers correctly"],
           ["Holdout", "○", "○", "Cut splats out with CG"],
           ["Shadow catcher", "—", "○", "Extract CG shadows only"],
           ["Depth of field", "○", "○", "Apply at render time"],
           ["Motion blur", "○", "△", "Cycles produced ghosting with these settings"],
           ["Depth / Normal passes", "△", "△", "Values exist, with holes and noise"],
           ["Mist / Position / Vector / Cryptomatte", "○", "○", "Values are written"]]),
    fig("cg-occlusion", "Red CG box placed in the Shibuya crossing", "A CG box in the foreground renders correctly in front of the splats.<br />\n"),
    fig("holdout", "Holdout cutting the splats with a CG box", "A holdout object cuts the splat background.<br />\n"),
    fig("shadow-catcher", "CG shadow extracted with the Cycles shadow catcher", br("A Cycles shadow catcher on the ground isolates CG shadows for compositing.")),
    fig("dof", "Shibuya with background blurred by depth of field", "Depth of field falls naturally on the splats.<br />\n"),
    fig("mblur-eevee", "EEVEE motion blur from a camera pan", "EEVEE motion blur streaks smoothly.<br />\n"),
    '<h2 id="limits"><span class="n">05</span> Four things that stop production use</h2>',
    "<h3>Lights have no effect</h3>",
    "<p>" + br("Splats render as emissive material, with the capture lighting baked into their color.",
               "A strong light does not change the splat color at all.",
               "Splats do not receive CG shadows either.",
               "Match your CG lighting to the direction of the captured light.",
               "Relighting the background, such as turning it into night, is not possible.") + "</p>",
    "<h3>The depth pass has holes</h3>",
    fig("depth-holes", "Depth pass speckled with black dots", br("Depth pass visualization.", "Black dots are pixels with no recorded depth.")),
    "<p>" + br("7.5–8.4% of splat pixels have no depth value.",
               "Semi-transparent splats leave the depth at infinity.",
               "Depth-based fog or post depth of field gets noisy, so apply depth of field at render time.",
               "Normals are not coherent enough for relighting either.") + "</p>",
    "<h3>Export drops the color</h3>",
    "<p>" + br("PLY export writes a file with zero splats.",
               "USD keeps position, scale and rotation but loses color and opacity.",
               "You cannot pass 3DGS to Houdini or Nuke as-is; render in Blender and deliver EXRs.") + "</p>",
    "<h3>Apply Transform breaks the look</h3>",
    fig("transform-object", "3DGS scaled with an object transform", "With an object transform, scaling keeps the look intact.<br />\n"),
    fig("transform-applied", "3DGS after Apply Transform with unscaled splats", br("After Apply Transform, positions spread but splat sizes stay the same, leaving gaps.")),
    "<p>" + br("After matchmoving, keep the object transform and do not apply it.") + "</p>",
    '<aside class="callout note"><b>Write one EXR per pass</b>' + br(
        "In this alpha, a multilayer EXR only contains Combined.",
        "Mesh-only scenes behave the same, so this is not a 3DGS issue.",
        "Use the compositor File Output node with one EXR per pass to get depth and normals.") + "</aside>",
    '<h2 id="summary"><span class="n">06</span> Start with background plates and previs</h2>',
    table([["Use", "Fit"],
           ["Replacing live-action backgrounds with 3DGS", "◎ Quality and speed are sufficient"],
           ["CG in front of a 3DGS background", "○ Match lighting on the CG side"],
           ["Previs, location scouting, camera work", "◎ Fast import, light to handle"],
           ["Relighting the background", "× Not possible"],
           ["Depth-based post processing", "△ Noisy"],
           ["Passing 3DGS to other software", "× Color is lost"]]),
    "<p>" + br("Blender 5.3's 3DGS support is already practical for importing, moving a camera and rendering images.",
               "Three walls remain: no lighting response, holes in depth, and color lost on export.",
               "Start with background plates and previs, and composite CG with the shadow catcher and one-EXR-per-pass output.",
               "I will revisit SPZ import and real spherical-harmonics data after the stable release.") + "</p>",
])

def build(cfg, tpl_path, out_path, lang_prefix):
    s = tpl(tpl_path)
    url = f"{SITE}{lang_prefix}/works/{SLUG}.html"
    s = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}｜{'ロケハン3D' if cfg['lang']=='ja' else 'Locahun3D'}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{cfg["desc"]}">', s, count=1)
    s = s.replace("blender-lcc2-vfx.html", f"{SLUG}.html")  # canonical / hreflang / og:url
    og = re.search(r"<!-- OGP:START.*?<!-- OGP:END -->", s, re.S).group(0)
    new_og = og
    for prop, val in (("og:title", cfg["title"]), ("og:description", cfg["desc"]), ("og:image:alt", cfg["alt"]),
                      ("og:image", f"{SITE}{IMG}/poster.jpg"), ("og:image:width", "1600"), ("og:image:height", "900")):
        new_og = re.sub(rf'<meta property="{re.escape(prop)}" content="[^"]*">', f'<meta property="{prop}" content="{val}">', new_og, count=1)
    for name, val in (("twitter:title", cfg["title"]), ("twitter:description", cfg["desc"]), ("twitter:image", f"{SITE}{IMG}/poster.jpg")):
        new_og = re.sub(rf'<meta name="{name}" content="[^"]*">', f'<meta name="{name}" content="{val}">', new_og, count=1)
    s = s.replace(og, new_og)
    header = (f'<header class="post">\n  <div class="post-meta">{cfg["meta"]}</div>\n  <h1>{cfg["h1"]}</h1>\n'
              f'  <p class="lead">{cfg["lead"]}</p>\n</header>\n<article>\n{MOBILE_LABEL_CSS}\n{cfg["body"]}\n</article>')
    s = re.sub(r'<header class="post">.*?</article>', lambda m: header, s, count=1, flags=re.S)
    rel = "".join(f'\n  <li><a href="{h}">{t}</a></li>' for h, t in cfg["related"])
    s = re.sub(r'(<section class="related"[^>]*><h2 id="related-h">[^<]*</h2><ul>).*?(</ul></section>)',
               lambda m: m.group(1) + rel + "\n" + m.group(2), s, count=1, flags=re.S)
    assert "blender-lcc2-vfx/" not in s.split("<article>")[1].split("</article>")[0]
    with open(os.path.join(ROOT, out_path), "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("wrote", out_path, len(s))

build(JA, "works/blender-lcc2-vfx.html", f"works/{SLUG}.html", "")
build(EN, "en/works/blender-lcc2-vfx.html", f"en/works/{SLUG}.html", "/en")
