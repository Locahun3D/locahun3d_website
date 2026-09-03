# -*- coding: utf-8 -*-
"""ロケハン3D 欧文横組みロゴ（マーク＋ワードマーク "Locahun 3D"）を生成する。

これが商標登録済みロゴ（KWI株式会社、9類・41類・42類、2026-08出願／
弁理士法人ととせ・ももとせ 服部京子弁理士）の唯一の生成元。
和文版 build_logo.py と対になる欧文版。単色(mono-black)のみ。

レイアウト規約（2026-09-02 確定・商標登録版）:
  キャンバス 1920x1000 透過
  フォント: Noto Sans JP, weight 900（サイト本体と同一）
  文字列: "Locahun 3D"（"Locahun"と"3D"の間はスペース、カーニング -10px）
  マーク高: 文字インク高の 1.07倍（角丸オプティカル補正）のさらに1.10倍（拡大調整）
  マーク〜文字の間隔: 110px（75px規定値 + 35pxの人手調整）
  マークは文字に対し +5px 下にオフセット（人手による視覚調整）
  レイアウト全体をインクの重心でキャンバス中央に再配置
  色: mono-black (17,18,20) のみ。透過版・白背景版の2種を出力。
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1000
MARK, GAP, SW, RING_SW = 230, 75, 5.0, 3.0
INK = (17, 18, 20)


def draw_mark(ink_size, ink_col, reticle_col, sw=SW, ring_sw=RING_SW, ss=4):
    """ScanMark をベクタ描画。ink幅 = (50+sw/2)-(14-sw/2) = 36+sw。build_logo.py と同一実装。"""
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
    return im


def ink_bbox_and_centroid(img):
    a = np.asarray(img.split()[-1]).astype(float)
    ys, xs = np.nonzero(a > 8)
    wsum = a[ys, xs]
    cy = (ys * wsum).sum() / wsum.sum()
    return xs.min(), xs.max(), ys.min(), ys.max(), cy


# ワードマーク "Locahun 3D" — Noto Sans JP weight 900、"Locahun"と"3D"の間を-10pxカーニング
font = ImageFont.truetype(r"C:\Windows\Fonts\NotoSansJP-VF.ttf", 240)
font.set_variation_by_axes([900])

pad = 200
tmp = Image.new("RGBA", (2600, 900), (0, 0, 0, 0))
td = ImageDraw.Draw(tmp)
KERN_3D = -10
adv = font.getlength("Locahun ")
td.text((pad, pad), "Locahun", font=font, fill=INK + (255,))
td.text((pad + adv + KERN_3D, pad), "3D", font=font, fill=INK + (255,))
tx0, tx1, ty0, ty1, tcy = ink_bbox_and_centroid(tmp)
text_img = tmp.crop((tx0, ty0, tx1 + 1, ty1 + 1))
text_ink_h = text_img.height

# マークのインク高: 文字高に角丸オプティカル補正(7%)+ 拡大調整(10%)
OVERSHOOT = 0.07
mark_h = int(round(text_ink_h * (1 + OVERSHOOT) * 1.10))
mark = draw_mark(mark_h, INK, INK)
m_x0, m_x1, m_y0, m_y1, _ = ink_bbox_and_centroid(mark)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
top = int(round((H - text_ink_h) / 2))
extra = mark_h - text_ink_h
layer.paste(mark, (0, top - m_y0 - extra // 2 + 5), mark)
layer.paste(text_img, (m_x1 + 1 + GAP + 35, top), text_img)
lx0, lx1, ly0, ly1, _ = ink_bbox_and_centroid(layer)
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ox = (W - (lx1 - lx0 + 1)) // 2 - lx0
oy = (H - (ly1 - ly0 + 1)) // 2 - ly0
canvas.paste(layer, (int(ox), int(oy)), layer)

out_dir = r"F:\Htlml\3DGS\digiroke3d_Web\assets\logo"
out1 = out_dir + r"\locahun3d-logo-latin-transparent.png"
canvas.save(out1)

white = Image.new("RGB", (W, H), (255, 255, 255))
white.paste(canvas, (0, 0), canvas)
out2 = out_dir + r"\locahun3d-logo-latin-white.png"
white.save(out2)
print("OK", out1, out2, "text_w:", text_img.width)
