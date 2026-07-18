"""
=====================================================================
PUHU Uydu Projesi - Isıl-Yapısal Tasarım Ekibi
5.1 / 5.2 Araştırma Sorusu - Soru 9
Panel Kalınlığının Yapısal ve Isıl Parametreler Üzerindeki
Zincirleme Etkisini Gösteren Sistem Etkileşim Diyagramı

Gereksinim: pip install matplotlib
Çalıştırma: python panel_diyagrami.py
=====================================================================
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Patch
import matplotlib.font_manager as fm

# ---------------------------------------------------------------
# 1) GENEL STİL / KATEGORİ RENK KODLARI
# ---------------------------------------------------------------
CATEGORY_COLORS = {
    "input":      {"face": "#2c3e50", "text": "white",  "label": "Girdi Parametresi"},
    "structural": {"face": "#3498db", "text": "white",  "label": "Yapısal Parametre"},
    "mass":       {"face": "#7f8c8d", "text": "white",  "label": "Kütle Parametresi"},
    "thermal":    {"face": "#e67e22", "text": "white",  "label": "Isıl Parametre"},
    "optical":    {"face": "#27ae60", "text": "white",  "label": "Optik Hizalama Sonucu"},
    "frequency":  {"face": "#8e44ad", "text": "white",  "label": "Doğal Frekans (Sistem Çıktısı)"},
    "decision":   {"face": "#f1c40f", "text": "black",  "label": "Gereksinim Kontrol Noktası"},
    "note":       {"face": "#fdf2e9", "text": "black",  "label": "Uyarı / Not"},
}

# ---------------------------------------------------------------
# 2) DÜĞÜM (NODE) TANIMLARI  ->  {id: (x, y, etiket, kategori, tip)}
#    tip: "box" | "diamond" | "note"
# ---------------------------------------------------------------
NODES = {
    "A": (13, 17.0, "PANEL KALINLIĞI (t)\nARTAR",                         "input",      "box"),

    "B": (5,  14.5, "Atalet Momenti (I)\nI = b·t³ / 12",                  "structural", "box"),
    "C": (13, 14.5, "Panel Kütlesi\nm_panel = ρ·b·L·t",                   "mass",       "box"),
    "D": (21, 14.5, "Eşdeğer Isıl İletkenlik\nG = 4·k·b·t / L",           "thermal",    "box"),

    "E": (3,  12.0, "Panel Rijitliği\nk_panel",                           "structural", "box"),
    "F": (7,  12.0, "Maks. Eğilme Gerilmesi\nσmax",                       "structural", "box"),
    "G": (11, 12.0, "Maks. Yer Değiştirme\nδmax",                         "structural", "box"),
    "K": (21, 12.0, "Faydalı Yük Sıcaklığı\nTp = Tr + Q/G",               "thermal",    "box"),

    "H": (3,   9.5, "Eşdeğer Sistem Rijitliği\nk_y (seri yay)",           "structural", "box"),
    "O": (7,   9.5, "Akma Emniyet Katsayısı\nny = σy / σmax",             "structural", "box"),
    "I": (15,  9.5, "Toplam Uydu Kütlesi\nm_toplam",                      "mass",       "box"),
    "L": (21,  9.5, "Sıcaklık Farkı\nΔTpanel = Tp − Tr",                  "thermal",    "box"),

    "J": (7,   6.5, "Birinci Yanal Doğal Frekans\nf1",                    "frequency",  "box"),
    "M": (21,  6.5, "Isıl Uzama\nΔL = αT·(L/2)·ΔTpanel",                  "optical",    "box"),

    "N": (21,  3.5, "OPTİK HİZALAMA /\nBORESIGHT KARARLILIĞI",            "optical",    "box"),

    "T": (3,   1.5, "ny ≥ 1.25 ?",                                        "decision",   "diamond"),
    "P": (7,   1.5, "f1 ≥ 35 Hz ?",                                       "decision",   "diamond"),
    "R": (11,  1.5, "δmax ≤ 1.0 mm ?",                                    "decision",   "diamond"),
    "Q": (17,  1.5, "Tp ≤ 40 °C ?",                                       "decision",   "diamond"),
    "S": (23,  1.5, "ΔL ≤ 0.15 mm ?",                                     "decision",   "diamond"),

    "NOTE": (13, -1.2,
             "⚠️  Not: Kalınlık AZALIRSA tüm oklar TERS yönde işler\n"
             "(rijitlik/frekans/G ↓  —  gerilme/δ/ΔT ↑)",
             "note", "note"),
}

# ---------------------------------------------------------------
# 3) KENAR (EDGE) TANIMLARI -> (kaynak, hedef, etiket, renk_kategorisi, eğrilik, çizgi_stili)
# ---------------------------------------------------------------
EDGES = [
    ("A", "B", "t³ ile ARTIRIR",                 "structural", 0.00, "-"),
    ("A", "C", "lineer ARTIRIR",                 "mass",       0.15, "-"),
    ("A", "D", "lineer ARTIRIR",                  "thermal",    -0.15, "-"),

    ("B", "E", "t³ ile ARTIRIR",                 "structural", 0.00, "-"),
    ("B", "F", "AZALTIR",                        "structural", 0.15, "-"),
    ("B", "G", "AZALTIR",                        "structural", -0.15, "-"),

    ("F", "O", "İYİLEŞTİRİR",                    "structural", 0.00, "-"),
    ("E", "H", "SINIRLI ARTIRIR\n(seri yay etkisi)", "structural", 0.00, "-"),

    ("C", "I", "ARTIRIR",                        "mass",       0.00, "-"),
    ("H", "J", "ARTIRIR",                        "frequency",  0.00, "-"),
    ("I", "J", "AZALTIR\n(kazancı söndürür)",     "mass",       0.20, "-"),

    ("D", "K", "AZALTIR\n(Q sabit)",              "thermal",    0.00, "-"),
    ("K", "L", "AZALTIR",                        "thermal",    0.00, "-"),
    ("L", "M", "AZALTIR",                        "thermal",    0.00, "-"),
    ("M", "N", "İYİLEŞTİRİR",                    "optical",    0.00, "-"),

    # Eşik / gereksinim kontrol bağlantıları (kesikli çizgi)
    ("J", "P", "KIYASLA", "decision", 0.00, "--"),
    ("G", "R", "KIYASLA", "decision", 0.00, "--"),
    ("O", "T", "KIYASLA", "decision", -0.15, "--"),
    ("K", "Q", "KIYASLA", "decision", -0.15, "--"),
    ("M", "S", "KIYASLA", "decision", 0.15, "--"),
]

BOX_W, BOX_H = 3.7, 1.15   # kutu genişlik/yükseklik
DIA_W, DIA_H = 3.6, 1.9    # elmas genişlik/yükseklik


# ---------------------------------------------------------------
# 4) ÇİZİM FONKSİYONLARI
# ---------------------------------------------------------------
def draw_box(ax, x, y, text, category):
    style = CATEGORY_COLORS[category]
    box = FancyBboxPatch(
        (x - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H,
        boxstyle="round,pad=0.06,rounding_size=0.18",
        linewidth=1.6, edgecolor="black", facecolor=style["face"], zorder=3,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.3,
            fontweight="bold", color=style["text"], zorder=4)


def draw_diamond(ax, x, y, text, category):
    style = CATEGORY_COLORS[category]
    verts = [(x, y + DIA_H / 2), (x + DIA_W / 2, y),
             (x, y - DIA_H / 2), (x - DIA_W / 2, y)]
    poly = Polygon(verts, closed=True, linewidth=1.6,
                    edgecolor="black", facecolor=style["face"], zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.0,
            fontweight="bold", color=style["text"], zorder=4)


def draw_note(ax, x, y, text, category):
    style = CATEGORY_COLORS[category]
    box = FancyBboxPatch(
        (x - 8.5, y - 0.9), 17, 1.8,
        boxstyle="round,pad=0.08,rounding_size=0.2",
        linewidth=1.3, edgecolor="#e67e22", facecolor=style["face"],
        linestyle="--", zorder=3,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=8.3,
            fontweight="bold", color=style["text"], zorder=4)


def draw_edge(ax, pos, n1, n2, label, category, rad, linestyle):
    x1, y1, *_ = pos[n1]
    x2, y2, *_ = pos[n2]
    color = CATEGORY_COLORS[category]["face"] if category != "decision" else "#7d6608"

    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=18,
        linewidth=1.8, color=color, linestyle=linestyle,
        shrinkA=28, shrinkB=28, zorder=1, alpha=0.9,
    )
    ax.add_patch(arrow)

    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    my += rad * 2.2  # eğrilik için etiket konumu düzeltmesi
    ax.text(mx, my, label, ha="center", va="center", fontsize=7.3,
            color="black", zorder=5,
            bbox=dict(boxstyle="round,pad=0.18", fc="white",
                      ec=color, lw=0.9, alpha=0.95))


# ---------------------------------------------------------------
# 5) ANA ÇİZİM
# ---------------------------------------------------------------
def main():
    fig, ax = plt.subplots(figsize=(20, 15))
    ax.set_xlim(-1, 27)
    ax.set_ylim(-3, 18.5)
    ax.axis("off")
    ax.set_aspect("equal")

    fig.suptitle(
        "PUHU Uydu Projesi — Panel Kalınlığının Yapısal ve Isıl Parametreler\n"
        "Üzerindeki Zincirleme Etkisi (5.2 Alan Becerisi Ölçen Soru — Madde 9)",
        fontsize=15, fontweight="bold", y=0.985,
    )

    # --- Kenarları çiz (kutuların ALTINDA kalsın diye önce oklar) ---
    for n1, n2, label, cat, rad, style in EDGES:
        draw_edge(ax, NODES, n1, n2, label, cat, rad, style)

    # --- Düğümleri çiz ---
    for node_id, (x, y, text, cat, ntype) in NODES.items():
        if ntype == "box":
            draw_box(ax, x, y, text, cat)
        elif ntype == "diamond":
            draw_diamond(ax, x, y, text, cat)
        elif ntype == "note":
            draw_note(ax, x, y, text, cat)

    # --- Lejant (renk kodu açıklaması) ---
    legend_handles = [
        Patch(facecolor=v["face"], edgecolor="black", label=v["label"])
        for k, v in CATEGORY_COLORS.items() if k != "note"
    ]
    ax.legend(
        handles=legend_handles, loc="upper left",
        bbox_to_anchor=(1.0, 1.0), fontsize=10, title="Kategori Renk Kodları",
        title_fontsize=11, frameon=True, facecolor="white", edgecolor="gray",
    )

    plt.tight_layout()
    output_name = "panel_kalinlik_etkilesim_diyagrami.png"
    plt.savefig(output_name, dpi=300, bbox_inches="tight")
    print(f"[OK] Diyagram kaydedildi -> {output_name}")
    plt.show()


if __name__ == "__main__":
    main()