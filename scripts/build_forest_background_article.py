#!/usr/bin/env python3
"""Generate works/3dgs-scan-ai-background-forest.html (JA) and en/works/... (EN).

Same layout and method as build_blender53_article.py: the committed reference
article (3dgs-lidar-denoise) provides <head> styles, site header, credits and
footer; only meta tags and the region from <header class="post"> to the related
section are replaced. Stills and clips come from
F:/Codex/Locahun3D_Promo/export_taki_article_media.py."""
import re, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "3dgs-scan-ai-background-forest"
REF = "3dgs-lidar-denoise"
IMG = f"/works/images/{SLUG}"
VID = f"/works/videos/{SLUG}"
SITE = "https://web.locahun3d.com"


def tpl(path):
    return subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def fig(name, alt, lead, rest=""):
    return (f'  <figure>\n    <img loading="lazy" decoding="async" src="{IMG}/{name}.webp" alt="{alt}">\n'
            f'    <figcaption><b>{lead}</b>{rest}</figcaption>\n  </figure>')


def vid(name, poster, label, lead, rest=""):
    return (f'  <figure>\n    <video controls playsinline preload="metadata" poster="{IMG}/{poster}" src="{VID}-{name}.mp4" aria-label="{label}"></video>\n'
            f'    <figcaption><b>{lead}</b>{rest}</figcaption>\n  </figure>')


def pair(n, a_alt, b_alt, a_cap, b_cap, cap=""):
    """Photo and render from the same pose, side by side (stacked on phones)."""
    tail = f'\n  <p class="pair-note">{cap}</p>' if cap else ""
    return (f'  <div class="pair">\n'
            f'    <figure><img loading="lazy" decoding="async" src="{IMG}/k2_{n}_photo.webp" alt="{a_alt}"><figcaption>{a_cap}</figcaption></figure>\n'
            f'    <figure><img loading="lazy" decoding="async" src="{IMG}/k2_{n}_ue.webp" alt="{b_alt}"><figcaption>{b_cap}</figcaption></figure>\n'
            f'  </div>{tail}')


PAIR_CSS = ('  <style>.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:26px 0}.pair figure{margin:0}.pair figcaption{font-size:12px;margin-top:8px}'
            '.pair-note{font-size:14px;color:var(--sub);margin:-12px 0 26px}@media(max-width:640px){.pair{grid-template-columns:1fr}}</style>')


def p(*lines):
    return "  <p>" + "<br>".join(lines) + "</p>"


def ul(*items):
    return "  <ul>\n" + "\n".join(f"    <li>{i}</li>" for i in items) + "\n  </ul>"


def callout(title, text, kind="note"):
    return f'  <div class="callout {kind}"><b>{title}</b>{text}</div>'


def h2(i, id_, text):
    return f'  <h2 id="{id_}"><span class="n">{i:02d}</span> {text}</h2>'


def h3(text):
    return f"  <h3>{text}</h3>"


def rcard(href, thumb, tag, date, read, title):
    return (f'      <a class="rcard" href="{href}">\n        <div class="rthumb" style="background-image:url(\'{thumb}\')"></div>\n'
            f'        <div class="rbody">\n          <div class="rmeta"><span>{tag}</span><span>{date}</span><span>{read}</span></div>\n'
            f'          <h3>{title}</h3>\n        </div>\n      </a>')


# ───────────────────────────── 日本語 ─────────────────────────────
JA = dict(
    lang="ja", brand="ロケハン3D",
    title="3DGSスキャンからAIで背景制作を行う",
    desc="払沢の滝の森をXGRIDS K2でスキャンし、3DGSから地形・岩・木道・木・植物・水をAIで起こしてUE5の背景にした工程を、2分の動画と画像でまとめます。K2の写真との比較と、残っている差も載せます。",
    alt="UE5で描画した払沢の滝の森。木道の橋と滝が見える",
    badges=["3DGS", "UE5", "Blender", "AI", "背景制作"], date="2026-11-03", read="読了 約7分",
    h1='3DGSスキャンからAIで<br class="pc">背景制作を行う',
    lead=("ロケハン3Dの中村です。<br>東京都檜原村の払沢の滝の森をXGRIDS K2でスキャンし、その3DGSを基準に、<strong>UE5で動かせる背景</strong>を制作しました。<br>"
          "地形、岩、木道、木、植物、水を、<strong>AIが書いたスクリプトでスキャンから順に起こしています</strong>。<br>"
          "この記事では、2分の動画に沿って工程をまとめます。<br>K2の写真と比べた結果と、残っている差も載せます。"),
    hero=vid("film", "poster.jpg", "3DGSスキャンからUE5の背景を作る工程の動画（2分・音声なし）",
             "工程をまとめた動画です。", "2分、音声なしです。"),
    toc_h="目次",
    toc=[("flow", "作ったものと進め方"), ("read", "スキャンから形と位置を読み取る"), ("layers", "地形から順に積む"),
         ("parts", "岩・木・木道・草を整える"), ("water", "川と滝を作る"), ("passes", "色・凹凸・光を分けて確認する"),
         ("k2", "K2の写真と同じ位置で比べる"), ("check", "3DGSと重ねて、隙間を数える"), ("diff", "残っている差"), ("summary", "まとめ")],
    steps=["K2でスキャン", "3DGSをUE5へ", "形と位置を読み取る", "AIが層ごとに生成", "写真・3DGSと比較", "修正"],
    related_h="関連する記事", back="実績とブログの一覧へ戻る",
    related=[("3dgs-codex-hall-modeling.html", "/works/images/musicholl_stage_model.webp", "CG技術", "2026-09-06", "約8分", "3DGSと撮影画像から、編集できるホールの3Dモデルを作る"),
             ("ue5-xgrids-3dgs-aerial-ai.html", "/works/images/ue5_shibuya_topdown_day.jpg", "アート", "2026-07-24", "約12分", "UE5 × XGRIDs SDKで3DGSから素材を出力する"),
             ("3dgs-software-comparison.html", "/works/images/dcc-og-cover.jpg", "CG技術", "2026-08-04", "約7分", "3DGSを扱えるソフト・ツール比較")],
    workflow="WORKFLOW: XGRIDS K2 SCAN → 3DGS → LCC4UNREAL → SCAN ANALYSIS → AI-GENERATED LAYERS → COMPARE WITH K2 PHOTOS AND 3DGS → FIX",
)
JA["body"] = [
    PAIR_CSS,
    callout("この記事で分かること",
            "3DGSスキャンを基準に、<strong>照明を当て直せてカメラも動かせる背景</strong>を作る工程が分かります。"
            "AIと人の分担、写真との比較の方法、まだ合っていない部分も載せています。"),
    h2(1, "flow", "作ったものと進め方"),
    p("3DGSは見た目をそのまま残せますが、照明を変えたり、岩や木を1つずつ動かしたりはできません。",
      "そこで、3DGSを見本にして、同じ森を<strong>物ごとに分かれた3Dシーン</strong>として作り直しました。"),
    fig("final", "UE5で描画した完成シーン", "UE5で描画した完成シーンです。", "Blenderでシーンを組み、UE5.8へ移してLumenで描画しています。"),
    p("制作はClaudeとCodexに任せ、BlenderとUE5を動かすスクリプトを書いてもらいました。",
      "岩、木、地面などの担当を分け、作った担当とは別の担当が、比較画像を見て点数を付けます。",
      "私は出てきた画像を見て、次に直す場所と優先順位を指示します。",
      "この進め方と、これまでの失敗は、<strong>自社の手順書にまとめて</strong>次のシーンでも使っています。"),
    callout("3DGSを自動変換したものではありません",
            "3DGSをそのままメッシュに変換したのではなく、スキャンから読み取った形と位置をもとに、部品を別に作っています。"
            "植物のモデルや葉の素材には手持ちの素材集も使い、光の環境にはPoly HavenのHDRIを使っています。"),

    h2(2, "read", "スキャンから形と位置を読み取る"),
    p("まずK2で現地を歩いてスキャンし、3DGSにします。",
      "LCC4UnrealでUE5へ読み込み、完成形を比べる基準としてシーンの中に置きます。"),
    fig("gs_walk", "UE5に読み込んだ払沢の滝の3DGS", "UE5に読み込んだ3DGSです。", "ここから先は、すべてこのスキャンと比べながら進めます。"),
    p("次に、スキャンから形と位置のデータを取り出します。",
      "取り出したのは、<strong>地形の高さ、岩161個の位置と大きさ、木22本の位置、植物約10万5千株の配置</strong>です。"),
    fig("map", "スキャンから読み取った岩・木・植物の配置を上から見た図", "読み取った配置を上から見た図です。", "丸が岩と木、緑の点が植物です。"),

    h2(3, "layers", "地形から順に積む"),
    p("読み取ったデータから、層ごとにシーンを生成します。",
      "同じカメラで3DGSから切り替えると、どの層が何を担当しているかを確認できます。"),
    vid("layers", "layer_terrain.webp", "地形から水まで層を積んでいく動画", "地形から水まで、順に積んだ映像です。", "字幕は日本語です。"),
    callout("まだ作っていない部分について",
            "映像と画像の途中段階では、まだ作っていない空の近くを3DGSのまま残し、明るさも編集で下げています。"
            "層だけだと、白い空に背景の破片が浮いて見えるためです。"),
    h3("地形"),
    p("スキャンの地面の高さから、穴のない1枚の地形を作ります。",
      "データがない岩の下や隙間は、周囲の高さから補います。"),
    fig("layer_terrain", "生成した地形", "地形だけの状態です。", "滝の周りの上部は3DGSのままです。"),
    h3("地面と遠景"),
    p("地面の肌を作り、落ち葉や小枝を配置します。",
      "奥の斜面には、スキャンの表面を使っています。"),
    fig("layer_ground", "地面と遠景を加えた状態", "地面と遠景を加えた状態です。"),
    h3("岩と根"),
    p("岩は、スキャンの位置と形から起こします。"),
    fig("layer_rocks", "岩と根を加えた状態", "岩と根を加えた状態です。"),
    h3("木道"),
    p("木道は、写真から測った板の位置に合わせて、1枚ずつ別の板として作ります。"),
    fig("layer_boardwalk", "木道を加えた状態", "木道を加えた状態です。"),
    h3("木"),
    p("幹の位置と太さをスキャンに当てはめて、木を立てます。"),
    fig("layer_trees", "木の幹を加えた状態", "木の幹を加えた状態です。"),
    h3("植物と水"),
    p("最後に、読み取った配置へ植物を置き、川と滝の水を入れます。"),
    fig("layer_plants", "植物を加えた状態", "植物を加えた状態です。"),
    fig("layer_water", "水まで加えた状態", "水まで加えた状態です。"),

    h2(4, "parts", "岩・木・木道・草を整える"),
    p("全体が揃ったら、部品ごとに作り込みます。"),
    h3("岩"),
    p("スキャンから起こした岩は、161個のうち138個で底が開いていました。",
      "このままだと隙間から空が見えるので、底を閉じて地面の下まで延ばします。",
      "表面の苔と岩肌は、写真素材をもとにBlenderで層を重ねて焼き込みます。"),
    fig("d_rock", "苔の付いた岩と川", "岩と苔です。"),
    h3("幹と枝葉"),
    p("樹皮の色は22種類を用意し、7つの撮影位置の写真に合わせます。",
      "葉には光が透ける材質を設定します。"),
    fig("d_bark", "手前の幹と奥の滝", "樹皮です。", "苔の付き方も写真に合わせています。"),
    fig("d_leaves", "下から見上げた枝葉", "枝葉です。"),
    h3("木道の板"),
    p("板には1枚ずつ、わずかな反りとねじれを付けます。"),
    fig("d_boards", "木道の板と奥の滝", "木道です。"),
    h3("草の接地"),
    p("配置した約13万5千株をシーンと照合し、浮いている3,544株を下ろすか移動します。"),
    fig("d_grass", "木道の周りの草", "接地を直した草です。"),

    h2(5, "water", "川と滝を作る"),
    p("川は、Blenderで計算した流速に沿って水面を流します。",
      "流れの速い場所には白い泡を出します。"),
    fig("d_foam", "白い泡の出ている川", "川と泡です。"),
    p("滝は、岩壁のスキャンに水を落とすシミュレーションを行います。",
      "計算結果をそのまま使うと見た目が崩れたので、結果をもとに<strong>水の帯へ置き換えています</strong>。"),
    fig("sim", "岩壁に水を落とすシミュレーション", "滝のシミュレーションです。"),
    fig("d_fall", "UE5で描画した滝", "置き換えた滝です。"),

    h2(6, "passes", "色・凹凸・光を分けて確認する"),
    p("完成画だけを見ていると、原因が色なのか、形なのか、光なのかが分かりません。",
      "そこで同じカメラのまま、色・凹凸・光に分けて確認し、原因のある所を直します。"),
    fig("pass_unlit", "色だけを表示した画", "色だけです。"),
    fig("pass_detail", "凹凸だけを表示した画", "凹凸（法線）だけです。"),
    fig("pass_light", "光だけを表示した画", "光だけです。"),
    p("光はPoly Havenの曇天HDRIと太陽で作り、Lumenで描いてAgXで仕上げます。"),

    h2(7, "k2", "K2の写真と同じ位置で比べる"),
    p("K2の生データには、3DGSより鮮明な写真が入っています。",
      "<strong>1,032枚の写真の位置を3DGSに合わせ</strong>、同じ位置からUE5で描いて比べます。"),
    vid("k2", "k2_1_photo.webp", "K2の写真とUE5の描画をワイプで切り替える動画", "写真とUE5をワイプで切り替えた映像です。", "字幕は日本語です。"),
    p("K2の写真とUE5の画を並べています。",
      "UE5側には全体の色味を整える補正をかけています。",
      "この比較では、物の位置と大きさの差を探します。"),
] + [pair(n, f"K2の写真 {n}", f"同じ位置から描いたUE5の画 {n}", "K2の写真", "UE5") for n in range(1, 7)] + [

    h2(8, "check", "3DGSと重ねて、隙間を数える"),
    p("3DGSとも、同じカメラで重ねて比べます。"),
    fig("wipe", "左が3DGS、右がUE5の画を重ねて切り替えた比較", "左が3DGS、右がUE5です。"),
    p("見た目で見つけにくい問題は、数えて直します。",
      "たとえば、岩や地面の隙間から見える空の色のピクセルを、視点ごとに数えます。",
      "確認用の20視点で、<strong>24,540ピクセルあった隙間が0</strong>になるまで修正しました。"),
    fig("d_ground_check", "修正後の地面と滝", "修正後の地面です。"),

    h2(9, "diff", "残っている差"),
    p("位置と大きさは写真に近づきましたが、すべてが一致しているわけではありません。",
      "上の6か所は、試した12か所のうち比較的合っているものを選んでいます。",
      "合っていない場所の例が、次の画です。"),
    pair("diff", "草に覆われた大きな岩と水の流れが写るK2の写真", "同じ位置から描いたUE5の画。岩の形と水の流れが写真と異なる", "K2の写真", "UE5"),
    ul("<strong>岩と水の流れの形：</strong>草に覆われた大きな岩と、その脇の水の流れは、写真と形が違います。橋の上の苔も再現できていません。",
       "<strong>植物の種類と量：</strong>配置はスキャンから取っていますが、1株ずつの種類や形までは合わせきれていません。",
       "<strong>色と明るさ：</strong>光の入り方は写真と揃っておらず、地面は写真より明るく見える場所があります。"),

    h2(10, "summary", "まとめ"),
    p("今回の工程は、次の流れです。"),
    ul("<strong>読み取る：</strong>3DGSから地形、岩、木、植物の形と位置を取り出します。",
       "<strong>生成する：</strong>AIが書いたスクリプトで、層ごとにシーンを組み立てます。",
       "<strong>比べる：</strong>K2の写真と3DGSを同じカメラで並べ、差を見つけて直します。"),
    ('  <div class="data-cta">\n    <span class="dc-tag">SCAN / 3DGS</span>\n'
     '    <h3>実在の場所をスキャンして、<br class="pc">映像の背景に使える形にします</h3>\n'
     '    <p>ロケ地を3DGSで記録し、BlenderやUnreal Engineで扱える形でお渡しします。<br>背景の制作まで含めて、用途に合わせてご相談ください。</p>\n'
     '    <a class="dc-btn" href="https://locahun3d.com/contact">スキャンの相談をする →</a>\n  </div>'),
]

# ───────────────────────────── English ─────────────────────────────
EN = dict(
    lang="en", brand="Locahun3D",
    title="Building a background from a 3DGS scan with AI",
    desc="How we scanned the forest at Hossawa Falls with an XGRIDS K2 and used AI to build terrain, rocks, boardwalks, trees, plants and water from the 3DGS as a UE5 background, with a 2-minute film, comparisons against K2 photos, and the differences that remain.",
    alt="The forest at Hossawa Falls rendered in UE5, with a boardwalk bridge and the waterfall",
    badges=["3DGS", "UE5", "Blender", "AI", "Backgrounds"], date="2026-11-03", read="~7 min read",
    h1='Building a background <br class="pc">from a 3DGS scan with AI',
    lead=("This is Nakamura from LOCAHUN 3D. I scanned the forest at Hossawa Falls in Hinohara, Tokyo, with an XGRIDS K2 and used that 3DGS as the reference for a <strong>background you can move through in UE5</strong>. "
          "Terrain, rocks, boardwalks, trees, plants and water were <strong>built from the scan, step by step, by scripts written by AI</strong>. "
          "This article follows the 2-minute film through the process, and includes the comparisons with K2 photos and the differences that remain."),
    hero=vid("film", "poster.jpg", "Film of the process from a 3DGS scan to a UE5 background (2 minutes, no audio)",
             "The film of the process.", "2 minutes, no audio. On-screen captions are in Japanese."),
    toc_h="Contents",
    toc=[("flow", "What we made and how we worked"), ("read", "Reading shapes and positions from the scan"), ("layers", "Stacking the scene from the terrain up"),
         ("parts", "Refining rocks, trees, boards and grass"), ("water", "Making the stream and the waterfall"), ("passes", "Checking color, surface detail and light separately"),
         ("k2", "Comparing with K2 photos from the same positions"), ("check", "Overlaying the 3DGS and counting gaps"), ("diff", "Differences that remain"), ("summary", "Summary")],
    steps=["Scan with K2", "Bring 3DGS into UE5", "Read shapes and positions", "AI builds each layer", "Compare with photos and 3DGS", "Fix"],
    related_h="Related articles", back="Back to Work &amp; Blog",
    related=[("3dgs-codex-hall-modeling.html", "/works/images/musicholl_stage_model.webp", "CG", "2026-09-06", "~8 min", "Building an Editable Hall Model from 3DGS and Captured Images"),
             ("ue5-xgrids-3dgs-aerial-ai.html", "/works/images/ue5_shibuya_topdown_day.jpg", "Art", "2026-07-24", "~12 min", "Exporting Assets from 3DGS with UE5 × XGRIDs SDK"),
             ("3dgs-software-comparison.html", "/works/images/dcc-og-cover.jpg", "CG", "2026-08-04", "~8 min", "Software &amp; Tools That Handle 3DGS, Compared")],
    workflow="WORKFLOW: XGRIDS K2 SCAN → 3DGS → LCC4UNREAL → SCAN ANALYSIS → AI-GENERATED LAYERS → COMPARE WITH K2 PHOTOS AND 3DGS → FIX",
)
EN["body"] = [
    PAIR_CSS,
    callout("What you get from this article",
            "The process for using a 3DGS scan as the reference for a <strong>background you can relight and move a camera through</strong>: "
            "how AI and people split the work, how we compare against photos, and what still does not match."),
    h2(1, "flow", "What we made and how we worked"),
    p("3DGS keeps the look of a place, but you cannot relight it or move individual rocks and trees.",
      "So we used the 3DGS as a reference and rebuilt the same forest as a <strong>3D scene split into separate objects</strong>."),
    fig("final", "Finished scene rendered in UE5", "The finished scene rendered in UE5.", " The scene was assembled in Blender, moved to UE5.8 and rendered with Lumen."),
    p("Claude and Codex did the production, writing the scripts that drive Blender and UE5. "
      "Separate workers handle rocks, trees, ground and so on, and a different worker from the one who built each part scores it from comparison images. "
      "I look at the images and direct what to fix next and in what order. "
      "This way of working, and what went wrong along the way, is recorded in <strong>our own production guide</strong> for use on later scenes."),
    callout("This is not an automatic 3DGS conversion",
            "The 3DGS was not converted directly to a mesh. Parts were built separately from the shapes and positions read from the scan. "
            "Plant models and leaf materials also draw on asset libraries we already own, and the lighting environment uses an HDRI from Poly Haven."),

    h2(2, "read", "Reading shapes and positions from the scan"),
    p("First we walk the site with the K2 and turn the scan into 3DGS. "
      "It goes into UE5 through LCC4Unreal and stays in the scene as the reference for comparison."),
    fig("gs_walk", "The Hossawa Falls 3DGS in UE5", "The 3DGS in UE5.", " Every later step is compared against this scan."),
    p("Next we extract shape and position data from the scan: <strong>terrain height, the position and size of 161 rocks, the positions of 22 trees, and the placement of about 105,000 plants</strong>."),
    fig("map", "Top view of rock, tree and plant positions read from the scan", "The extracted layout from above.", " Circles are rocks and trees; green dots are plants."),

    h2(3, "layers", "Stacking the scene from the terrain up"),
    p("The scene is generated layer by layer from that data. "
      "Switching from the 3DGS with the same camera shows what each layer contributes."),
    vid("layers", "layer_terrain.webp", "Film of the layers stacking from terrain to water", "The layers stacking, from terrain to water.", " On-screen captions are in Japanese."),
    callout("About the parts not built yet",
            "In the in-between stages shown in the film and images, the area near the sky that has not been built stays as 3DGS, and the brightness is lowered in the edit. "
            "With the layers alone, pieces of the backdrop appear to float against a white sky."),
    h3("Terrain"),
    p("A single hole-free terrain is made from the heights of the scanned ground. "
      "Areas with no data, such as under rocks and in gaps, are filled from the surrounding heights."),
    fig("layer_terrain", "The generated terrain", "Terrain only.", " The top of the frame around the waterfall is still 3DGS."),
    h3("Ground and distance"),
    p("The ground surface is created, and fallen leaves and twigs are scattered on it. "
      "The far slope uses scanned surfaces."),
    fig("layer_ground", "With ground and distance added", "With ground and distance added."),
    h3("Rocks and roots"),
    p("Rocks are built from the positions and shapes in the scan."),
    fig("layer_rocks", "With rocks and roots added", "With rocks and roots added."),
    h3("Boardwalk"),
    p("The boardwalk is made of individual boards, placed to match board positions measured from the photos."),
    fig("layer_boardwalk", "With the boardwalk added", "With the boardwalk added."),
    h3("Trees"),
    p("Tree trunks are fitted to the positions and thicknesses in the scan."),
    fig("layer_trees", "With tree trunks added", "With tree trunks added."),
    h3("Plants and water"),
    p("Finally, plants go into the extracted positions, and water is added to the stream and the waterfall."),
    fig("layer_plants", "With plants added", "With plants added."),
    fig("layer_water", "With water added", "With water added."),

    h2(4, "parts", "Refining rocks, trees, boards and grass"),
    p("Once everything is in place, each part is refined."),
    h3("Rocks"),
    p("Of the 161 rocks built from the scan, 138 had open undersides. "
      "Sky would show through the gaps, so the undersides are closed and extended below the ground. "
      "The moss and rock surface are baked in Blender in layers based on photo materials."),
    fig("d_rock", "Mossy rocks and the stream", "Rocks and moss."),
    h3("Trunks and foliage"),
    p("We prepared 22 bark colors and matched them to photos from 7 camera positions. "
      "Leaves get a material that lets light through."),
    fig("d_bark", "A trunk in the foreground with the waterfall behind", "Bark.", " The moss pattern is also matched to the photos."),
    fig("d_leaves", "Foliage seen from below", "Foliage."),
    h3("Boards"),
    p("Each board gets a slight bow and twist of its own."),
    fig("d_boards", "Boardwalk boards with the waterfall behind", "The boardwalk."),
    h3("Grass contact"),
    p("About 135,000 plants are checked against the scene, and the 3,544 that float are lowered or moved."),
    fig("d_grass", "Grass around the boardwalk", "Grass after the contact fix."),

    h2(5, "water", "Making the stream and the waterfall"),
    p("The stream surface follows flow speeds computed in Blender. "
      "White foam appears where the flow is fast."),
    fig("d_foam", "The stream with white foam", "Stream and foam."),
    p("For the waterfall, we simulate water falling onto the scanned rock wall. "
      "Used as is, the result looked broken, so <strong>we replaced it with bands of water based on the simulation</strong>."),
    fig("sim", "Simulation of water falling onto the rock wall", "The waterfall simulation."),
    fig("d_fall", "The waterfall rendered in UE5", "The replacement waterfall."),

    h2(6, "passes", "Checking color, surface detail and light separately"),
    p("From the final image alone, you cannot tell whether a problem comes from color, shape or light. "
      "So with the same camera, we check color, surface detail and light separately and fix the actual cause."),
    fig("pass_unlit", "Color only", "Color only."),
    fig("pass_detail", "Surface detail only", "Surface detail (normals) only."),
    fig("pass_light", "Light only", "Light only."),
    p("Light comes from an overcast Poly Haven HDRI and a sun, rendered with Lumen and finished with AgX."),

    h2(7, "k2", "Comparing with K2 photos from the same positions"),
    p("The K2 raw data contains photos much sharper than the 3DGS. "
      "We <strong>aligned 1,032 photos to the 3DGS</strong> and rendered UE5 from the same positions to compare."),
    vid("k2", "k2_1_photo.webp", "Film wiping between K2 photos and UE5 renders", "Wiping between the photos and UE5.", " On-screen captions are in Japanese."),
    p("K2 photos and UE5 renders are shown side by side. "
      "The UE5 side has an overall color adjustment. "
      "In this comparison we look for differences in object position and size."),
] + [pair(n, f"K2 photo {n}", f"UE5 render {n} from the same position", "K2 photo", "UE5") for n in range(1, 7)] + [

    h2(8, "check", "Overlaying the 3DGS and counting gaps"),
    p("We also compare against the 3DGS with the same camera."),
    fig("wipe", "3DGS on the left and UE5 on the right", "3DGS on the left, UE5 on the right."),
    p("Problems that are hard to see get counted. "
      "For example, we count the sky-colored pixels showing through gaps in the rocks and ground from each view. "
      "We kept fixing until <strong>24,540 gap pixels fell to 0</strong> across the 20 check views."),
    fig("d_ground_check", "The ground and waterfall after fixes", "The ground after fixes."),

    h2(9, "diff", "Differences that remain"),
    p("Positions and sizes are now closer to the photos, but not everything matches. "
      "The six views above are the better matches out of 12 we tried. "
      "Here is an example that does not match."),
    pair("diff", "K2 photo with a large grass-covered rock and flowing water", "UE5 render from the same position, where the rock shape and water flow differ from the photo", "K2 photo", "UE5"),
    ul("<strong>Rock and water shapes:</strong> the large grass-covered rock and the water beside it differ in shape from the photo, and the moss on the bridge is not reproduced.",
       "<strong>Plant species and amounts:</strong> placement comes from the scan, but the species and form of each plant are not fully matched.",
       "<strong>Color and brightness:</strong> the way the light falls does not match the photos, and the ground looks brighter than in the photos in places."),

    h2(10, "summary", "Summary"),
    p("The process runs as follows."),
    ul("<strong>Read:</strong> extract the shapes and positions of terrain, rocks, trees and plants from the 3DGS.",
       "<strong>Generate:</strong> assemble the scene layer by layer with scripts written by AI.",
       "<strong>Compare:</strong> line up K2 photos and 3DGS with the same camera, find differences and fix them."),
    ('  <div class="data-cta">\n    <span class="dc-tag">SCAN / 3DGS</span>\n'
     '    <h3>We scan real places <br class="pc">in a form ready for film backgrounds</h3>\n'
     '    <p>We capture locations as 3DGS and deliver them in formats you can use in Blender or Unreal Engine.<br>Tell us what you need, including background production.</p>\n'
     '    <a class="dc-btn" href="https://locahun3d.com/en/contact">Talk to us about a scan →</a>\n  </div>'),
]


def build(cfg, ref_path, out_path):
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
    s = s.replace(f"/works/{REF}.html", f"/works/{SLUG}.html")
    header = ('<header class="post">\n  <div class="meta">\n    ' + "".join(f'<span class="badge">{b}</span>' for b in cfg["badges"])
              + f'\n    <span>{cfg["date"]}</span><span>・</span><span>{cfg["read"]}</span>\n  </div>\n'
              f'  <h1>{cfg["h1"]}</h1>\n  <p class="lead">{cfg["lead"]}</p>\n\n{cfg["hero"]}\n</header>\n\n'
              f'<nav class="toc">\n  <h2>{cfg["toc_h"]}</h2>\n  <ol>\n'
              + "".join(f'    <li><a href="#{a}">{t}</a></li>\n' for a, t in cfg["toc"]) + "  </ol>\n</nav>\n\n")
    steps = '  <div class="stepflow">\n    ' + '<span class="a">→</span>\n    '.join(f"<b>{x}</b>" for x in cfg["steps"]) + "\n  </div>"
    article = "<article>\n" + steps + "\n\n" + "\n\n".join(cfg["body"]) + "\n</article>\n\n"
    related = (f'<section class="related" aria-labelledby="related-h">\n  <h2 id="related-h">{cfg["related_h"]}</h2>\n  <div class="rgrid">\n'
               + "\n".join(rcard(*r) for r in cfg["related"]) + "\n  </div>\n  <div class=\"backwrap\">\n"
               '    <a class="backlink" href="index.html#blog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg> '
               + cfg["back"] + "</a>\n  </div>\n</section>\n\n")
    s = re.sub(r"WORKFLOW: [^<]*", cfg["workflow"], s, count=1)
    start = s.index('<header class="post">')
    end = s.index('<section class="credit">')
    s = s[:start] + header + article + related + "\n" + s[end:]
    body = s[start:s.index('<section class="credit">')]
    assert REF not in body and "isaacsim" not in body.lower(), "reference article content leaked into the new body"
    with open(os.path.join(ROOT, out_path), "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("wrote", out_path, len(s))


build(JA, f"works/{REF}.html", f"works/{SLUG}.html")
build(EN, f"en/works/{REF}.html", f"en/works/{SLUG}.html")
