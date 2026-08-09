# 3DGS対応ソフト比較記事 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `works/`配下に、3DGSを扱う各種ソフト・ツールをダウンロードURL付きで一覧できる新規リファレンス記事`3dgs-software-comparison.html`を追加し、`works/index.html`のブログ一覧に載せる。

**Architecture:** 静的HTML1ファイル(既存記事`portalcam-xbin-raw-extraction.html`と同一テンプレート: ヘッダー/OGP/BudouX/戻る導線/関連記事)。表データはこの記事内にインラインで直書き(ビルドステップなし、既存サイトの流儀に合わせる)。

**Tech Stack:** 素のHTML/CSS/JS(既存サイトと同じ、フレームワーク無し)。BudouX(CDN経由、文節改行)。

---

## 裏取り済みデータ(このまま記事に使う。URLは2026-08-04時点でWebSearchにより確認済み)

### カテゴリ1: DCC(3DCGソフト)
| ソフト | 3DGS対応方式 | 得意 | 不得意 | URL | ライセンス |
|---|---|---|---|---|---|
| Houdini 22 | ネイティブ対応(H22で「production-ready Gaussian Splats」を謳う) | 点群と同様にノードベースで変形・アニメーション、Karmaで直接レンダリング | ライセンス費用と習得コストが高い | https://www.sidefx.com/ | 商用(Indie/Apprentice等の無料版あり) |
| Blender | KIRI Engine製「3DGS Render」アドオン(OSS) | 無料で導入でき、ライトに反応・シャドウを落とせる。点群編集→3DGS変換にも対応 | サードパーティアドオン依存、大規模データで動作が重くなりやすい | https://github.com/Kiri-Innovation/3dgs-render-blender-addon | オープンソース・無料 |
| 3ds Max | V-Ray 7(Chaos)がネイティブ対応 | レイトレースでの直接レンダリング。V-Ray 7.3でシーンライトによるリライトにも対応 | V-Rayライセンス前提、編集機能は限定的 | https://www.chaos.com/vray/3ds-max | 商用(サブスク) |
| Cinema 4D | Octane(OTOY) 2026 Alpha 3(v1.7.0)でC4Dプラグインからスプラット対応 | Luma/Polycam/NeRDF Studio製のPLYを読み込み可能、モーショングラフィックスとの相性 | 執筆時点でスプラット対応は実験的機能(Alpha) | https://home.otoy.com/render/octane-render/ | 商用(サブスク) |

### カテゴリ2: ビューアー・エディタ
| ソフト | 特徴 | URL | ライセンス |
|---|---|---|---|
| SuperSplat(PlayCanvas) | ブラウザ完結の3DGSエディタ。クロップ・カラー編集・LCC2インポート対応、書き出し用の軽量ビューアーは別リポジトリ | Editor: https://github.com/playcanvas/supersplat ／ Viewer: https://github.com/playcanvas/supersplat-viewer | MIT・無料 |

### カテゴリ3: 変換ツール
| ソフト | 特徴 | URL | ライセンス |
|---|---|---|---|
| splat-transform(PlayCanvas) | CLI+ライブラリ。PLY/SPZ/SOG/KSPLAT/LCC/LCC2などの相互変換、LOD生成、マージ、ボクセル化まで対応。ブラウザ完結版「SuperSplat Convert」(WASM)もあり | `npm install -g @playcanvas/splat-transform` ／ https://github.com/playcanvas/splat-transform | MIT・無料 |

### カテゴリ4: ゲームエンジンプラグイン
**Unreal Engine 5**
| プラグイン | 特徴 | URL | ライセンス |
|---|---|---|---|
| XGRIDS LCC Plugin for UE | LCC/LCC2ネイティブ読込、リライト対応 | https://developer.xgrids.com/(サンプルデータ・プラグイン配布元) | XGRIDS独自ライセンス(要確認事項あり) |
| Luma AI UE Plugin | .ply/.lumaをドラッグ&ドロップでBlueprint化。無料 | https://www.fab.com/listings/b52460e0-3ace-465e-a378-495a5531e318 | 無料 |
| XScene-UEPlugin(XVERSE) | Niagara経由のリアルタイムレンダリング、編集・管理機能 | https://github.com/xverse-engine/XScene-UEPlugin | Apache 2.0・無料 |
| MLSLabs GS Renderer | 非Niagaraの独自パイプライン、4DGS(動的ボリュメトリック)対応、数百万ガウシアンでも高フレームレート | https://github.com/mlslabs/MLSLabsGaussianSplattingRenderer-UE | 無料(OSS) |
| NanoGS | Naniteスタイルのスクリーンスペース誤差LODクラスタリング。UE5.6+ | https://github.com/TimChen1383/NanoGaussianSplatting | MIT・無料 |

**Unity**
| プラグイン | 特徴 | URL | ライセンス |
|---|---|---|---|
| XGRIDS LCC Unity SDK | レンダリング・レイキャスト・クリッピング等を一式提供 | https://github.com/xgrids/LCC-Unity-SDK | XGRIDS独自ライセンス(要確認事項あり) |
| UnityGaussianSplatting(aras-p) | PLY・SPZ形式に対応した可視化実装。D3D12/Metal/Vulkan対応、VR(Quest/Vive/Varjo)確認済み | https://github.com/aras-p/UnityGaussianSplatting | MIT系OSS・無料(2023年12月時点で作者は大きな追加開発の予定なしと明記) |

---

## Task 1: 記事テンプレートの把握とベースコピー

**Files:**
- Read: `works/portalcam-xbin-raw-extraction.html`(テンプレート参照元)
- Create: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `works/portalcam-xbin-raw-extraction.html`を全文読み、以下を確認する: `<head>`のOGP/meta構造、ヘッダー(`site-header`)、目次(`<nav>`のリンクリスト)、本文の見出し番号(`<span class="n">`)、戻る導線・関連記事セクションのマークアップ、BudouXの`<script type="module">`部分。
- [ ] **Step 2:** そのファイルを丸ごとコピーして`works/3dgs-software-comparison.html`を新規作成する(この時点ではまだ中身を書き換えない)。

## Task 2: 記事メタ情報(head)の書き換え

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `<title>`を`3DGSを扱えるソフト・ツール比較｜ロケハン3D`に変更。
- [ ] **Step 2:** `<meta name="description">`・OGP(`og:title`/`og:description`/`twitter:title`/`twitter:description`)を「3D Gaussian Splatting(3DGS)を扱えるDCC・ビューアー・変換ツール・ゲームエンジンプラグインを、入手先URL付きで一覧。Houdini・Blender・3ds Max・Cinema 4D・SuperSplat・splat-transform・UE5/Unityプラグインまで。」に統一(文言は既存記事の文体に合わせ微調整可)。
- [ ] **Step 3:** `og:url`・`canonical`・`hreflang`を`works/3dgs-software-comparison.html`に書き換える。
- [ ] **Step 4:** `og:image`はサムネイル画像が無いため、既存の共通OGP画像(`Digiloke_OG_Cover.jpg`、コピー元にある値)をそのまま流用する。

## Task 3: 本文の書き換え(リード文＋目次)

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** 記事タイトル(hero部分)を「3DGSを扱えるソフト・ツール比較」に変更。
- [ ] **Step 2:** リード文(1〜2文)を書く。直接手順口調("〜できます")で、記事の目的(「3DGSを読み込み・編集・書き出しできるソフトをカテゴリ別に整理し、入手先をまとめます」)を説明する。伝聞・観察口調("〜だと分かりました"等)は使わない。
- [ ] **Step 3:** 目次(`<nav>`のリスト)を4項目にする: `#dcc`(DCC比較)、`#viewer`(ビューアー・エディタ)、`#converter`(変換ツール)、`#engine`(ゲームエンジンプラグイン)。

## Task 4: カテゴリ1「DCC」セクション

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `<h2 id="dcc">`見出しを追加し、短い説明文(1〜3文、直接手順口調)を書く。例:「3DGSはゲームエンジンだけでなく、普段のVFXパイプラインで使う3DCGソフト側でもそのまま扱えます。ソフトごとの対応方式と入手先を整理します。」
- [ ] **Step 2:** 上記「裏取り済みデータ」の**カテゴリ1**の表をそのままHTMLの`<table>`に変換する(列: ソフト／3DGS対応方式／得意／不得意／入手先／ライセンス)。「入手先」列は`<a href="URL" target="_blank" rel="noopener">`でリンク化する。
- [ ] **Step 3:** 表のCSSは既存サイトに`table`スタイルが無い場合、`<style>`内に追記する(枠線=`var(--line)`、フォントは本文と同じ、モバイルで横スクロール可能にするため`<div style="overflow-x:auto">`で表を囲む)。

## Task 5: カテゴリ2「ビューアー・エディタ」セクション

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `<h2 id="viewer">`見出し+短い説明文。
- [ ] **Step 2:** 「裏取り済みデータ」の**カテゴリ2**の表をTask4と同じ書式で追加。

## Task 6: カテゴリ3「変換ツール」セクション

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `<h2 id="converter">`見出し+短い説明文。
- [ ] **Step 2:** 「裏取り済みデータ」の**カテゴリ3**の表を追加。

## Task 7: カテゴリ4「ゲームエンジンプラグイン」セクション

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** `<h2 id="engine">`見出し+短い説明文。
- [ ] **Step 2:** 「UE5」小見出し+表、「Unity」小見出し+表を、「裏取り済みデータ」の**カテゴリ4**の内容でそれぞれ追加。
- [ ] **Step 3:** XGRIDS系(LCC Plugin for UE、LCC Unity SDK)の行には、ライセンス列に「独自ライセンス」の一言を明記する(既に表に含めた通り。誇張・断定を避け、リンク先で詳細確認を促す一文を表の下に添える)。

## Task 8: 戻る導線・関連記事・不要要素の調整

**Files:**
- Modify: `works/3dgs-software-comparison.html`

- [ ] **Step 1:** コピー元(`portalcam-xbin-raw-extraction.html`)固有の内容(著者紹介、xBin固有の画像・動画埋め込み、その記事だけの結論部分など)を、この記事に不要なものは削除する。
- [ ] **Step 2:** 「関連記事」セクションは、`ue5-xgrids-3dgs-aerial-ai.html`(3DGS対応比較に触れている記事)と`houdini-comfyui-gsplat-workflow.html`へのリンクに差し替える。
- [ ] **Step 3:** 画像・動画が無い記事のため、コピー元にあった`<img>`/`<video>`タグは全て削除する(壊れたパスを残さない)。

## Task 9: ブログ一覧への追加

**Files:**
- Modify: `works/index.html:258`(`POSTS`配列)

- [ ] **Step 1:** `POSTS`配列の先頭(最新記事として)に以下のオブジェクトを追加する:

```js
{
  tag:"tech", tagLabel:"技術", date:"2026-08-04", read:"約6分",
  title:"3DGSを扱えるソフト・ツール比較",
  excerpt:"3D Gaussian Splatting(3DGS)を読み込み・編集・書き出しできるDCC・ビューアー・変換ツール・ゲームエンジンプラグインを、入手先URL付きで整理。Houdini・Blender・3ds Max・Cinema 4DからSuperSplat、splat-transform、UE5/Unity向けプラグインまで。",
  href:"3dgs-software-comparison.html", thumb:"" 
},
```

- [ ] **Step 2:** サムネイル画像が無いため`thumb`は空文字にする(`blogCard`関数は`thumb`が偽値なら背景画像なしでカードを描画する仕様を`index.html:293`で確認済み。追加のコード変更は不要)。

## Task 10: ブラウザでの目視検証

**Files:** なし(検証のみ)

- [ ] **Step 1:** `preview_start`でこのリポジトリを静的サーバとして開く(例: `python -m http.server`相当をlaunch.jsonに登録するか、既存の起動方法があればそれを使う)。無ければ`npx serve .`等シンプルな静的サーバでよい。
- [ ] **Step 2:** `works/index.html`を開き、ブログ一覧に新記事カードが表示されること、クリックで`3dgs-software-comparison.html`に遷移することを確認する。
- [ ] **Step 3:** 記事ページで、目次リンク(4項目)が該当セクションにスクロールすること、4つの表が正しく表示されること、BudouXによる見出し改行が効いていること(コンソールエラーが出ていないこと)を`read_console_messages`で確認する。
- [ ] **Step 4:** 表内の全リンク(裏取り済みデータのURL、計13件)を実際にクリックまたは新規タブで開き、404でないことを確認する。
- [ ] **Step 5:** `resize_window`でモバイル幅(375px)に切り替え、表が`overflow-x:auto`で横スクロールできること、レイアウト崩れが無いことをスクリーンショットで確認する。
- [ ] **Step 6:** 問題があれば該当箇所を修正し、Step 2〜5を再実行する。

## Task 11: コミット・プッシュ

**Files:**
- `works/3dgs-software-comparison.html`
- `works/index.html`

- [ ] **Step 1:**

```bash
git add works/3dgs-software-comparison.html works/index.html
git commit -m "works: 3DGS対応ソフト・ツール比較記事を追加(DL URL付き)"
git push
```

(`feedback_autopush_locahun3d_website`ルールに従い、pushまで自動で行う)

---

## Self-Review メモ
- **仕様網羅**: spec記載の4カテゴリ・表の列構成・事実確認方針・記事一覧追加・非スコープ(英語版なし、キャプチャアプリなし)を全てTaskに反映済み。
- **プレースホルダー無し**: 表データは全て実URLで確定済み(WebSearchで裏取り済み、2026-08-04時点)。
- **型/命名の一貫性**: `POSTS`配列のオブジェクト形式は`works/index.html`の既存エントリと同一キー(`tag`/`tagLabel`/`date`/`read`/`title`/`excerpt`/`href`/`thumb`)を使用。
