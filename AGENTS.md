# digiroke3d_Web — role after 2026-09-04

This repository **no longer serves any website**. The old marketing site and Worker `locahun3dwebsite` are retired.

What lives here:
- `works/` (JA) and `en/works/` (EN): the **source HTML of the 実績＆技術ブログ articles**. Both languages are always produced together.
- `assets/logo/` + `build_logo*.py`: brand logo source of truth. `assets/Digiloke_*`: article OGP images.
- `scripts/sync_ogp.py`, `scripts/works_dark_audit.mjs`: article tooling.

How articles reach production:
1. Edit/generate HTML here (JA + EN). Commit.
2. In `F:\Htlml\3DGS\locahun3d_online` run `node scripts/import-works.mjs`, commit `content/works/**` + `src/content/works.generated.ts`, then push (auto-deploy). Push only when the owner says so.
3. New images/videos go to R2 bucket `locahun3d-assets` under `works/images/**` / `works/videos/**` (`locahun3d_online/scripts/upload-r2.mjs`). URLs stay `https://web.locahun3d.com/works/...` — never change them.

Writing rules (owner's): JA/EN both; sentence-per-line breaks after 。; no numbers-heavy geek detail; direct procedural voice; no changelog/correction notes in articles; all works pages are noindex.

Start guide: `F:\docs\CODEX_START.md`. Handoff: `F:\docs\HANDOFF_2026-09-05_works完全統合・ヘッダー根本治療・整理.md`.
