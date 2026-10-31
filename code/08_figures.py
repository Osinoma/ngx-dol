#!/usr/bin/env python3
"""
08_figures.py - Figures for the NGX-DOL data paper.

PLAIN-LANGUAGE NOTE: Draws three charts from the finished data: (1) how much
trading happened and how many stocks traded each month; (2) how illiquid the
typical stock was each year; (3) how concentrated trading was among the top ten
brokers. Each carries a DRAFT stamp until you have checked the data; run with
--final afterwards to remove it. You do not need to open this file.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from nglib import PROC, ROOT

FINAL = "--final" in sys.argv
OUT = os.path.join(ROOT, "paper", "figures"); os.makedirs(OUT, exist_ok=True)
S1, S2 = "#2a78d6", "#eb6834"          # validated categorical slots 1-2 (light surface)
INK, INK2, GRID, BG = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": BG,
                     "axes.facecolor": BG, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
SRC = "Source: NGX-DOL v1.0, built from Nigerian Exchange Ltd Data Library reports, 30 Jun 2014 - 30 Oct 2026."


def stamp(fig):
    if not FINAL:
        fig.text(0.99, 0.99, "DRAFT - not verified", ha="right", va="top", color="#d03b3b", fontsize=9, weight="bold")
    fig.text(0.01, -0.04, SRC, ha="left", va="bottom", color=INK2, fontsize=7)


def save(fig, name):
    stamp(fig); fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches="tight"); plt.close(fig)


def main():
    D = pd.read_csv(os.path.join(PROC, "ngxdol_daily.csv"), parse_dates=["date"],
                    usecols=["date", "symbol", "traded", "in_official_list", "universe_imputed", "value", "day_trades_missing"])
    D = D[~D.day_trades_missing]
    day = D.groupby("date").agg(value=("value", "sum"), traded=("traded", "sum"),
                                listed=("symbol", "size"))
    m = day.resample("ME").agg({"value": "sum", "traded": "mean", "listed": "mean"})

    # Figure 1: activity
    fig, ax = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True, gridspec_kw={"hspace": 0.25})
    ax[0].plot(m.index, m.value / 1e9, color=S1, lw=2)
    ax[0].set_ylabel("NGN billion per month"); ax[0].set_title("a. Value of equities traded", loc="left", color=INK, fontsize=10)
    ax[1].plot(m.index, m.listed, color=S2, lw=2); ax[1].plot(m.index, m.traded, color=S1, lw=2)
    ax[1].text(m.index[-1], m.listed.iloc[-1] + 4, " listed", color=INK2, va="bottom", ha="right")
    ax[1].text(m.index[-1], m.traded.iloc[-1] - 4, " traded", color=INK2, va="top", ha="right")
    ax[1].set_ylabel("securities per day (monthly mean)")
    ax[1].set_title("b. Securities listed vs. traded on a typical day", loc="left", color=INK, fontsize=10)
    ax[1].legend(["listed", "traded"], frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.08), ncol=2)
    ax[1].set_title("b. Securities listed vs. traded on a typical day", loc="left", color=INK, fontsize=10, pad=22)
    save(fig, "fig1_activity.png")

    # Figure 2: illiquidity
    Mo = pd.read_csv(os.path.join(PROC, "ngxdol_monthly.csv"))
    Mo["year"] = Mo.month.str[:4].astype(int)
    y = Mo.groupby("year").agg(zr=("zero_return_share", "mean"), am=("amihud_mean", "median"))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.35})
    ax[0].plot(y.index, y.zr * 100, color=S1, lw=2, marker="o", ms=4)
    ax[0].set_ylim(0, 100); ax[0].set_ylabel("% of listed days")
    ax[0].set_title("a. Zero-return days, mean stock-month", loc="left", color=INK, fontsize=10)
    ax[1].plot(y.index, y.am, color=S1, lw=2, marker="o", ms=4); ax[1].set_yscale("log")
    ax[1].set_ylabel("|return| per NGN million traded")
    ax[1].set_title("b. Amihud illiquidity, median stock-month", loc="left", color=INK, fontsize=10)
    for a in ax:
        a.set_xticks(range(2014, 2027, 2))
    save(fig, "fig2_illiquidity.png")

    # Figure 3: broker concentration
    C = pd.read_csv(os.path.join(PROC, "ngxdol_broker_concentration.csv"), parse_dates=["week_end"])
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    for meas, col in (("volume", S1), ("value", S2)):
        c = C[C.measure == meas].set_index("week_end").sort_index().cr10.clip(upper=1) * 100
        r = c.rolling(13, min_periods=6).median()
        ax.plot(r.index, r, color=col, lw=2, label=f"share of {meas}")
    ax.set_ylim(0, 100); ax.set_ylabel("top-10 brokers' share, % (13-week median)")
    ax.set_title("Concentration of trading among the ten largest brokers", loc="left", color=INK, fontsize=10)
    ax.legend(frameon=False, loc="lower left")
    save(fig, "fig3_broker_cr10.png")
    print("figures written", "(final)" if FINAL else "(DRAFT)")


if __name__ == "__main__":
    main()
