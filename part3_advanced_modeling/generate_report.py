#!/usr/bin/env python3
"""Generate PDF report for Part 3: Advanced Modeling & Ensemble Methods."""

import os
from fpdf import FPDF


class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "House Prices - Advanced Modeling Report", align="C",
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

    def add_plot(self, title, image_path, w=180):
        if self.get_y() + 100 > 270:
            self.add_page()
        self.sub_title(title)
        self.image(image_path, x=15, w=w)
        self.ln(4)

    def finding_table(self, headers, rows, col_widths=None):
        n = len(headers)
        if col_widths is None:
            col_widths = [190 // n] * n
            col_widths[-1] = 190 - sum(col_widths[:-1])
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(200, 200, 220)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6, h, border=1, fill=True)
        self.ln()
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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE_DIR, "plots")
OUTPUT_PDF = os.path.join(BASE_DIR, "Advanced_Modeling_Report.pdf")


def build_report():
    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()

    # ── Title Page ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.ln(30)
    pdf.cell(0, 12, "House Prices - Ames, Iowa", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Advanced Modeling & Ensemble Report", align="C",
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
        "This report presents advanced modeling techniques for the Ames, Iowa "
        "housing dataset from the Kaggle 'House Prices: Advanced Regression "
        "Techniques' competition. Building on Part 2's baseline (0.13881 RMSE), "
        "this part implements domain-specific preprocessing, feature engineering, "
        "skewness correction, and model stacking to achieve a target of < 0.11 RMSE.\n\n"
        "Dataset: https://www.kaggle.com/c/house-prices-advanced-regression-techniques"
    )

    # ── 1. Introduction ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("1. Introduction")
    pdf.body_text(
        "Part 2 achieved a Kaggle score of 0.13881 RMSE using XGBoost with "
        "hyperparameter tuning. While tuning improved over the default model, "
        "the score still falls short of the < 0.11 RMSE target required for "
        "full marks. The primary gaps identified were:\n\n"
        "  1. Basic preprocessing (blanket median fill, no domain knowledge)\n"
        "  2. No feature engineering beyond the raw 79 features\n"
        "  3. No skewness correction on numeric features\n"
        "  4. Single model (XGBoost) without ensemble methods\n\n"
        "This notebook addresses all four gaps through advanced techniques."
    )

    # ── 2. Improved Preprocessing ─────────────────────────────────────────
    pdf.section_title("2. Improved Preprocessing")
    pdf.body_text(
        "Instead of blanket median/None fill, domain-specific imputation was applied:"
    )
    pdf.finding_table(
        ["Feature(s)", "Strategy", "Rationale"],
        [
            ("Garage/Bsmt/Pool/Fence", "Fill 'None' or 0", "NA means feature absent"),
            ("LotFrontage", "Median per Neighborhood", "Similar lots in same area"),
            ("MSZoning, Electrical, etc.", "Mode of column", "Most common value"),
            ("Functional", "Fill 'Typ'", "Per data description: NA = Typical"),
            ("Utilities", "Dropped", "Near-zero variance (99.9% AllPub)"),
        ],
        col_widths=[55, 55, 80],
    )
    pdf.body_text(
        "The neighborhood-based LotFrontage imputation is particularly impactful "
        "because lot frontage is strongly correlated with neighborhood characteristics."
    )

    # ── 3. Feature Engineering ────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("3. Feature Engineering")
    pdf.body_text(
        "18 new features were created on the combined train+test dataset before "
        "encoding. These features capture domain knowledge about housing value:"
    )
    pdf.finding_table(
        ["Category", "Features", "Description"],
        [
            ("Area Aggregates", "TotalSF, TotalPorchSF, TotalBath, TotalFinBsmtSF",
             "Combined area/count features"),
            ("Binary Indicators", "HasPool, HasGarage, HasBsmt, HasFireplace, "
             "Has2ndFlr, IsNew, IsRemodeled", "Presence/absence flags"),
            ("Age Features", "HouseAge, RemodAge, GarageAge",
             "Years since built/remodeled"),
            ("Quality Interactions", "OverallScore, ExterScore, GarageScore, "
             "KitchenScore, TotalQual", "Quality * Condition products"),
            ("Polynomial", "OverallQual^2, GrLivArea^2, TotalSF^2",
             "Non-linear relationships"),
        ],
        col_widths=[40, 75, 75],
    )
    pdf.body_text(
        "TotalSF (total square footage) and OverallQual^2 are typically the most "
        "impactful engineered features for this dataset. The polynomial features "
        "capture the non-linear relationship between quality/size and price."
    )

    # ── 4. Skewness Correction ────────────────────────────────────────────
    pdf.section_title("4. Skewness Correction (Box-Cox)")
    pdf.body_text(
        "Many numeric features in the Ames dataset are highly right-skewed "
        "(e.g., lot area, basement SF, porch SF). Skewed features can degrade "
        "performance of linear models. Box-Cox1p transformation was applied to "
        "all features with |skewness| > 0.75.\n\n"
        "The Box-Cox transformation finds the optimal power parameter lambda "
        "that makes the distribution as close to normal as possible."
    )
    plot_path = os.path.join(PLOT_DIR, "skewness_before_after.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Skewness Distribution Before vs After Box-Cox", plot_path)

    # ── 5. Feature Selection ──────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("5. Feature Selection (Lasso)")
    pdf.body_text(
        "After encoding, the feature space expanded significantly due to one-hot "
        "encoding. Lasso regression (alpha=0.0005) was used to identify and remove "
        "noisy features by zeroing out irrelevant coefficients. Features with "
        "|coefficient| > 1e-4 were retained.\n\n"
        "This reduces overfitting risk and improves generalization, especially for "
        "linear models in the ensemble."
    )
    plot_path = os.path.join(PLOT_DIR, "feature_importance.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Top 30 Features by Lasso Coefficient", plot_path)

    # ── 6. Individual Models ──────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("6. Individual Models")
    pdf.body_text(
        "Eight diverse models were trained and evaluated with 10-fold CV. "
        "The ensemble benefits from diversity: regularized linear models "
        "(RidgeCV, LassoCV, ElasticNetCV), support vector regression (SVR), "
        "and tree-based models (GBR, XGBoost, LightGBM). Each linear model "
        "uses a per-pipeline RobustScaler and CV-tuned alpha.\n\n"
        "The best Kaggle submission (v7, 0.12038 RMSE) used models with "
        "hyperparameters matched to top-scoring competition kernels, including "
        "very shallow LightGBM trees (num_leaves=4) and slow-learning XGBoost "
        "(lr=0.01, 3460 estimators)."
    )
    pdf.finding_table(
        ["Model", "Key Hyperparameters", "10-fold CV RMSE"],
        [
            ("RidgeCV", "alpha~15, RobustScaler pipeline", "0.1037"),
            ("LassoCV", "alpha via CV, RobustScaler pipeline", "0.1058"),
            ("ElasticNetCV", "alpha+l1_ratio via CV, RobustScaler", "0.1056"),
            ("SVR", "C=20, epsilon=0.008, gamma=0.0003", "0.1033"),
            ("GradientBoosting", "3000 trees, lr=0.05, Huber loss", "0.1062"),
            ("XGBoost", "3460 trees, lr=0.01, max_depth=3", "0.1070"),
            ("LightGBM", "5000 trees, lr=0.01, num_leaves=4", "0.1065"),
        ],
        col_widths=[45, 80, 65],
    )
    plot_path = os.path.join(PLOT_DIR, "model_comparison.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Individual Model Comparison", plot_path)
    plot_path = os.path.join(PLOT_DIR, "cv_scores_boxplot.png")
    if os.path.exists(plot_path):
        pdf.add_plot("CV Score Distribution", plot_path)

    # ── 7. Ensemble Methods ───────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("7. Ensemble Methods")
    pdf.body_text(
        "Multiple ensemble approaches were compared, progressing from simple "
        "to advanced:"
    )
    pdf.sub_title("Approach A: Weighted Average")
    pdf.body_text(
        "Optimal weights for each base model's OOF predictions were found via "
        "scipy.optimize.minimize (SLSQP). Weights are constrained to sum to 1."
    )
    pdf.sub_title("Approach B: Stacking with Meta-Learner")
    pdf.body_text(
        "Out-of-fold (OOF) predictions from all base models serve as features "
        "for a Lasso meta-learner. Proper OOF generation prevents data leakage: "
        "each fold's validation predictions come from a model that never saw "
        "those samples during training. A secondary meta-stacking approach feeds "
        "both OOF predictions AND original features to an XGBoost meta-regressor."
    )
    pdf.sub_title("Approach C: Top-Kernel Weighted Blend (Best)")
    pdf.body_text(
        "Based on analysis of top-scoring Kaggle kernels, the best submission "
        "uses a weighted blend of 8 components:\n"
        "  10% ElasticNet + 5% Lasso + 10% Ridge + 10% SVR +\n"
        "  10% GBR + 15% XGBoost + 10% LightGBM + 30% Meta-Stack\n\n"
        "The meta-stack component (30% weight) is the largest single contributor. "
        "This configuration mirrors the approach used by the #1 kernel on the "
        "competition leaderboard."
    )
    plot_path = os.path.join(PLOT_DIR, "ensemble_comparison.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Ensemble Method Comparison", plot_path)

    # ── 8. Results ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("8. Results & Diagnostics")
    plot_path = os.path.join(PLOT_DIR, "residuals_plot.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Residual Analysis", plot_path)
    plot_path = os.path.join(PLOT_DIR, "prediction_vs_actual.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Prediction vs Actual", plot_path)
    pdf.body_text(
        "The residuals plot shows predictions are well-centered around zero with "
        "no systematic bias. The prediction vs actual plot shows strong alignment "
        "along the diagonal, with some deviation at extreme values (very expensive "
        "or very cheap houses)."
    )

    # ── 9. Kaggle Score ──────────────────────────────────────────────────
    pdf.section_title("9. Kaggle Submission Score")
    screenshot_path = os.path.join(BASE_DIR, "score_screenshot.png")
    if os.path.exists(screenshot_path):
        pdf.add_plot("Kaggle Leaderboard Score", screenshot_path)
    pdf.body_text(
        "The best ensemble model's predictions were submitted to Kaggle.\n\n"
        "Part 2 Score: 0.13881 RMSE\n"
        "Part 3 Score: 0.12038 RMSE (best submission)\n\n"
        "Improvement: 0.01843 RMSE reduction (13.3% relative improvement).\n\n"
        "Multiple ensemble strategies were evaluated on Kaggle:\n"
        "  - Top-kernel blend (8 models + meta-stack, Box-Cox lam=0.15): 0.12038\n"
        "  - Meta-blend (50/50 topkernel + simple avg): 0.12111\n"
        "  - Top-kernel blend with prediction clipping: 0.12211\n"
        "  - Simple average (6 models, no Box-Cox): 0.12217\n\n"
        "Key models: RidgeCV, LassoCV, ElasticNetCV, SVR (C=20), GBR (3000 trees),\n"
        "XGBoost (3460 trees, lr=0.01), LightGBM (5000 trees, num_leaves=4).\n\n"
        "The submission contains 1,459 predictions (Id range 1461-2919) with "
        "all prices > 0."
    )

    # ── 10. Conclusions ──────────────────────────────────────────────────
    pdf.section_title("10. Conclusions")
    pdf.body_text(
        "1. Domain-specific imputation (especially LotFrontage by neighborhood) "
        "improved data quality compared to blanket median fill.\n\n"
        "2. Feature engineering added 18 meaningful features capturing area totals, "
        "quality interactions, age, and polynomial relationships.\n\n"
        "3. Box-Cox skewness correction normalized highly skewed features, "
        "improving linear model performance.\n\n"
        "4. Lasso-based feature selection removed noisy features, reducing "
        "overfitting risk.\n\n"
        "5. A diverse 8-model ensemble (including SVR) with proper OOF stacking "
        "achieved significant improvement over any single model.\n\n"
        "6. The top-kernel weighted blend (30% meta-stack + 7 base models) "
        "provides a robust final prediction combining the strengths of different "
        "model families. SVR was a critical addition providing unique diversity.\n\n"
        "7. Using a fixed Box-Cox lambda (0.15) instead of per-feature optimal "
        "lambda improved generalization. Using CV-tuned alphas (RidgeCV, LassoCV) "
        "instead of fixed alphas also helped.\n\n"
        "8. LightGBM with very shallow trees (num_leaves=4) and slow learning "
        "(lr=0.01, 5000 estimators) significantly outperformed the Optuna-tuned "
        "version, demonstrating that strong regularization trumps optimization.\n\n"
        "GitHub Repository: https://github.com/alialsaifi/hbku-data-tools-midterm"
    )

    pdf.output(OUTPUT_PDF)
    print(f"Report saved to: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_report()
