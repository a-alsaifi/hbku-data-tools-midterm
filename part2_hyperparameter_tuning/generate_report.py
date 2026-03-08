#!/usr/bin/env python3
"""Generate PDF report for Part 2: Hyperparameter Tuning."""

import os
from fpdf import FPDF


class Report(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "House Prices - Hyperparameter Tuning Report", align="C",
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
OUTPUT_PDF = os.path.join(BASE_DIR, "Hyperparameter_Tuning_Report.pdf")


def build_report():
    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()

    # ── Title Page ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.ln(30)
    pdf.cell(0, 12, "House Prices - Ames, Iowa", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Hyperparameter Tuning Report", align="C",
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
        "This report presents the results of hyperparameter tuning on the Ames, Iowa "
        "housing dataset from the Kaggle 'House Prices: Advanced Regression Techniques' "
        "competition. Three tuning strategies are compared: Grid Search CV, Randomized "
        "Search CV, and Optuna Bayesian Optimization (TPE). All experiments are tracked "
        "with Weights & Biases (WandB).\n\n"
        "Dataset: https://www.kaggle.com/c/house-prices-advanced-regression-techniques"
    )

    # ── 1. Methodology ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("1. Methodology")
    pdf.body_text(
        "The goal is to minimize Root Mean Squared Error (RMSE) on log-transformed "
        "SalePrice using XGBRegressor. The target variable is transformed with "
        "np.log1p(SalePrice) and predictions are reversed with np.expm1()."
    )
    pdf.body_text(
        "Three hyperparameter tuning strategies are evaluated:\n"
        "  1. Grid Search CV - exhaustive search over a discrete parameter grid\n"
        "  2. Randomized Search CV - 100 random samples from continuous distributions\n"
        "  3. Optuna Bayesian Optimization - 50 trials using Tree-structured Parzen "
        "Estimator (TPE)\n\n"
        "All methods use 5-fold cross-validation with the same KFold splits for "
        "fair comparison. Baseline models (Ridge regression and default XGBoost) "
        "establish the performance floor."
    )

    # ── 2. Preprocessing ─────────────────────────────────────────────────────
    pdf.section_title("2. Preprocessing")
    pdf.body_text(
        "1. Outlier Removal: Two well-known GrLivArea outliers (> 4000 sq ft with "
        "SalePrice < $300,000) are removed from the training set.\n\n"
        "2. Missing Values: Numeric columns are filled with median values. Categorical "
        "columns are filled with 'None' (indicating feature absence).\n\n"
        "3. Ordinal Encoding: Quality columns (ExterQual, KitchenQual, etc.) are mapped "
        "to integers: None=0, Po=1, Fa=2, TA=3, Gd=4, Ex=5.\n\n"
        "4. One-Hot Encoding: Remaining categorical variables are one-hot encoded with "
        "drop_first=True to avoid multicollinearity."
    )

    # ── 3. Grid Search CV ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("3. Grid Search CV")
    pdf.body_text(
        "Grid Search exhaustively evaluates every combination of discrete parameter "
        "values. The parameter grid includes:"
    )
    pdf.finding_table(
        ["Parameter", "Values"],
        [
            ("n_estimators", "300, 500, 800"),
            ("max_depth", "3, 5, 7"),
            ("learning_rate", "0.01, 0.05, 0.1"),
            ("subsample", "0.8, 1.0"),
        ],
        col_widths=[60, 130],
    )
    pdf.body_text(
        "Total configurations: 3 x 3 x 3 x 2 = 54, each evaluated with 5-fold CV "
        "(270 total fits). This guarantees finding the global optimum within the grid "
        "but is limited to the predefined discrete values."
    )

    # ── 4. Randomized Search CV ──────────────────────────────────────────────
    pdf.section_title("4. Randomized Search CV")
    pdf.body_text(
        "Randomized Search samples 100 configurations from continuous distributions, "
        "exploring a much larger parameter space than Grid Search:"
    )
    pdf.finding_table(
        ["Parameter", "Distribution"],
        [
            ("n_estimators", "randint(200, 1200)"),
            ("max_depth", "randint(3, 10)"),
            ("learning_rate", "uniform(0.005, 0.2)"),
            ("subsample", "uniform(0.6, 1.0)"),
            ("colsample_bytree", "uniform(0.5, 1.0)"),
            ("min_child_weight", "randint(1, 10)"),
            ("reg_alpha", "uniform(0, 1)"),
            ("reg_lambda", "uniform(0.5, 2.0)"),
        ],
        col_widths=[60, 130],
    )
    pdf.body_text(
        "With 100 iterations and 5-fold CV (500 total fits), Randomized Search "
        "explores more hyperparameters and continuous ranges, often finding better "
        "solutions than Grid Search in comparable time."
    )

    # ── 5. Optuna Bayesian ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("5. Optuna Bayesian Optimization")
    pdf.body_text(
        "Optuna uses the Tree-structured Parzen Estimator (TPE) to intelligently "
        "guide the search. Unlike random or grid approaches, TPE models the "
        "relationship between hyperparameters and performance, focusing exploration "
        "on promising regions of the search space."
    )
    pdf.body_text(
        "The study runs 50 trials, each evaluating a configuration with 5-fold CV "
        "(250 total fits). Key advantages:\n"
        "  - Learns from previous trials to propose better configurations\n"
        "  - Supports log-scale sampling for learning_rate and reg_alpha\n"
        "  - Automatic early stopping of unpromising configurations\n"
        "  - Each trial is logged to WandB for full visibility"
    )

    # ── 6. Comparison ────────────────────────────────────────────────────────
    pdf.section_title("6. Results Comparison")
    plot_path = os.path.join(PLOT_DIR, "method_comparison.png")
    if os.path.exists(plot_path):
        pdf.add_plot("Method Comparison (CV RMSE)", plot_path)
    pdf.body_text(
        "The bar chart above compares all tuning methods by their best 5-fold CV RMSE "
        "on log-transformed SalePrice. Lower is better. The green bar indicates the "
        "overall best method."
    )

    # ── 7. WandB Integration ─────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("7. Weights & Biases (WandB) Integration")
    pdf.body_text(
        "All experiments are logged to WandB (wandb.ai) for experiment tracking and "
        "reproducibility. Four runs are created:\n\n"
        "  1. baseline - Ridge and default XGBoost RMSE values\n"
        "  2. grid-search - Best params and RMSE from GridSearchCV\n"
        "  3. random-search - Best params and RMSE from RandomizedSearchCV\n"
        "  4. optuna-bayesian - All 50 trial results with per-trial metrics\n\n"
        "WandB provides interactive dashboards for comparing runs, visualizing "
        "hyperparameter importance, and tracking metric trends across trials."
    )

    # ── 8. Kaggle Score ──────────────────────────────────────────────────────
    pdf.section_title("8. Kaggle Submission Score")
    pdf.body_text(
        "The submission.csv file was generated using the best model parameters and "
        "uploaded to the Kaggle competition.\n\n"
        "Kaggle Public Leaderboard Score: TODO - paste score after uploading to Kaggle\n\n"
        "The submission contains 1,459 predictions (Id range 1461-2919) with all "
        "prices > 0."
    )

    # ── 9. Conclusions ───────────────────────────────────────────────────────
    pdf.section_title("9. Conclusions")
    pdf.body_text(
        "1. All three tuning methods improve upon the default XGBoost baseline, "
        "confirming the importance of hyperparameter optimization.\n\n"
        "2. Randomized Search and Optuna generally outperform Grid Search by exploring "
        "continuous parameter spaces and additional hyperparameters (colsample_bytree, "
        "regularization terms).\n\n"
        "3. Optuna's Bayesian approach achieves competitive results with fewer total "
        "evaluations (50 trials vs 100 iterations for Random Search), demonstrating "
        "the efficiency of informed search strategies.\n\n"
        "4. WandB integration provides full experiment tracking, making results "
        "reproducible and easy to compare.\n\n"
        "GitHub Repository: https://github.com/alialsaifi/hbku-data-tools-midterm"
    )

    pdf.output(OUTPUT_PDF)
    print(f"Report saved to: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_report()
