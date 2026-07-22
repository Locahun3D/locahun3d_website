"""ロケハン3D 横組みロゴ（マーク＋ワードマーク）を全カラーバリアントで生成する。

これが唯一の生成元。元PNG(logo_1920x1000_transparent.png)からワードマークの
アルファだけを取り出し、マークは scan-mark.tsx のジオメトリからベクタ描画する。
→ 拡大ボケなし・色は何色でも劣化なく差し替え可能。

レイアウト規約（2026-07-22 確定）:
  マーク高 230px / ブラケット線幅 5.0(viewBox64基準) / リング線幅 3.0 据置
  マーク〜文字 125px / マークと文字は「インクの重心」で上下を揃える
  ロックアップは 1920x1000 キャンバスの中央
"""
import sys
import numpy as np
from PIL import Image, ImageDraw

SRC = r"C:\Users\askgg\Desktop\logo_1920x1000_transparent.png"
W, H = 1920, 1000
MARK, GAP, SW, RING_SW = 230, 125, 5.0, 3.0
TEXT_CROP = (500, 0, 1900, 1000)   # 元PNG内のワードマーク領域
TEXT_INK_L, TEXT_INK_R = 66, 1288  # 上記クロップ内でのインク左右端

# 配色: (name, 文字＋ブラケット色, レチクル色)
VARIANTS = [
    ("dark-amber",  (17, 18, 20),    (255, 180, 84)),   # 明るい背景・スキャン(標準)
    ("light-amber", (250, 250, 246), (255, 180, 84)),   # 暗い背景・スキャン
    ("dark-blue",   (17, 18, 20),    (94, 200, 232)),   # 明るい背景・オンライン
    ("light-blue",  (250, 250, 246), (94, 200, 232)),   # 暗い背景・オンライン
    ("mono-black",  (17, 18, 20),    (17, 18, 20)),     # 単色（印刷・FAX・1色押し）
    ("mono-white",  (250, 250, 246), (250, 250, 246)),  # 単色（写真上・箔押し）
]


def draw_mark(ink_size, ink_col, reticle_col, sw=SW, ring_sw=RING_SW, ss=4):
    """ScanMark をベクタ描画。ink幅 = (50+sw/2)-(14-sw/2) = 36+sw。"""
    vb = ink_size / ((36.0 + sw) / 64.0)
    S = int(round(vb * ss))
    k = S / 64.0
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = sw * k
    col = ink_col + (255,)
    ret = reticle_col + (255,)

    def seg(pts):
        p = [(x * k, y * k) for x, y in pts]
        d.line(p, fill=col, width=max(1, int(round(w))))
        # PIL に丸キャップが無いため端点に円を置いて再現
        for (x, y) in p:
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col)

    seg([(14, 23), (14, 14), (23, 14)])
    seg([(41, 14), (50, 14), (50, 23)])
    seg([(14, 41), (14, 50), (23, 50)])
    seg([(50, 41), (50, 50), (41, 50)])
    c, r = 32 * k, 7 * k
    d.ellipse([c - r, c - r, c + r, c + r], outline=ret,
              width=max(1, int(round(ring_sw * k))))
    r2 = 2.4 * k
    d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=ret)
    im = im.resize((int(round(vb)), int(round(vb))), Image.LANCZOS)
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox())


def recolor(img, rgb):
    """アルファを保ったまま RGB だけ差し替える（アンチエイリアスを壊さない）。"""
    a = np.array(img)
    a[:, :, 0], a[:, :, 1], a[:, :, 2] = rgb
    return Image.fromarray(a, "RGBA")


def build(out_dir):
    src = Image.open(SRC).convert("RGBA")
    text = src.crop(TEXT_CROP)
    ta = np.array(text).astype(float)[:, :, 3]
    ys = np.arange(H)
    wsum = ta.sum(axis=1)
    text_centroid = (ys * wsum).sum() / wsum.sum()
    trows = np.where((ta > 16).any(axis=1))[0]
    tw = TEXT_INK_R - TEXT_INK_L + 1

    for name, ink, ret in VARIANTS:
        m = draw_mark(MARK, ink, ret)
        mw, mh = m.size
        x0 = (W - (mw + GAP + tw)) // 2
        my = text_centroid - mh / 2
        top = min(my, trows.min())
        bot = max(my + mh, trows.max())
        dy = (H - (bot - top)) / 2 - top
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.paste(m, (x0, int(round(my + dy))), m)
        t = recolor(text, ink)
        out.paste(t, (x0 + mw + GAP - TEXT_INK_L, int(round(dy))), t)
        p = f"{out_dir}/locahun3d-logo-{name}.png"
        out.save(p)
        print("  ", p)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
