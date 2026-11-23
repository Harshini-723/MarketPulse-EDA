
import os
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MarketPulse | Food Price Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_PATH = DATA_DIR / "sample_market_prices.csv"

sns.set_theme(style="whitegrid", palette="crest")


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f8fbfb, #edf4f3);
}

section[data-testid="stSidebar"] {
    background: #102f38;
}

section[data-testid="stSidebar"] * {
    color: white;
}

section[data-testid="stSidebar"] hr {
    border-color: #47616a;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.market-hero {
    background: linear-gradient(115deg, #102f38, #147765);
    padding: 45px;
    border-radius: 25px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 12px 35px rgba(16,47,56,0.12);
}

.market-hero .eyebrow {
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 700;
    color: #a8e6d7;
    margin-bottom: 18px;
}

.market-hero h1 {
    font-family: 'Manrope', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: white;
}

.market-hero p {
    font-size: 16px;
    line-height: 1.8;
    max-width: 750px;
    color: #e0f0ed;
}

.metric-card {
    background: white;
    border: 1px solid #e1ebea;
    border-radius: 18px;
    padding: 22px;
    min-height: 125px;
    box-shadow: 0 5px 18px rgba(16,47,56,0.04);
}

.metric-label {
    color: #70858c;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

.metric-value {
    color: #125c51;
    font-size: 29px;
    font-weight: 800;
    margin-top: 12px;
}

.metric-description {
    color: #82949a;
    font-size: 12px;
    margin-top: 5px;
}

.feature-card {
    background: white;
    border: 1px solid #e1ebea;
    border-radius: 18px;
    padding: 22px;
    min-height: 155px;
    box-shadow: 0 5px 18px rgba(16,47,56,0.04);
    margin-bottom: 15px;
}

.feature-label {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #71848b;
}

.feature-number {
    font-size: 29px;
    font-weight: 800;
    color: #126354;
    margin: 10px 0;
}

.feature-description {
    font-size: 13px;
    color: #82949a;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: #173b44;
}

.stButton > button,
.stDownloadButton > button {
    background: #126354;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #0d4b40;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SAMPLE DATA GENERATION
# =========================================================

def generate_sample_dataset():

    rng = np.random.default_rng(42)

    commodities = {
        "Rice": 55,
        "Wheat": 35,
        "Tomato": 30,
        "Onion": 40,
        "Potato": 28,
        "Sugar": 45
    }

    markets = [
        "Chennai",
        "Madurai",
        "Coimbatore",
        "Trichy"
    ]

    dates = pd.date_range(
        start="2022-01-01",
        end="2025-12-01",
        freq="MS"
    )

    rows = []

    for commodity, base_price in commodities.items():

        for market in markets:

            market_factor = rng.uniform(0.90, 1.15)

            for date in dates:

                month = date.month

                seasonal_factor = (
                    1 + 0.12 * np.sin(
                        2 * np.pi * month / 12
                    )
                )

                yearly_factor = (
                    1 + 0.035 * (date.year - 2022)
                )

                noise = rng.normal(1, 0.07)

                price = (
                    base_price
                    * market_factor
                    * seasonal_factor
                    * yearly_factor
                    * noise
                )

                demand = rng.integers(500, 2000)

                supply = rng.integers(450, 2100)

                inflation = round(
                    rng.uniform(3, 8), 2
                )

                if month in [3, 4, 5]:
                    season = "Summer"
                elif month in [6, 7, 8, 9]:
                    season = "Monsoon"
                elif month in [10, 11]:
                    season = "Post-Monsoon"
                else:
                    season = "Winter"

                rows.append({
                    "Date": date,
                    "Commodity": commodity,
                    "Market": market,
                    "Price": round(max(price, 1), 2),
                    "Demand": demand,
                    "Supply": supply,
                    "Inflation": inflation,
                    "Season": season
                })

    return pd.DataFrame(rows)


def load_sample_dataset():

    try:

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        if SAMPLE_PATH.exists():

            sample = pd.read_csv(
                SAMPLE_PATH
            )

            if sample.empty:
                raise ValueError("Sample CSV is empty.")

            return sample

        sample = generate_sample_dataset()

        sample.to_csv(
            SAMPLE_PATH,
            index=False
        )

        return sample

    except Exception as e:

        st.error(
            f"Sample dataset loading failed: {e}"
        )

        return None


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "data": None,
    "dataset_name": None,
    "resampled_data": None,
    "cleaned_data": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_data():

    if st.session_state.data is None:

        st.warning(
            "Please upload a dataset or load the sample dataset first."
        )

        return None

    if st.session_state.data.empty:

        st.error("The active dataset is empty.")

        return None

    return st.session_state.data.copy()


def get_column_types(df):

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    date_columns = []

    for col in df.columns:

        if col in numeric_columns:
            continue

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_columns.append(col)
            continue

        # Avoid interpreting ordinary text labels as dates.
        if not any(word in str(col).lower() for word in
                   ["date", "time", "month", "year"]):
            continue

        converted = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        if len(df) and converted.notna().mean() >= 0.7:
            date_columns.append(col)

    categorical_columns = [
        col for col in df.columns
        if col not in numeric_columns
        and col not in date_columns
    ]

    return (
        numeric_columns,
        categorical_columns,
        date_columns
    )


def show_metric(label, value, description=""):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def create_chart():

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    ax.grid(
        axis="y",
        alpha=0.2
    )

    return fig, ax


def display_chart(fig):

    fig.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


def download_csv(df, filename):

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def prepare_numeric(df, column):

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <h2 style="color:white;">📈 MarketPulse</h2>
    <p style="color:#9bb3b9;">
        Food Price & Seasonal Trend Explorer
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Dataset Upload",
            "Dataset Overview",
            "Variable Comparison",
            "Relationship Analysis",
            "Multivariate Analysis",
            "Percentage Analysis",
            "Contingency Analysis",
            "Time-Series Analysis",
            "Resampling",
            "Export"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### ACTIVE DATASET")

    if st.session_state.data is not None:

        st.success(
            st.session_state.dataset_name
        )

        st.caption(
            f"{len(st.session_state.data):,} rows | "
            f"{len(st.session_state.data.columns)} columns"
        )

    else:

        st.caption("No dataset selected")

    st.markdown("---")

    st.caption(
        "MarketPulse | Analytics Dashboard"
    )


# =========================================================
# HOME
# =========================================================

if page == "Home":

    st.markdown("""
    <div class="market-hero">

        <div class="eyebrow">
            FOOD PRICE ANALYTICS & MARKET INSIGHTS
        </div>

        <h1>
            MarketPulse<br>
            Food Price Analysis Dashboard
        </h1>

        <p>
            Analyze food prices, compare commodities,
            explore market relationships and visualize
            seasonal trends using interactive data analytics.
            Upload your own CSV or begin with the included
            sample food-price dataset.
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Your EDA Workspace")

    col1, col2, col3 = st.columns(3)

    features = [
        (
            "RELATIONSHIPS",
            "01",
            "Explore pairs of numeric variables and analyze correlations."
        ),
        (
            "MULTIPLE VARIABLES",
            "02",
            "Compare categories and analyze multiple variables together."
        ),
        (
            "TIME & SEASONALITY",
            "03",
            "Track food prices and resample time-series data."
        )
    ]

    for container, feature in zip(
        [col1, col2, col3],
        features
    ):

        with container:

            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-label">{feature[0]}</div>
                <div class="feature-number">{feature[1]}</div>
                <div class="feature-description">
                    {feature[2]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## Dashboard Capabilities")

    capabilities = [
        ("📂", "Dataset Management",
         "Upload CSV files and inspect dataset structure."),

        ("📊", "Statistical Analysis",
         "Calculate descriptive statistics and distributions."),

        ("🔗", "Relationship Analysis",
         "Explore correlations between numeric variables."),

        ("🧮", "Multivariate Analysis",
         "Compare numerical data across categories."),

        ("📅", "Time-Series Analysis",
         "Analyze changes in food prices over time."),

        ("⬇", "Export Results",
         "Download processed datasets and results.")
    ]

    cols = st.columns(3)

    for i, (icon, title, description) in enumerate(capabilities):

        with cols[i % 3]:

            st.markdown(f"""
            <div class="feature-card">
                <h3>{icon} {title}</h3>
                <p class="feature-description">
                    {description}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button(
        "📈 Load Sample Dataset",
        type="primary"
    ):

        sample = load_sample_dataset()

        if sample is not None:

            st.session_state.data = sample
            st.session_state.dataset_name = "Sample Market Prices"
            st.session_state.resampled_data = None

            st.success(
                f"Successfully loaded {len(sample):,} records!"
            )

            st.rerun()


# =========================================================
# DATASET UPLOAD
# =========================================================

elif page == "Dataset Upload":

    st.title("📂 Dataset Upload")

    st.write(
        "Upload your food price dataset in CSV format."
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            uploaded_df = pd.read_csv(
                uploaded_file
            )

            if uploaded_df.empty:
                st.error("The uploaded CSV has no data rows.")

            elif len(uploaded_df.columns) == 0:
                st.error("No columns found in the CSV.")

            else:

                st.session_state.data = uploaded_df
                st.session_state.dataset_name = uploaded_file.name
                st.session_state.resampled_data = None
                st.session_state.cleaned_data = None

                st.success(
                    "Dataset uploaded successfully!"
                )

                st.markdown("## Dataset Preview")

                st.dataframe(
                    uploaded_df.head(10),
                    use_container_width=True
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    show_metric(
                        "Total Rows",
                        f"{len(uploaded_df):,}"
                    )

                with c2:
                    show_metric(
                        "Total Columns",
                        f"{len(uploaded_df.columns):,}"
                    )

                with c3:
                    show_metric(
                        "Missing Values",
                        f"{uploaded_df.isna().sum().sum():,}"
                    )

        except Exception as e:

            st.error(
                f"Unable to read CSV: {e}"
            )

    st.markdown("---")

    st.markdown("### Load Included Sample Dataset")

    if st.button("Load Sample Market Dataset"):

        sample = load_sample_dataset()

        if sample is not None:

            st.session_state.data = sample
            st.session_state.dataset_name = "Sample Market Prices"
            st.session_state.resampled_data = None

            st.success("Sample dataset loaded!")

            st.rerun()


# =========================================================
# DATASET OVERVIEW
# =========================================================

elif page == "Dataset Overview":

    st.title("📊 Dataset Overview")

    df = get_data()

    if df is not None:

        numeric_cols, categorical_cols, date_cols = get_column_types(df)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            show_metric("Total Rows", f"{len(df):,}")

        with c2:
            show_metric("Total Columns", f"{len(df.columns):,}")

        with c3:
            show_metric("Numeric Columns", len(numeric_cols))

        with c4:
            show_metric(
                "Missing Values",
                f"{df.isna().sum().sum():,}"
            )

        st.markdown("## Dataset Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        st.markdown("## Column Information")

        column_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isna().sum().values,
            "Unique Values": df.nunique().values
        })

        st.dataframe(
            column_info,
            use_container_width=True
        )

        st.markdown("## Missing Value Analysis")

        missing = df.isna().sum()
        missing = missing[missing > 0]

        if not missing.empty:

            missing_df = pd.DataFrame({
                "Column": missing.index,
                "Missing Count": missing.values,
                "Missing Percentage": (
                    missing.values / len(df) * 100
                ).round(2)
            })

            st.dataframe(
                missing_df,
                use_container_width=True
            )

            fig, ax = create_chart()

            missing.plot(
                kind="bar",
                ax=ax
            )

            ax.set_title("Missing Values by Column")
            ax.set_ylabel("Missing Count")
            ax.set_xlabel("Column")

            plt.xticks(rotation=45)

            display_chart(fig)

        else:

            st.success("No missing values found.")

        st.markdown("## Numerical Summary")

        if numeric_cols:

            st.dataframe(
                df[numeric_cols].describe().T,
                use_container_width=True
            )

        else:

            st.info("No numerical columns found.")


# =========================================================
# VARIABLE COMPARISON
# =========================================================

elif page == "Variable Comparison":

    st.title("📉 Variable Comparison")

    df = get_data()

    if df is not None:

        numeric_cols, _, _ = get_column_types(df)

        if not numeric_cols:

            st.warning("No numeric columns available.")

        else:

            selected_column = st.selectbox(
                "Select Numeric Variable",
                numeric_cols
            )

            chart_type = st.selectbox(
                "Select Chart Type",
                [
                    "Histogram",
                    "Box Plot",
                    "Density Plot",
                    "Violin Plot"
                ]
            )

            values = prepare_numeric(
                df,
                selected_column
            ).dropna()

            if values.empty:

                st.warning("No valid numeric values found.")

            else:

                fig, ax = create_chart()

                if chart_type == "Histogram":

                    sns.histplot(
                        values,
                        kde=True,
                        ax=ax
                    )

                elif chart_type == "Box Plot":

                    sns.boxplot(
                        x=values,
                        ax=ax
                    )

                elif chart_type == "Density Plot":

                    if values.nunique() > 1:
                        sns.kdeplot(
                            values,
                            fill=True,
                            ax=ax
                        )
                    else:
                        ax.hist(values)

                elif chart_type == "Violin Plot":

                    sns.violinplot(
                        x=values,
                        ax=ax
                    )

                ax.set_title(
                    f"{chart_type} of {selected_column}"
                )

                display_chart(fig)

                st.markdown("## Statistical Summary")

                st.dataframe(
                    values.describe().to_frame("Value"),
                    use_container_width=True
                )


# =========================================================
# RELATIONSHIP ANALYSIS
# =========================================================

elif page == "Relationship Analysis":

    st.title("🔗 Relationship Analysis")

    df = get_data()

    if df is not None:

        numeric_cols, _, _ = get_column_types(df)

        if len(numeric_cols) < 2:

            st.warning(
                "At least two numeric columns are required."
            )

        else:

            c1, c2 = st.columns(2)

            with c1:

                x_col = st.selectbox(
                    "Select X Variable",
                    numeric_cols
                )

            with c2:

                y_col = st.selectbox(
                    "Select Y Variable",
                    [
                        col for col in numeric_cols
                        if col != x_col
                    ]
                )

            plot_df = df[[x_col, y_col]].copy()

            plot_df[x_col] = prepare_numeric(
                plot_df, x_col
            )

            plot_df[y_col] = prepare_numeric(
                plot_df, y_col
            )

            plot_df = plot_df.dropna()

            fig, ax = create_chart()

            if not plot_df.empty:

                sns.scatterplot(
                    data=plot_df,
                    x=x_col,
                    y=y_col,
                    ax=ax
                )

                ax.set_title(
                    f"{x_col} vs {y_col}"
                )

                display_chart(fig)

                correlation = plot_df[x_col].corr(
                    plot_df[y_col]
                )

                st.metric(
                    "Pearson Correlation",
                    f"{correlation:.4f}"
                    if pd.notna(correlation)
                    else "N/A"
                )

            else:

                plt.close(fig)
                st.warning("No valid pairs available.")

            st.markdown("## Correlation Matrix")

            corr_df = df[numeric_cols].apply(
                pd.to_numeric,
                errors="coerce"
            )

            corr = corr_df.corr()

            fig, ax = plt.subplots(
                figsize=(10, 6)
            )

            sns.heatmap(
                corr,
                annot=True,
                cmap="YlGnBu",
                fmt=".2f",
                ax=ax
            )

            ax.set_title("Correlation Heatmap")

            display_chart(fig)


# =========================================================
# MULTIVARIATE ANALYSIS
# =========================================================

elif page == "Multivariate Analysis":

    st.title("🧮 Multivariate Analysis")

    df = get_data()

    if df is not None:

        numeric_cols, categorical_cols, _ = get_column_types(df)

        if not numeric_cols:

            st.warning("Numeric columns are required.")

        else:

            selected_numeric = st.multiselect(
                "Select Numeric Variables",
                numeric_cols,
                default=numeric_cols[:min(3, len(numeric_cols))]
            )

            if selected_numeric:

                st.markdown("## Pair Plot")

                if len(selected_numeric) >= 2:

                    pair_df = df[selected_numeric].apply(
                        pd.to_numeric,
                        errors="coerce"
                    ).dropna()

                    if len(pair_df) > 500:
                        pair_df = pair_df.sample(
                            500,
                            random_state=42
                        )

                    if len(pair_df) >= 2:

                        fig = sns.pairplot(
                            pair_df,
                            diag_kind="hist"
                        )

                        fig.fig.tight_layout()

                        st.pyplot(
                            fig.fig,
                            use_container_width=True
                        )

                        plt.close(fig.fig)

                    else:

                        st.info("Not enough valid rows for a pair plot.")

                else:

                    st.info(
                        "Select at least two variables for a pair plot."
                    )

                st.markdown("## Multivariable Correlation")

                corr = df[selected_numeric].apply(
                    pd.to_numeric,
                    errors="coerce"
                ).corr()

                fig, ax = plt.subplots(
                    figsize=(9, 5)
                )

                sns.heatmap(
                    corr,
                    annot=True,
                    cmap="crest",
                    fmt=".2f",
                    ax=ax
                )

                display_chart(fig)

            if categorical_cols and numeric_cols:

                st.markdown("## Category-wise Comparison")

                category_col = st.selectbox(
                    "Select Category",
                    categorical_cols
                )

                value_col = st.selectbox(
                    "Select Numeric Variable",
                    numeric_cols,
                    key="multivariate_value"
                )

                temp = df[
                    [category_col, value_col]
                ].copy()

                temp[value_col] = pd.to_numeric(
                    temp[value_col],
                    errors="coerce"
                )

                grouped = (
                    temp.groupby(
                        category_col,
                        dropna=False,
                        observed=True
                    )[value_col]
                    .mean()
                    .sort_values(ascending=False)
                    .head(20)
                )

                st.dataframe(
                    grouped.to_frame("Average"),
                    use_container_width=True
                )

                fig, ax = create_chart()

                grouped.plot(
                    kind="bar",
                    ax=ax
                )

                ax.set_title(
                    f"Average {value_col} by {category_col}"
                )

                ax.set_ylabel(value_col)

                plt.xticks(rotation=45)

                display_chart(fig)


# =========================================================
# PERCENTAGE ANALYSIS
# =========================================================

elif page == "Percentage Analysis":

    st.title("📊 Percentage Analysis")

    df = get_data()

    if df is not None:

        _, categorical_cols, _ = get_column_types(df)

        if not categorical_cols:

            st.warning("No categorical columns found.")

        else:

            selected_column = st.selectbox(
                "Select Categorical Column",
                categorical_cols
            )

            counts = df[selected_column].fillna(
                "(Missing)"
            ).value_counts()

            percentages = (
                counts / counts.sum() * 100
            ).round(2)

            result = pd.DataFrame({
                "Category": counts.index.astype(str),
                "Count": counts.values,
                "Percentage": percentages.values
            })

            st.markdown("## Percentage Distribution")

            st.dataframe(
                result,
                use_container_width=True
            )

            fig, ax = plt.subplots(
                figsize=(8, 6)
            )

            pie_counts = counts.head(15)

            if len(counts) > 15:
                pie_counts.loc["Other"] = counts.iloc[15:].sum()

            pie_counts.plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax
            )

            ax.set_ylabel("")

            ax.set_title(
                f"Percentage Distribution of {selected_column}"
            )

            display_chart(fig)

            download_csv(
                result,
                "percentage_analysis.csv"
            )


# =========================================================
# CONTINGENCY ANALYSIS
# =========================================================

elif page == "Contingency Analysis":

    st.title("📋 Contingency Analysis")

    df = get_data()

    if df is not None:

        _, categorical_cols, _ = get_column_types(df)

        if len(categorical_cols) < 2:

            st.warning(
                "At least two categorical columns are required."
            )

        else:

            c1, c2 = st.columns(2)

            with c1:

                row_col = st.selectbox(
                    "Select Row Variable",
                    categorical_cols
                )

            with c2:

                column_col = st.selectbox(
                    "Select Column Variable",
                    [
                        col for col in categorical_cols
                        if col != row_col
                    ]
                )

            table_type = st.selectbox(
                "Select Table Type",
                [
                    "Counts",
                    "Row Percentage",
                    "Column Percentage"
                ]
            )

            cross_tab = pd.crosstab(
                df[row_col].fillna("(Missing)"),
                df[column_col].fillna("(Missing)")
            )

            if table_type == "Row Percentage":

                result = cross_tab.div(
                    cross_tab.sum(axis=1).replace(0, np.nan),
                    axis=0
                ) * 100

            elif table_type == "Column Percentage":

                result = cross_tab.div(
                    cross_tab.sum(axis=0).replace(0, np.nan),
                    axis=1
                ) * 100

            else:

                result = cross_tab

            st.markdown("## Contingency Table")

            st.dataframe(
                result.round(2),
                use_container_width=True
            )

            fig, ax = plt.subplots(
                figsize=(10, 6)
            )

            sns.heatmap(
                result,
                annot=True,
                fmt=".1f" if table_type != "Counts" else ".0f",
                cmap="YlGnBu",
                ax=ax
            )

            ax.set_title(
                f"{row_col} vs {column_col}"
            )

            display_chart(fig)

            download_csv(
                result.reset_index(),
                "contingency_analysis.csv"
            )


# =========================================================
# TIME-SERIES ANALYSIS
# =========================================================

elif page == "Time-Series Analysis":

    st.title("📅 Time-Series Analysis")

    df = get_data()

    if df is not None:

        numeric_cols, _, date_cols = get_column_types(df)

        if not date_cols:

            st.warning(
                "No date column detected. Upload a dataset containing dates."
            )

        elif not numeric_cols:

            st.warning("No numeric columns available.")

        else:

            c1, c2 = st.columns(2)

            with c1:

                date_col = st.selectbox(
                    "Select Date Column",
                    date_cols
                )

            with c2:

                value_col = st.selectbox(
                    "Select Numeric Variable",
                    numeric_cols
                )

            plot_df = df.copy()

            plot_df[date_col] = pd.to_datetime(
                plot_df[date_col],
                errors="coerce"
            )

            plot_df[value_col] = pd.to_numeric(
                plot_df[value_col],
                errors="coerce"
            )

            plot_df = plot_df.dropna(
                subset=[date_col, value_col]
            )

            plot_df = plot_df.sort_values(date_col)

            if plot_df.empty:

                st.warning(
                    "No valid date and numeric values available."
                )

            else:

                st.markdown("## Time-Series Trend")

                # Aggregate duplicate dates for a clearer trend.
                trend = (
                    plot_df.groupby(date_col)[value_col]
                    .mean()
                    .reset_index()
                )

                fig, ax = create_chart()

                sns.lineplot(
                    data=trend,
                    x=date_col,
                    y=value_col,
                    marker="o",
                    ax=ax
                )

                ax.set_title(
                    f"{value_col} Over Time"
                )

                ax.set_xlabel("Date")
                ax.set_ylabel(value_col)

                plt.xticks(rotation=45)

                display_chart(fig)

                st.markdown("## Monthly Trend")

                monthly = (
                    plot_df.set_index(date_col)[value_col]
                    .resample("ME")
                    .mean()
                    .dropna()
                )

                if not monthly.empty:

                    fig, ax = create_chart()

                    monthly.plot(
                        ax=ax,
                        marker="o"
                    )

                    ax.set_title(
                        f"Monthly Average {value_col}"
                    )

                    ax.set_xlabel("Month")
                    ax.set_ylabel(value_col)

                    plt.xticks(rotation=45)

                    display_chart(fig)

                    monthly_df = monthly.reset_index()

                    monthly_df.columns = [
                        "Month",
                        "Average"
                    ]

                    st.dataframe(
                        monthly_df,
                        use_container_width=True
                    )

                    download_csv(
                        monthly_df,
                        "monthly_trend.csv"
                    )

                st.markdown("## Date Range")

                st.write(
                    f"Start Date: {plot_df[date_col].min().date()}"
                )

                st.write(
                    f"End Date: {plot_df[date_col].max().date()}"
                )


# =========================================================
# RESAMPLING
# =========================================================

elif page == "Resampling":

    st.title("🔄 Time-Series Resampling")

    df = get_data()

    if df is not None:

        numeric_cols, categorical_cols, date_cols = get_column_types(df)

        if not date_cols:

            st.warning("A date column is required.")

        elif not numeric_cols:

            st.warning("A numeric column is required.")

        else:

            c1, c2 = st.columns(2)

            with c1:

                date_col = st.selectbox(
                    "Select Date Column",
                    date_cols,
                    key="resample_date"
                )

            with c2:

                value_col = st.selectbox(
                    "Select Numeric Column",
                    numeric_cols,
                    key="resample_value"
                )

            frequency = st.selectbox(
                "Select Resampling Frequency",
                [
                    "Daily",
                    "Weekly",
                    "Monthly",
                    "Quarterly",
                    "Yearly"
                ]
            )

            aggregation = st.selectbox(
                "Select Aggregation",
                [
                    "Mean",
                    "Sum",
                    "Minimum",
                    "Maximum",
                    "Count"
                ]
            )

            group_col = st.selectbox(
                "Group By (Optional)",
                ["None"] + categorical_cols
            )

            if st.button(
                "Generate Resampled Data",
                type="primary"
            ):

                try:

                    working_df = df.copy()

                    working_df[date_col] = pd.to_datetime(
                        working_df[date_col],
                        errors="coerce"
                    )

                    working_df[value_col] = pd.to_numeric(
                        working_df[value_col],
                        errors="coerce"
                    )

                    working_df = working_df.dropna(
                        subset=[date_col, value_col]
                    )

                    if working_df.empty:

                        st.error(
                            "No valid records available."
                        )

                    else:

                        frequency_map = {
                            "Daily": "D",
                            "Weekly": "W",
                            "Monthly": "ME",
                            "Quarterly": "QE",
                            "Yearly": "YE"
                        }

                        aggregation_map = {
                            "Mean": "mean",
                            "Sum": "sum",
                            "Minimum": "min",
                            "Maximum": "max",
                            "Count": "count"
                        }

                        freq = frequency_map[frequency]
                        agg = aggregation_map[aggregation]

                        if group_col == "None":

                            resampled = (
                                working_df
                                .set_index(date_col)[value_col]
                                .resample(freq)
                                .agg(agg)
                                .dropna()
                                .reset_index()
                            )

                            resampled.columns = [
                                "Period",
                                "Value"
                            ]

                        else:

                            resampled = (
                                working_df
                                .set_index(date_col)
                                .groupby(
                                    group_col,
                                    observed=True
                                )[value_col]
                                .resample(freq)
                                .agg(agg)
                                .dropna()
                                .reset_index()
                            )

                            resampled.columns = [
                                "Category",
                                "Period",
                                "Value"
                            ]

                        st.session_state.resampled_data = resampled

                        st.success(
                            "Resampling completed successfully!"
                        )

                except Exception as e:

                    st.error(
                        f"Resampling failed: {e}"
                    )

            resampled = st.session_state.resampled_data

            if resampled is not None:

                st.markdown("## Resampled Dataset")

                st.dataframe(
                    resampled,
                    use_container_width=True
                )

                st.markdown("## Resampled Trend")

                fig, ax = create_chart()

                if "Category" in resampled.columns:

                    for category, group in resampled.groupby("Category"):

                        ax.plot(
                            group["Period"],
                            group["Value"],
                            marker="o",
                            label=str(category)
                        )

                    ax.legend(
                        bbox_to_anchor=(1.02, 1),
                        loc="upper left"
                    )

                else:

                    ax.plot(
                        resampled["Period"],
                        resampled["Value"],
                        marker="o"
                    )

                ax.set_title(
                    f"{frequency} {aggregation} of {value_col}"
                )

                ax.set_xlabel("Period")
                ax.set_ylabel(value_col)

                plt.xticks(rotation=45)

                display_chart(fig)

                download_csv(
                    resampled,
                    "resampled_data.csv"
                )


# =========================================================
# EXPORT
# =========================================================

elif page == "Export":

    st.title("⬇ Export Data")

    df = get_data()

    if df is not None:

        st.markdown("## Original Dataset")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        download_csv(
            df,
            "marketpulse_dataset.csv"
        )

        st.markdown("---")

        st.markdown("## Cleaned Dataset")

        if st.button("Prepare Cleaned Dataset"):

            cleaned_df = df.copy()

            cleaned_df = cleaned_df.drop_duplicates()

            numeric_columns = cleaned_df.select_dtypes(
                include=np.number
            ).columns

            for col in numeric_columns:

                median = cleaned_df[col].median()

                if pd.notna(median):

                    cleaned_df[col] = cleaned_df[col].fillna(
                        median
                    )

            categorical_columns = cleaned_df.select_dtypes(
                include=["object", "category"]
            ).columns

            for col in categorical_columns:

                mode = cleaned_df[col].mode()

                if not mode.empty:

                    cleaned_df[col] = cleaned_df[col].fillna(
                        mode.iloc[0]
                    )

            st.session_state.cleaned_data = cleaned_df

            st.success(
                "Cleaned dataset prepared successfully!"
            )

        if st.session_state.cleaned_data is not None:

            st.dataframe(
                st.session_state.cleaned_data.head(10),
                use_container_width=True
            )

            download_csv(
                st.session_state.cleaned_data,
                "marketpulse_cleaned_data.csv"
            )

        st.markdown("---")

        st.markdown("## Dataset Summary Export")

        numeric_cols, _, _ = get_column_types(df)

        if numeric_cols:

            summary = df[numeric_cols].describe().T

            st.dataframe(
                summary,
                use_container_width=True
            )

            download_csv(
                summary.reset_index(),
                "marketpulse_summary.csv"
            )

        else:

            st.info(
                "No numeric columns available for summary export."
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<div style="
    text-align:center;
    color:#82949a;
    font-size:12px;
    padding:15px;
">
    MarketPulse | Food Price & Seasonal Trend Explorer
    <br>
    Interactive Exploratory Data Analysis Dashboard
    <br>
    Built with Python, Streamlit, Pandas, NumPy and Seaborn
</div>
""", unsafe_allow_html=True)
