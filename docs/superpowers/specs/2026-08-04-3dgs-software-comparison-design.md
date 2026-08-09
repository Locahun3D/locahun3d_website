# 3DGS対応ソフト比較記事 — 設計

## 目的
`works/`(実績＆技術ブログ)に、3D Gaussian Splatting(3DGS)を扱える各種ソフト・ツールをダウンロードURL付きで一覧できる、独立したリファレンス記事を追加する。既存記事から引用・被リンクされる「早見表」として機能させる。

## スコープ
新規ファイル1本 + ブログ一覧(`works/index.html`)への1エントリ追加。既存の`ue5-xgrids-3dgs-aerial-ai.html`内の比較表(Houdini/Blender/3ds Max/C4D、リンクなし)はそのまま残し、変更しない。

## 記事の性格
既存の長文記事(UE5記事・Isaac Sim記事)とは異なり、**リファレンス重視**。カテゴリごとに短い解説文+表という構成にし、物語的な体験談は書かない。

## カテゴリ構成(4つ)
1. **DCC(3DCGソフト)** — Houdini 22 / Blender(アドオン) / 3ds Max(V-Ray 7) / Cinema 4D(レンダラー経由)
2. **ビューアー・エディタ** — SuperSplat(PlayCanvas)ほか
3. **変換ツール** — splat-transform(PlayCanvas)ほか
4. **ゲームエンジンプラグイン** — UE5(XGRIDS LCC Plugin、Luma AI UE Plugin、XScene-UEPlugin、MLSLabs GS Renderer、NanoGSなど)、Unity(該当プラグイン)

各カテゴリ冒頭に1〜3文の短い説明(直接手順口調ルール `feedback_blog_direct_procedural_voice` 準拠。「〜できます」調で統一し、伝聞・観察口調は使わない)。

## 表の列
| ソフト/ツール | 3DGS対応方式 | 得意 | 不得意 | 入手先URL | ライセンス/価格 |

- 「入手先URL」は実際にリンク化する(`<a href>`)。
- 既存のUE5記事内の比較表(Houdini/Blender/3ds Max/C4D、UEプラグイン4種)の記述内容は事実として再利用可能だが、**URLは今回新たに裏取りしてから追加する**(既存記事にはURLが無いため)。

## 事実確認の方針(重要)
- 記載する全ソフトの入手先URL・現行の対応状況は、実装前に1件ずつWebSearch/WebFetchで裏取りする。
- 記憶・訓練データだけに基づく推測のURL・バージョン番号・価格は書かない。裏取りできなかった項目は「公式サイトで要確認」等に留めるか、掲載を見送る。
- LCC2フォーマットのライセンス懸念(`project_lcc2_loader`メモリ参照)など、社内的な法務未確認事項は記事本文に持ち込まない(読者向け記事とプロジェクト内部メモは別物)。

## 実装箇所
1. 新規HTML: `works/3dgs-software-comparison.html`
   - 既存記事(例: `portalcam-xbin-raw-extraction.html`)と同じテンプレート(ヘッダー・OGP・BudouX・戻る導線・関連記事)を踏襲。
   - タイトル・meta description・OGPは内容確定後に作成。
2. `works/index.html`の`POSTS`配列に新規カード追加(tag="tech"、date/read/thumbnailは記事完成時に確定)。

## テスト/検証方針
- ローカルでブラウザプレビューを開き、記事ページの表示・リンク遷移・BudouX改行・レスポンシブ(モバイル幅)を目視確認。
- 全リンクが実在URLであることを確認(裏取り済みのURLのみ使用)。
- `git commit`は完了時に実施、`git push`はプロジェクトルール(`feedback_autopush_locahun3d_website`)に従い自動実行。

## 非スコープ
- 英語版(`/en/works/`)への同時展開は行わない(既存記事も個別対応のため、必要なら別途)。
- キャプチャ/トレーニングアプリ(Postshot、Luma AIアプリ、Polycamなど)は今回のカテゴリに含めない(「3DGSを扱う」=読み込み・編集・書き出し側に限定)。
