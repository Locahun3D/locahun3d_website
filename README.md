# digiroke3d_Web

このリポジトリの役割は次の2つに限定されています。

1. **works 記事HTMLの生成元** — `works/`（日本語）・`en/works/`（英語）配下の実績・技術ブログ記事。
   - ヘッダーは配信側（locahun3d_online）のオンライン実ヘッダーを Worker が合成注入する方式に統一済み。詳細は `works/index.html` 内のコメントおよび意思決定ログを参照。
   - `scripts/sync_ogp.py`, `scripts/works_dark_audit.mjs`, `scripts/works_dark_blue.py` は記事生成・検証用スクリプト。
2. **ブランドロゴ正本** — `assets/logo/`（`build_logo.py` / `build_logo_latin.py` を含む）。ロゴを変更する場合は必ずここを正本として扱う。

## 配信について

works 記事の実配信は本リポジトリからではなく、**locahun3d_online** 側で行います。

```
node scripts/import-works.mjs
```

（locahun3d_online リポジトリ側のスクリプト）を実行して、このリポジトリの `works/` / `en/works/` を取り込みます。

## 退役した仕組み

かつて本リポジトリを Cloudflare Workers（`locahun3dwebsite`）として直接デプロイし、マーケサイト全体（トップページ・マニフェスト・データ・デモ・プライバシー・お問い合わせ・ピッチハブ等の各HTML、`worker.js`、`wrangler.jsonc`、ヘッダー合成用の `clerk-header.js` / `lib/header-partial.mjs` 等）を配信していましたが、これらは **2026-09-04 に退役** しました。マーケサイト配信は locahun3d_online に統合されています。上記の退役済みファイル群はリポジトリ棚卸しにより削除済みです（参照0を確認のうえ削除）。
