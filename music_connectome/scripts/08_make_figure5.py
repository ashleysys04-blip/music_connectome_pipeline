"""
Fig 5: Suppressor effect visualization
Compares standardized partial regression coefficients across M1, M2, M3 models
to show how onset and hours coefficients change when included together.
"""
import matplotlib.pyplot as plt
import numpy as np

# Data from summary.md / M1, M2, M3 results
# Each tuple: (model_label, beta_onset, se_onset, beta_hours, se_hours)
data = {
    "M1\n(onset only)":   {"onset": (-0.0919, 0.0885), "hours": None},
    "M2\n(hours only)":   {"onset": None,              "hours": (-0.0388, 0.0801)},
    "M3\n(both)":         {"onset": (-0.2069, 0.1149), "hours": (-0.1580, 0.1035)},
}

models = list(data.keys())
x = np.arange(len(models))
width = 0.36

# Extract values (use 0 for missing so the bar disappears)
onset_b = [data[m]["onset"][0] if data[m]["onset"] else 0 for m in models]
onset_e = [data[m]["onset"][1] if data[m]["onset"] else 0 for m in models]
hours_b = [data[m]["hours"][0] if data[m]["hours"] else 0 for m in models]
hours_e = [data[m]["hours"][1] if data[m]["hours"] else 0 for m in models]

# Colors: muted blue (onset) and muted orange (hours), matching common viz palettes
onset_color = "#3B6BB0"
hours_color = "#E08B3C"

fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=140)

bars_o = ax.bar(x - width/2, onset_b, width,
                yerr=onset_e, capsize=5,
                color=onset_color, edgecolor="black", linewidth=0.7,
                label="Music onset age", zorder=3,
                error_kw={"elinewidth": 1.2, "ecolor": "#333"})
bars_h = ax.bar(x + width/2, hours_b, width,
                yerr=hours_e, capsize=5,
                color=hours_color, edgecolor="black", linewidth=0.7,
                label="Log cumulative hours", zorder=3,
                error_kw={"elinewidth": 1.2, "ecolor": "#333"})

# Zero line
ax.axhline(0, color="black", linewidth=0.9)

# Y-axis: enough room for the largest negative bar + error bar
ax.set_ylim(-0.42, 0.10)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=11)
ax.set_ylabel("Standardized β (PSM as outcome)", fontsize=11)
ax.set_title("Suppressor effect: onset coefficient grows when hours is added\n(trained-only, n≈183)",
             fontsize=12, pad=12)

# Light horizontal grid
ax.yaxis.grid(True, linestyle="--", alpha=0.35, zorder=0)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Annotate beta values above/below each non-empty bar
def annotate(bar, val, se, color):
    if val == 0:
        return
    # place text just outside the error bar
    y = val - se - 0.018 if val < 0 else val + se + 0.012
    ha = "center"
    ax.text(bar.get_x() + bar.get_width()/2, y,
            f"β = {val:+.3f}", ha=ha, va="top" if val < 0 else "bottom",
            fontsize=9.5, color=color, fontweight="bold")

for b, v, s in zip(bars_o, onset_b, onset_e):
    annotate(b, v, s, onset_color)
for b, v, s in zip(bars_h, hours_b, hours_e):
    annotate(b, v, s, hours_color)

# Highlight the suppressor jump with an arrow from M1 onset bar to M3 onset bar
ax.annotate("",
            xy=(x[2] - width/2, -0.207),
            xytext=(x[0] - width/2, -0.092),
            arrowprops=dict(arrowstyle="->", color="#B23A48",
                            lw=1.8, connectionstyle="arc3,rad=-0.25"))
ax.text((x[0] + x[2])/2 - width/2 - 0.05, -0.30,
        "|β| more than doubles\nwhen hours is controlled",
        ha="center", va="center", fontsize=10, color="#B23A48",
        fontstyle="italic")

ax.legend(loc="lower left", frameon=False, fontsize=10)

plt.tight_layout()
out = "/home/claude/work/fig5_suppressor.png"
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"saved -> {out}")