# MarketPulse – Food Price & Seasonal Trend Explorer

MarketPulse is a beginner-friendly Streamlit application for exploring relationships between variables, category percentages, market/commodity comparisons and time-based patterns in food-price datasets. It supports both a built-in sample and user-uploaded CSV files.

## Features

- Built-in food/vegetable market price dataset and custom CSV upload.
- Automatic numeric, categorical and date-column detection.
- Dataset dimensions, preview, data types, missing values and duplicates in the profile.
- Bivariate scatterplots with fitted trends and Pearson correlation.
- Correlation heatmaps and optional resistant (robust) regression lines.
- Third-variable exploration with category-colored scatterplots and grouped summaries.
- Percentage tables and two-/three-variable contingency tables.
- Interactive date selection and time-series charts with optional category comparisons.
- Daily, weekly and monthly resampling with mean, median, sum, min, max or count.
- CSV export for selected columns and resampled results.
- Simple-English “What does this mean?” explanations.

## EDA syllabus coverage

| Unit | Topics covered |
|---|---|
| Unit 4 | Relationships between variables, bivariate exploration, scatterplots, correlation, resistant trend lines, percentages, contingency tables and comparisons across batches/groups |
| Unit 5 | Multivariate exploration, third-variable comparisons, three-way contingency tables, causal interpretation cautions, time-series fundamentals, date indexing, trends, grouping and resampling |

## Technology

Python, Streamlit, Pandas, NumPy, Matplotlib and Seaborn. No React, Node.js or external database is required.

## Project structure

```text
MarketPulse/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_market_prices.csv
├── modules/
│   ├── __init__.py
│   └── analysis.py
└── tests/
    └── test_analysis.py
```

## Installation

1. Install Python 3.10 or newer.
2. Extract `MarketPulse.zip`.
3. Open the `MarketPulse` folder in VS Code.
4. Create a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the application

From the project root:

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Upload your own dataset

1. Open **Dataset Upload** from the sidebar.
2. Choose a `.csv` file. UTF-8 encoding and a header row are recommended.
3. Open **Dataset Overview** to inspect detected field types.
4. Use the relationship and percentage pages for suitable numeric/category columns.
5. Use **Time-Series Analysis** or **Resampling** when a date column and numeric measure are available.

MarketPulse does not require specific food-price column names. It detects columns and asks you to select the fields. If a page cannot run because a dataset lacks required column types, it displays a clear explanation.

## GitHub instructions

Create an empty GitHub repository, then run these commands from the project directory:

```bash
git init
git add .
git commit -m "Add MarketPulse EDA application"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/MarketPulse.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Avoid committing private or confidential datasets.

## Deploy on Streamlit Community Cloud

1. Push this project to GitHub.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **Create app** and choose the repository and branch.
4. Set the main file path to `app.py`.
5. Deploy. Streamlit installs the packages listed in `requirements.txt`.
6. Keep `data/sample_market_prices.csv` in the repository for the built-in sample option.

## Testing

Run the included unit tests from the project root:

```bash
python -m unittest discover -s tests -v
```

The tests cover automatic column detection, date parsing, percentage tables, contingency tables, resampling and basic data profiling. Browser-driven interaction tests require a running browser.

## Interpretation notes

- Correlation and group comparisons describe association, not causation.
- A time-series pattern does not establish why a value changed.
- Date detection is heuristic. Review the detected date field, especially for ambiguous date formats.
- Robust trend lines reduce sensitivity to extreme observations; they do not automatically identify errors.
- Resampling aggregates observations into larger time intervals and may hide short-lived changes.
- This is an educational EDA tool, not an official market-price source or financial advice.
