# HBKU Data Tools and Applications - Midterm Project

Kaggle House Prices: Advanced Regression Techniques

## Structure

```
├── data/                           # Dataset (not committed)
├── part1_eda/                      # Part 1: Exploratory Data Analysis
│   ├── eda_report.py               # EDA analysis + PDF generator
│   ├── generate_report.py          # ROLAP schema PDF generator
│   ├── EDA_Report.pdf
│   ├── ROLAP_Schema_Report.pdf
│   └── plots/
├── part2_hyperparameter_tuning/    # Part 2: Hyperparameter Tuning
│   ├── hyperparameter_tuning.ipynb # Main notebook
│   ├── generate_report.py          # PDF report generator
│   ├── Hyperparameter_Tuning_Report.pdf
│   ├── submission.csv              # Kaggle submission
│   └── plots/
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the dataset from [Kaggle](https://www.kaggle.com/c/house-prices-advanced-regression-techniques) and place CSV files in `data/`.

## Part 2: Hyperparameter Tuning

Three strategies compared on XGBRegressor:
1. Grid Search CV
2. Randomized Search CV (100 iterations)
3. Optuna Bayesian Optimization (50 trials, TPE sampler)

All experiments logged to WandB. Run the notebook:
```bash
cd part2_hyperparameter_tuning
jupyter notebook hyperparameter_tuning.ipynb
```
