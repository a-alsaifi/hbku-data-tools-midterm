#!/usr/bin/env python3
"""Generate EDA PDF report for the Kaggle House Prices dataset."""

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "train.csv")
PLOT_DIR = os.path.join(BASE_DIR, "plots")
OUTPUT_PDF = os.path.join(BASE_DIR, "EDA_Report.pdf")
os.makedirs(PLOT_DIR, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(include="object").columns.tolist()

# ══════════════════════════════════════════════════════════════════════════════
#  REPORT CLASS  (mirrors generate_report.py styling)
# ══════════════════════════════════════════════════════════════════════════════

class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "House Prices Dataset - EDA Report", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(230, 230, 250)
        self.cell(0, 9, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 120)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 5, text)
        self.ln(1)

    # ── New helpers ────────────────────────────────────────────────────────────
    def add_plot(self, title, image_path, w=180):
        """Embed a saved PNG image with a subtitle."""
        if self.get_y() + 100 > 270:
            self.add_page()
        self.sub_title(title)
        self.image(image_path, x=15, w=w)
        self.ln(4)

    def finding_table(self, headers, rows, col_widths=None):
        """Generic table for analysis results."""
        n = len(headers)
        if col_widths is None:
            col_widths = [190 // n] * n
            col_widths[-1] = 190 - sum(col_widths[:-1])
        # header row
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(200, 200, 220)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, fill=True)
        self.ln()
        # data rows
        self.set_font("Helvetica", "", 7.5)
        for row in rows:
            x0, y0 = self.get_x(), self.get_y()
            if y0 + 10 > 270:
                self.add_page()
                x0, y0 = self.get_x(), self.get_y()
            max_y = y0
            for i, val in enumerate(row):
                self.set_xy(x0 + sum(col_widths[:i]), y0)
                self.multi_cell(col_widths[i], 5, str(val), border=1)
                max_y = max(max_y, self.get_y())
            self.set_y(max_y)
        self.ln(2)


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def iqr_outliers(series):
    """Return boolean mask of IQR outliers."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)


def plot_outlier_boxplot():
    """Box plot of SalePrice with outlier count annotation."""
    fig, ax = plt.subplots(figsize=(10, 5))
    mask = iqr_outliers(df["SalePrice"])
    bp = ax.boxplot(df["SalePrice"].dropna(), vert=False, widths=0.6,
                    flierprops=dict(marker="o", markerfacecolor="red", markersize=4, alpha=0.5))
    ax.set_xlabel("SalePrice ($)", fontsize=11)
    ax.set_title(f"SalePrice Box Plot  ({mask.sum()} IQR outliers out of {len(df)})", fontsize=12)
    ax.ticklabel_format(style="plain", axis="x")
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "outlier_saleprice_boxplot.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_outlier_scatter(xcol, ycol="SalePrice", fname=None):
    """Scatter plot with IQR outliers highlighted in red."""
    fig, ax = plt.subplots(figsize=(10, 6))
    mask_x = iqr_outliers(df[xcol])
    mask_y = iqr_outliers(df[ycol])
    mask = mask_x | mask_y
    ax.scatter(df.loc[~mask, xcol], df.loc[~mask, ycol],
               c="steelblue", alpha=0.5, s=18, label="Normal")
    ax.scatter(df.loc[mask, xcol], df.loc[mask, ycol],
               c="red", alpha=0.7, s=24, label="Outlier", edgecolors="darkred", linewidths=0.5)
    # annotate the most extreme points
    extremes = df.loc[mask].nlargest(3, xcol)
    for _, r in extremes.iterrows():
        ax.annotate(f"Id {int(r['Id'])}", (r[xcol], r[ycol]),
                    fontsize=7, color="darkred",
                    textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel(xcol, fontsize=11)
    ax.set_ylabel(ycol, fontsize=11)
    ax.set_title(f"{xcol} vs {ycol}  (outliers in red)", fontsize=12)
    ax.legend(fontsize=9)
    ax.ticklabel_format(style="plain", axis="both")
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, fname or f"outlier_{xcol.lower()}_scatter.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def outlier_summary():
    """Return rows for the outlier summary table."""
    rows = []
    for col in ["SalePrice", "GrLivArea", "LotArea"]:
        mask = iqr_outliers(df[col])
        cnt = mask.sum()
        pct = f"{100 * cnt / len(df):.1f}%"
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lo = q1 - 1.5 * iqr
        hi = q3 + 1.5 * iqr
        rows.append((col, str(cnt), pct, f"{lo:,.0f}", f"{hi:,.0f}"))
    return rows


# ── Correlation / redundancy ──────────────────────────────────────────────────

def plot_correlation_heatmap():
    """Heatmap of top-correlated numeric features."""
    corr = df[numeric_cols].corr()
    # select features involved in pairs with |r|>0.7 for readability
    high = set()
    for i in range(len(corr)):
        for j in range(i + 1, len(corr)):
            if abs(corr.iloc[i, j]) > 0.7:
                high.add(corr.index[i])
                high.add(corr.columns[j])
    high = sorted(high)
    sub = corr.loc[high, high]
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(sub, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                linewidths=0.4, ax=ax, annot_kws={"size": 7})
    ax.set_title("Correlation Heatmap (features with |r| > 0.7)", fontsize=13)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "correlation_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def get_redundant_pairs(threshold=0.80):
    """Return list of (col_a, col_b, r) where |r| > threshold."""
    corr = df[numeric_cols].corr()
    pairs = []
    for i in range(len(corr)):
        for j in range(i + 1, len(corr)):
            r = corr.iloc[i, j]
            if abs(r) > threshold:
                pairs.append((corr.index[i], corr.columns[j], round(r, 4)))
    pairs.sort(key=lambda x: -abs(x[2]))
    return pairs


def plot_redundancy_bars(pairs):
    """Horizontal bar chart of the most correlated pairs."""
    labels = [f"{a} / {b}" for a, b, _ in pairs]
    vals = [abs(r) for _, _, r in pairs]
    fig, ax = plt.subplots(figsize=(10, max(4, len(pairs) * 0.55)))
    colors = ["#d9534f" if v > 0.85 else "#f0ad4e" for v in vals]
    ax.barh(labels, vals, color=colors, edgecolor="grey", linewidth=0.5)
    ax.set_xlabel("|Pearson r|", fontsize=11)
    ax.set_title("Highly Correlated Feature Pairs (|r| > 0.80)", fontsize=12)
    ax.axvline(0.80, color="black", linestyle="--", linewidth=0.8, label="threshold 0.80")
    ax.legend(fontsize=9)
    ax.set_xlim(0.75, 1.0)
    for i, v in enumerate(vals):
        ax.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=8)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "redundancy_top_pairs.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ── Same-value dominated attributes ──────────────────────────────────────────

def get_same_value_attrs(threshold=90):
    """Return list of (col, dominant_value, pct) where mode frequency > threshold %."""
    results = []
    for col in df.columns:
        mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else np.nan
        freq = (df[col] == mode_val).sum()
        pct = 100 * freq / len(df)
        if pct > threshold:
            results.append((col, str(mode_val), round(pct, 2)))
    results.sort(key=lambda x: -x[2])
    return results


def plot_same_value_bars(attrs):
    """Horizontal bar chart of same-value dominated attributes."""
    labels = [f"{col} (={val})" for col, val, _ in attrs]
    pcts = [p for _, _, p in attrs]
    fig, ax = plt.subplots(figsize=(10, max(4, len(attrs) * 0.55)))
    ax.barh(labels, pcts, color="#5bc0de", edgecolor="grey", linewidth=0.5)
    ax.axvline(90, color="red", linestyle="--", linewidth=1, label="90% threshold")
    ax.set_xlabel("Mode Frequency (%)", fontsize=11)
    ax.set_title("Attributes Dominated by a Single Value (> 90%)", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_xlim(85, 101)
    for i, v in enumerate(pcts):
        ax.text(min(v + 0.3, 100.5), i, f"{v:.1f}%", va="center", fontsize=8)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "same_value_attributes.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ── Categorical merging ──────────────────────────────────────────────────────

def plot_categorical_bar(col, fname=None):
    """Bar chart with 5% threshold line; below-threshold bars in red."""
    counts = df[col].value_counts().sort_values(ascending=True)
    threshold = 0.05 * len(df)  # ~73
    colors = ["#d9534f" if v < threshold else "steelblue" for v in counts.values]
    fig, ax = plt.subplots(figsize=(10, max(4, len(counts) * 0.45)))
    ax.barh(counts.index.astype(str), counts.values, color=colors,
            edgecolor="grey", linewidth=0.5)
    ax.axvline(threshold, color="red", linestyle="--", linewidth=1,
               label=f"5% threshold ({int(threshold)} records)")
    ax.set_xlabel("Count", fontsize=11)
    ax.set_title(f"Category Frequencies: {col}", fontsize=12)
    ax.legend(fontsize=9)
    for i, v in enumerate(counts.values):
        ax.text(v + 2, i, str(v), va="center", fontsize=8)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, fname or f"categorical_{col.lower()}.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def merge_candidates(col, threshold_pct=5):
    """Return categories below the threshold."""
    counts = df[col].value_counts()
    threshold = threshold_pct / 100 * len(df)
    return [(cat, cnt, f"{100*cnt/len(df):.1f}%")
            for cat, cnt in counts.items() if cnt < threshold]


# ══════════════════════════════════════════════════════════════════════════════
#  BUILD PDF
# ══════════════════════════════════════════════════════════════════════════════

def build_report():
    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()

    # ── Title Page ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.ln(30)
    pdf.cell(0, 12, "House Prices - Ames, Iowa", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Exploratory Data Analysis (EDA) Report", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Data Tools and Applications - Spring 2026", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "HBKU", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Ali Al-Saifi", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "ID: 210089822", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "This report presents an Exploratory Data Analysis (EDA) of the Ames, Iowa "
        "housing dataset from the Kaggle 'House Prices: Advanced Regression Techniques' "
        "competition. The dataset contains 1,460 residential property sales with 81 features "
        "describing almost every aspect of the homes. The analysis covers outlier detection, "
        "redundant attribute identification, same-value dominated attributes, and categorical "
        "merging recommendations.\n\n"
        "Dataset: https://www.kaggle.com/c/house-prices-advanced-regression-techniques"
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 1 - Dataset Overview
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("1. Dataset Overview")

    n_rows, n_cols = df.shape
    n_num = len(numeric_cols)
    n_cat = len(categorical_cols)
    pdf.body_text(
        f"The training dataset contains {n_rows:,} rows and {n_cols} columns.\n"
        f"  - Numeric attributes: {n_num}\n"
        f"  - Categorical attributes: {n_cat}\n"
        f"  - Target variable: SalePrice"
    )

    # Missing values
    pdf.sub_title("Top Missing-Value Columns")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(15)
    miss_rows = []
    for col_name, cnt in missing.items():
        miss_rows.append((col_name, str(cnt), f"{100*cnt/n_rows:.1f}%"))
    pdf.finding_table(
        ["Column", "Missing Count", "% Missing"],
        miss_rows,
        col_widths=[60, 50, 80]
    )

    pdf.body_text(
        "Columns like PoolQC, MiscFeature, Alley, Fence, and FireplaceQu have very high "
        "missing rates (> 45%). Many of these represent features that simply do not exist "
        "for the property (e.g., no pool, no alley access) and are coded as NaN."
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 2 - Outlier Detection (Task 1)
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("2. Outlier Detection (Task 1)")
    pdf.body_text(
        "Outliers are identified using the Interquartile Range (IQR) method. A data point "
        "is considered an outlier if it falls below Q1 - 1.5*IQR or above Q3 + 1.5*IQR. "
        "Three key attributes are examined: SalePrice, GrLivArea vs SalePrice, and "
        "LotArea vs SalePrice."
    )

    # box plot
    bp_path = plot_outlier_boxplot()
    pdf.add_plot("2.1  SalePrice Distribution (Box Plot)", bp_path)

    # scatter plots
    sc1_path = plot_outlier_scatter("GrLivArea", fname="outlier_grlivarea_scatter.png")
    pdf.add_plot("2.2  GrLivArea vs SalePrice", sc1_path)

    sc2_path = plot_outlier_scatter("LotArea", fname="outlier_lotarea_scatter.png")
    pdf.add_plot("2.3  LotArea vs SalePrice", sc2_path)

    # summary table
    pdf.sub_title("2.4  Outlier Summary")
    o_rows = outlier_summary()
    pdf.finding_table(
        ["Attribute", "Outlier Count", "% of Data", "Lower Bound", "Upper Bound"],
        o_rows,
        col_widths=[35, 30, 25, 50, 50]
    )
    pdf.body_text(
        "SalePrice has the most outliers by count, concentrated on the upper end (expensive "
        "homes). LotArea has a handful of extremely large lots that could heavily influence "
        "regression models. The two large GrLivArea outliers (~4,500+ sq ft) with low sale "
        "prices are well-known anomalies often removed in modeling."
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 3 - Redundant Attributes (Task 2)
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("3. Redundant Attributes (Task 2)")
    pdf.body_text(
        "Redundant attributes are identified using Pearson correlation. Pairs of numeric "
        "features with |r| > 0.80 are flagged as potentially redundant, meaning one could "
        "be dropped without significant information loss."
    )

    hm_path = plot_correlation_heatmap()
    pdf.add_plot("3.1  Correlation Heatmap (features with |r| > 0.7)", hm_path)

    pairs = get_redundant_pairs(0.80)
    bp_path = plot_redundancy_bars(pairs)
    pdf.add_plot("3.2  Highly Correlated Feature Pairs", bp_path)

    pdf.sub_title("3.3  Redundant Pairs (|r| > 0.80)")
    recommend = {
        ("GarageArea", "GarageCars"): "Keep GarageCars (more interpretable, fewer outliers).",
        ("GarageCars", "GarageArea"): "Keep GarageCars (more interpretable, fewer outliers).",
        ("TotalBsmtSF", "1stFlrSF"): "Keep TotalBsmtSF (captures full basement info).",
        ("1stFlrSF", "TotalBsmtSF"): "Keep TotalBsmtSF (captures full basement info).",
        ("GrLivArea", "TotRmsAbvGrd"): "Keep GrLivArea (continuous, more precise).",
        ("TotRmsAbvGrd", "GrLivArea"): "Keep GrLivArea (continuous, more precise).",
        ("YearBuilt", "GarageYrBlt"): "Keep YearBuilt (fewer missing values).",
        ("GarageYrBlt", "YearBuilt"): "Keep YearBuilt (fewer missing values).",
    }
    pair_rows = []
    for a, b, r in pairs:
        rec = recommend.get((a, b), "Consider dropping one based on domain context.")
        pair_rows.append((a, b, f"{r:.4f}", rec))
    pdf.finding_table(
        ["Feature A", "Feature B", "Pearson r", "Recommendation"],
        pair_rows,
        col_widths=[35, 35, 25, 95]
    )
    pdf.body_text(
        "The strongest redundancy is between GarageArea and GarageCars (r ~ 0.88). "
        "Keeping one from each pair reduces multicollinearity without losing predictive power."
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 4 - Same-Value Dominated Attributes (Task 3)
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("4. Same-Value Dominated Attributes (Task 3)")
    pdf.body_text(
        "Attributes where a single value accounts for more than 90% of all observations "
        "provide very little discriminative power and are candidates for removal."
    )

    sv_attrs = get_same_value_attrs(90)
    sv_path = plot_same_value_bars(sv_attrs)
    pdf.add_plot("4.1  Attributes with > 90% Same Value", sv_path)

    pdf.sub_title("4.2  Flagged Attributes")
    sv_rows = [(col, val, f"{pct:.1f}%") for col, val, pct in sv_attrs]
    pdf.finding_table(
        ["Attribute", "Dominant Value", "Frequency %"],
        sv_rows,
        col_widths=[50, 70, 70]
    )
    pdf.body_text(
        "Utilities is almost entirely 'AllPub' (99.9%) and carries virtually zero information. "
        "Street (99.6% 'Pave'), PoolArea (99.5% value 0), and several condition/functional "
        "columns are similarly dominated. These attributes can typically be dropped from "
        "predictive models without impact."
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 5 - Categorical Merging (Task 4)
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("5. Categorical Merging Analysis (Task 4)")
    pdf.body_text(
        "For categorical attributes, categories with fewer than 5% of observations "
        f"(< {int(0.05 * len(df))} records) are flagged as merge candidates. Merging rare "
        "categories into an 'Other' group reduces sparsity and improves model stability."
    )

    # MSZoning
    mz_path = plot_categorical_bar("MSZoning", "categorical_mszoning.png")
    pdf.add_plot("5.1  MSZoning - Category Frequencies", mz_path)
    mz_cands = merge_candidates("MSZoning")
    if mz_cands:
        pdf.body_text(
            "Merge candidates (< 5%): " +
            ", ".join(f"{c} ({p})" for c, _, p in mz_cands) +
            ". Recommendation: merge these into 'Other' or combine with the closest "
            "zoning type (e.g., RH and RM could merge into 'Residential_Medium')."
        )
    else:
        pdf.body_text("No categories fall below the 5% threshold for MSZoning.")

    # SaleCondition
    sc_path = plot_categorical_bar("SaleCondition", "categorical_salecondition.png")
    pdf.add_plot("5.2  SaleCondition - Category Frequencies", sc_path)
    sc_cands = merge_candidates("SaleCondition")
    if sc_cands:
        pdf.body_text(
            "Merge candidates (< 5%): " +
            ", ".join(f"{c} ({p})" for c, _, p in sc_cands) +
            ". Recommendation: merge AdjLand, Alloca, and Family into 'Other_Condition'."
        )
    else:
        pdf.body_text("No categories fall below the 5% threshold for SaleCondition.")

    # Neighborhood
    nb_path = plot_categorical_bar("Neighborhood", "categorical_neighborhood.png")
    pdf.add_plot("5.3  Neighborhood - Category Frequencies", nb_path)
    nb_cands = merge_candidates("Neighborhood")
    if nb_cands:
        pdf.body_text(
            f"Merge candidates (< 5%): {len(nb_cands)} neighborhoods fall below the threshold. "
            "Recommendation: group rare neighborhoods by geographic proximity or median "
            "SalePrice similarity into broader clusters (e.g., 'Low_Density', 'Mid_Range')."
        )
    else:
        pdf.body_text("No categories fall below the 5% threshold for Neighborhood.")

    # ══════════════════════════════════════════════════════════════════════════
    #  Section 6 - Conclusions
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("6. Conclusions")
    pdf.body_text(
        "1. Outlier Detection: The IQR method identified outliers in SalePrice, GrLivArea, "
        "and LotArea. Two well-known GrLivArea outliers (large area, low price) should be "
        "removed before modeling. Extreme LotArea values may also warrant capping or removal."
    )
    pdf.body_text(
        "2. Redundant Attributes: Four pairs of features have |r| > 0.80: "
        "GarageArea/GarageCars, TotalBsmtSF/1stFlrSF, GrLivArea/TotRmsAbvGrd, and "
        "YearBuilt/GarageYrBlt. Dropping one feature from each pair reduces multicollinearity "
        "with minimal information loss."
    )
    pdf.body_text(
        "3. Same-Value Attributes: Several columns are dominated by a single value "
        "(> 90%), most notably Utilities (99.9% AllPub), Street (99.6% Pave), and PoolArea "
        "(99.5% zero). These provide negligible predictive value and can be safely removed."
    )
    pdf.body_text(
        "4. Categorical Merging: Rare categories exist in MSZoning, SaleCondition, and "
        "especially Neighborhood. Merging these below-threshold categories reduces sparsity "
        "and prevents overfitting during one-hot encoding."
    )
    pdf.body_text(
        "These preprocessing steps form a solid foundation for subsequent feature engineering "
        "and predictive modeling on the Ames housing dataset."
    )

    # ── Save ───────────────────────────────────────────────────────────────────
    pdf.output(OUTPUT_PDF)
    print(f"Report saved to: {OUTPUT_PDF}")
    print(f"Plots saved to: {PLOT_DIR}/")


if __name__ == "__main__":
    build_report()
