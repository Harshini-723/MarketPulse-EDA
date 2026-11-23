
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MarketPulse | Food Price Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

SAMPLE_PATHS = [
    BASE_DIR / "data" / "sample_market_prices.csv",
    BASE_DIR / "dataset" / "sample_market_prices.csv",
    BASE_DIR / "sample_market_prices.csv"
]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f5faf9, #eef5f4);
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #10343c;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Main title */

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #153b40;
}

.sub-title {
    color: #71868b;
    font-size: 16px;
}

/* Active dataset card */

.active-dataset-card {
    background-color: #e8f5ef !important;
    color: #164b3c !important;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #b8dfcc;
    margin-bottom: 12px;
    font-weight: 700;
}

.active-dataset-card,
.active-dataset-card * {
    color: #164b3c !important;
}

/* Sidebar captions */

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #b8d0d3 !important;
}

/* Sidebar warning */

[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: #e8f5ef !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #164b3c !important;
}

/* Footer */

.footer {
    text-align: center;
    color: #84999d;
    padding: 25px;
    font-size: 13px;
}

/* Buttons */

div.stButton > button {
    background-color: #126b5c;
    color: white;
    border-radius: 9px;
    border: none;
    padding: 10px 18px;
}

div.stButton > button:hover {
    background-color: #0d5147;
    color: white;
}

</style>
""", unsafe_allow_html=True)


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
# DATASET FUNCTIONS
# =========================================================

def find_sample_file():

    for path in SAMPLE_PATHS:
        if path.exists() and path.is_file():
            return path

    return None


def load_sample_dataset():

    sample_path = find_sample_file()

    if sample_path is None:
        st.error("Sample dataset file not found.")
        st.info(
            "Expected location: data/sample_market_prices.csv"
        )
        return None

    try:
        df = pd.read_csv(sample_path)

        if df.empty:
            st.error("Sample dataset is empty.")
            return None

        df.columns = df.columns.astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"Sample dataset loading error: {e}")
        return None


def load_uploaded_dataset(uploaded_file):

    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.error("Uploaded dataset is empty.")
            return None

        df.columns = df.columns.astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"CSV loading error: {e}")
        return None


def set_dataset(df, name):

    st.session_state.data = df.copy()
    st.session_state.dataset_name = name

    st.session_state.resampled_data = None
    st.session_state.cleaned_data = None


# =========================================================
# COLUMN DETECTION
# =========================================================

def get_numeric_columns(df):

    result = []

    for col in df.columns:

        values = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        valid_count = values.notna().sum()

        if valid_count >= max(1, int(len(df) * 0.5)):
            result.append(col)

    return result


def get_categorical_columns(df):

    numeric_cols = get_numeric_columns(df)

    return [
        col for col in df.columns
        if col not in numeric_cols
    ]


def get_date_columns(df):

    result = []

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):
            continue

        values = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        if values.notna().sum() >= max(
            1, int(len(df) * 0.7)
        ):
            result.append(col)

    return result


def numeric_series(df, column):

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


# =========================================================
# CHART FUNCTION
# =========================================================

def show_chart(fig):

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 📈 MarketPulse")

    st.caption(
        "Food Price & Seasonal Trend Explorer"
    )

    st.divider()

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

    st.divider()

    st.markdown("### ACTIVE DATASET")

    if st.session_state.data is not None:

        st.markdown(
            f"""
            <div class="active-dataset-card">
                📊 {st.session_state.dataset_name}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            f"Rows: {len(st.session_state.data)}"
        )

        st.caption(
            f"Columns: {len(st.session_state.data.columns)}"
        )

    else:

        st.warning("No dataset loaded")


# =========================================================
# CURRENT DATASET
# =========================================================

df = st.session_state.data


# =========================================================
# HOME
# =========================================================

if page == "Home":

    st.markdown(
        '<div class="main-title">📈 MarketPulse</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Food Price Analytics and Seasonal Trend Explorer'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown("### Welcome to MarketPulse")

    st.write("""
    MarketPulse is an interactive Exploratory Data Analysis
    dashboard designed to study food prices, market variations,
    seasonal patterns, and relationships between variables.
    """)

    col1, col2, col3 = st.columns(3)

    col1.info("📊 Dataset Analysis")
    col2.info("📈 Trend Analysis")
    col3.info("🔍 Statistical Analysis")

    st.divider()

    st.markdown("### Getting Started")

    st.write("1. Open Dataset Upload.")
    st.write("2. Upload a CSV or load the sample dataset.")
    st.write("3. Explore the analysis pages.")
    st.write("4. Export your results.")

    if df is not None:

        st.success(
            f"Active dataset: {st.session_state.dataset_name}"
        )

        st.dataframe(
            df.head(5),
            use_container_width=True
        )


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

        if st.button("Load Uploaded Dataset"):

            uploaded_df = load_uploaded_dataset(
                uploaded_file
            )

            if uploaded_df is not None:

                set_dataset(
                    uploaded_df,
                    uploaded_file.name
                )

                st.success(
                    "Dataset uploaded successfully!"
                )

                st.dataframe(
                    uploaded_df.head(10),
                    use_container_width=True
                )

    st.divider()

    st.markdown("### Load Included Sample Dataset")

    if st.button(
        "Load Sample Market Dataset",
        key="load_sample"
    ):

        sample_df = load_sample_dataset()

        if sample_df is not None:

            set_dataset(
                sample_df,
                "Sample Market Prices"
            )

            st.success(
                "Sample Market Dataset Loaded Successfully!"
            )

            st.write("Dataset Preview")

            st.dataframe(
                sample_df.head(10),
                use_container_width=True
            )

            st.info(
                f"Loaded {len(sample_df)} rows "
                f"and {len(sample_df.columns)} columns."
            )

    st.divider()

    if st.session_state.data is not None:

        st.markdown("### Current Dataset")

        st.write(
            st.session_state.dataset_name
        )

        st.dataframe(
            st.session_state.data.head(5),
            use_container_width=True
        )


# =========================================================
# DATASET OVERVIEW
# =========================================================

elif page == "Dataset Overview":

    st.title("📊 Dataset Overview")

    if df is None:

        st.warning(
            "Please load a dataset from Dataset Upload."
        )

    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Rows", len(df))
        col2.metric("Total Columns", len(df.columns))
        col3.metric(
            "Missing Values",
            int(df.isna().sum().sum())
        )
        col4.metric(
            "Duplicate Rows",
            int(df.duplicated().sum())
        )

        st.divider()

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

        st.subheader("Dataset Information")

        info_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": [
                str(df[col].dtype)
                for col in df.columns
            ],
            "Non-Null Values": [
                int(df[col].notna().sum())
                for col in df.columns
            ],
            "Missing Values": [
                int(df[col].isna().sum())
                for col in df.columns
            ]
        })

        st.dataframe(
            info_df,
            use_container_width=True
        )

        st.subheader("Statistical Summary")

        st.dataframe(
            df.describe(include="all").transpose(),
            use_container_width=True
        )

        st.subheader("Missing Value Analysis")

        missing = df.isna().sum()
        missing = missing[missing > 0]

        if len(missing) > 0:

            fig, ax = plt.subplots(figsize=(10, 4))

            missing.plot(
                kind="bar",
                ax=ax
            )

            ax.set_title("Missing Values by Column")
            ax.set_ylabel("Missing Count")

            show_chart(fig)

        else:

            st.success("No missing values found.")


# =========================================================
# VARIABLE COMPARISON
# =========================================================

elif page == "Variable Comparison":

    st.title("📊 Variable Comparison")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        numeric_cols = get_numeric_columns(df)

        if not numeric_cols:

            st.warning("No numeric columns available.")

        else:

            selected_columns = st.multiselect(
                "Select numeric variables",
                numeric_cols,
                default=numeric_cols[:min(3, len(numeric_cols))]
            )

            if selected_columns:

                selected_data = df[selected_columns].apply(
                    pd.to_numeric,
                    errors="coerce"
                )

                st.subheader("Descriptive Statistics")

                st.dataframe(
                    selected_data.describe(),
                    use_container_width=True
                )

                selected_variable = st.selectbox(
                    "Select variable for distribution",
                    selected_columns
                )

                values = numeric_series(
                    df,
                    selected_variable
                ).dropna()

                if len(values) > 0:

                    fig, ax = plt.subplots(figsize=(9, 4))

                    sns.histplot(
                        values,
                        kde=True,
                        ax=ax
                    )

                    ax.set_title(
                        f"Distribution of {selected_variable}"
                    )

                    show_chart(fig)

                    fig, ax = plt.subplots(figsize=(8, 3))

                    sns.boxplot(
                        x=values,
                        ax=ax
                    )

                    ax.set_title(
                        f"Box Plot of {selected_variable}"
                    )

                    show_chart(fig)


# =========================================================
# RELATIONSHIP ANALYSIS
# =========================================================

elif page == "Relationship Analysis":

    st.title("🔗 Relationship Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        numeric_cols = get_numeric_columns(df)

        if len(numeric_cols) < 2:

            st.warning(
                "At least two numeric columns are required."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                x_col = st.selectbox(
                    "X-axis variable",
                    numeric_cols
                )

            with col2:

                y_options = [
                    col for col in numeric_cols
                    if col != x_col
                ]

                y_col = st.selectbox(
                    "Y-axis variable",
                    y_options
                )

            chart_df = pd.DataFrame({
                x_col: numeric_series(df, x_col),
                y_col: numeric_series(df, y_col)
            }).dropna()

            if len(chart_df) > 0:

                fig, ax = plt.subplots(figsize=(9, 5))

                sns.scatterplot(
                    data=chart_df,
                    x=x_col,
                    y=y_col,
                    ax=ax
                )

                ax.set_title(
                    f"{x_col} vs {y_col}"
                )

                show_chart(fig)

                correlation = chart_df[x_col].corr(
                    chart_df[y_col]
                )

                st.metric(
                    "Correlation Coefficient",
                    f"{correlation:.3f}"
                )

            st.divider()

            st.subheader("Correlation Matrix")

            corr = df[numeric_cols].apply(
                pd.to_numeric,
                errors="coerce"
            ).corr()

            fig, ax = plt.subplots(figsize=(10, 6))

            sns.heatmap(
                corr,
                annot=True,
                cmap="coolwarm",
                fmt=".2f",
                ax=ax
            )

            show_chart(fig)


# =========================================================
# MULTIVARIATE ANALYSIS
# =========================================================

elif page == "Multivariate Analysis":

    st.title("🧩 Multivariate Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        numeric_cols = get_numeric_columns(df)

        if len(numeric_cols) >= 2:

            selected = st.multiselect(
                "Select variables",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))]
            )

            if len(selected) >= 2:

                plot_df = df[selected].apply(
                    pd.to_numeric,
                    errors="coerce"
                ).dropna()

                if len(plot_df) > 500:

                    plot_df = plot_df.sample(
                        500,
                        random_state=42
                    )

                if len(plot_df) > 0:

                    st.subheader("Pair Plot")

                    pair_fig = sns.pairplot(
                        plot_df,
                        diag_kind="hist"
                    )

                    st.pyplot(
                        pair_fig.figure,
                        use_container_width=True
                    )

                    plt.close(pair_fig.figure)

                    st.subheader("Multivariate Correlation")

                    fig, ax = plt.subplots(figsize=(9, 6))

                    sns.heatmap(
                        plot_df.corr(),
                        annot=True,
                        cmap="viridis",
                        ax=ax
                    )

                    show_chart(fig)

                else:

                    st.warning(
                        "No usable numeric data in selected columns."
                    )

        else:

            st.warning(
                "At least two numeric variables are required."
            )


# =========================================================
# PERCENTAGE ANALYSIS
# =========================================================

elif page == "Percentage Analysis":

    st.title("📈 Percentage Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        cat_cols = get_categorical_columns(df)

        if not cat_cols:

            st.warning("No categorical columns available.")

        else:

            selected_col = st.selectbox(
                "Select categorical variable",
                cat_cols
            )

            counts = df[selected_col].value_counts(
                dropna=False
            )

            percentages = (
                counts / counts.sum()
            ) * 100

            result = pd.DataFrame({
                "Category": counts.index.astype(str),
                "Count": counts.values,
                "Percentage": percentages.values
            })

            st.subheader("Category Percentage Table")

            st.dataframe(
                result,
                use_container_width=True
            )

            fig, ax = plt.subplots(figsize=(9, 5))

            percentages.plot(
                kind="bar",
                ax=ax
            )

            ax.set_title(
                f"Percentage Distribution of {selected_col}"
            )

            ax.set_ylabel("Percentage (%)")
            ax.set_xlabel(selected_col)

            show_chart(fig)


# =========================================================
# CONTINGENCY ANALYSIS
# =========================================================

elif page == "Contingency Analysis":

    st.title("📋 Contingency Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        cat_cols = get_categorical_columns(df)

        if len(cat_cols) < 2:

            st.warning(
                "At least two categorical columns are required."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                row_col = st.selectbox(
                    "Select row variable",
                    cat_cols
                )

            with col2:

                col_options = [
                    col for col in cat_cols
                    if col != row_col
                ]

                column_col = st.selectbox(
                    "Select column variable",
                    col_options
                )

            cross = pd.crosstab(
                df[row_col],
                df[column_col]
            )

            st.subheader("Contingency Table")

            st.dataframe(
                cross,
                use_container_width=True
            )

            st.subheader("Row Percentage")

            row_percent = cross.div(
                cross.sum(axis=1).replace(0, np.nan),
                axis=0
            ) * 100

            st.dataframe(
                row_percent.fillna(0).round(2),
                use_container_width=True
            )

            st.subheader("Column Percentage")

            col_percent = cross.div(
                cross.sum(axis=0).replace(0, np.nan),
                axis=1
            ) * 100

            st.dataframe(
                col_percent.fillna(0).round(2),
                use_container_width=True
            )

            fig, ax = plt.subplots(figsize=(9, 5))

            sns.heatmap(
                cross,
                annot=True,
                fmt="g",
                cmap="Blues",
                ax=ax
            )

            ax.set_title("Contingency Heatmap")

            show_chart(fig)


# =========================================================
# TIME-SERIES ANALYSIS
# =========================================================

elif page == "Time-Series Analysis":

    st.title("📅 Time-Series Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        date_cols = get_date_columns(df)
        numeric_cols = get_numeric_columns(df)

        if not date_cols:

            st.warning(
                "No date column detected in the dataset."
            )

        elif not numeric_cols:

            st.warning(
                "No numeric variable available."
            )

        else:

            date_col = st.selectbox(
                "Select date column",
                date_cols
            )

            value_col = st.selectbox(
                "Select numeric variable",
                numeric_cols
            )

            time_df = df.copy()

            time_df[date_col] = pd.to_datetime(
                time_df[date_col],
                errors="coerce"
            )

            time_df[value_col] = pd.to_numeric(
                time_df[value_col],
                errors="coerce"
            )

            time_df = time_df.dropna(
                subset=[date_col, value_col]
            )

            time_df = time_df.sort_values(
                date_col
            )

            if len(time_df) > 0:

                st.subheader("Time-Series Trend")

                # Aggregate multiple records per date
                trend_df = (
                    time_df.groupby(date_col)[value_col]
                    .mean()
                    .reset_index()
                    .sort_values(date_col)
                )

                fig, ax = plt.subplots(figsize=(11, 5))

                ax.plot(
                    trend_df[date_col],
                    trend_df[value_col],
                    marker="o",
                    linewidth=1.5
                )

                ax.set_title(
                    f"{value_col} Over Time"
                )

                ax.set_xlabel("Date")
                ax.set_ylabel(value_col)

                plt.xticks(rotation=45)
                plt.tight_layout()

                show_chart(fig)

                st.subheader("Year-wise Average")

                yearly = (
                    trend_df
                    .assign(
                        Year=trend_df[date_col].dt.year
                    )
                    .groupby("Year")[value_col]
                    .mean()
                    .reset_index()
                )

                st.dataframe(
                    yearly,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No valid date and numeric values found."
                )


# =========================================================
# RESAMPLING
# =========================================================

elif page == "Resampling":

    st.title("🔄 Time-Series Resampling")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        date_cols = get_date_columns(df)
        numeric_cols = get_numeric_columns(df)
        cat_cols = get_categorical_columns(df)

        if not date_cols or not numeric_cols:

            st.warning(
                "A valid date and numeric column are required."
            )

        else:

            date_col = st.selectbox(
                "Date column",
                date_cols
            )

            value_col = st.selectbox(
                "Value column",
                numeric_cols
            )

            frequency_label = st.selectbox(
                "Resampling frequency",
                [
                    "Daily",
                    "Weekly",
                    "Monthly",
                    "Quarterly",
                    "Yearly"
                ]
            )

            aggregation = st.selectbox(
                "Aggregation method",
                [
                    "mean",
                    "sum",
                    "min",
                    "max",
                    "median"
                ]
            )

            group_col = st.selectbox(
                "Group by (optional)",
                ["None"] + cat_cols
            )

            if st.button("Perform Resampling"):

                freq_map = {
                    "Daily": "D",
                    "Weekly": "W",
                    "Monthly": "MS",
                    "Quarterly": "QS",
                    "Yearly": "YS"
                }

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
                        "No valid records available for resampling."
                    )

                else:

                    freq = freq_map[frequency_label]

                    if group_col == "None":

                        result = (
                            working_df
                            .set_index(date_col)[value_col]
                            .resample(freq)
                            .agg(aggregation)
                            .reset_index()
                        )

                    else:

                        result = (
                            working_df
                            .set_index(date_col)
                            .groupby(group_col)[value_col]
                            .resample(freq)
                            .agg(aggregation)
                            .reset_index()
                        )

                    st.session_state.resampled_data = result

                    st.success(
                        "Resampling completed successfully!"
                    )

            result = st.session_state.resampled_data

            if result is not None:

                st.subheader("Resampled Dataset")

                st.dataframe(
                    result,
                    use_container_width=True
                )

                st.subheader("Resampled Trend")

                fig, ax = plt.subplots(figsize=(10, 5))

                if (
                    group_col != "None"
                    and group_col in result.columns
                ):

                    for group_name, group_data in result.groupby(
                        group_col
                    ):

                        ax.plot(
                            group_data[date_col],
                            group_data[value_col],
                            marker="o",
                            label=str(group_name)
                        )

                    ax.legend()

                else:

                    ax.plot(
                        result[date_col],
                        result[value_col],
                        marker="o"
                    )

                ax.set_title("Resampled Time-Series Trend")

                plt.xticks(rotation=45)
                plt.tight_layout()

                show_chart(fig)


# =========================================================
# EXPORT
# =========================================================

elif page == "Export":

    st.title("📥 Export Analysis")

    if df is None:

        st.warning("Please load a dataset first.")

    else:

        st.subheader("Download Original Dataset")

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Dataset CSV",
            data=csv_data,
            file_name="marketpulse_dataset.csv",
            mime="text/csv"
        )

        st.divider()

        st.subheader("Download Statistical Summary")

        summary = df.describe(
            include="all"
        ).transpose()

        summary_csv = summary.to_csv().encode(
            "utf-8"
        )

        st.download_button(
            label="Download Statistical Summary",
            data=summary_csv,
            file_name="marketpulse_summary.csv",
            mime="text/csv"
        )

        if st.session_state.resampled_data is not None:

            st.divider()

            st.subheader("Download Resampled Dataset")

            resampled_csv = (
                st.session_state.resampled_data
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                label="Download Resampled CSV",
                data=resampled_csv,
                file_name="marketpulse_resampled.csv",
                mime="text/csv"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    MarketPulse | Food Price & Seasonal Trend Explorer<br>
    Interactive Exploratory Data Analysis Dashboard<br>
    Built with Python, Streamlit, Pandas, NumPy and Seaborn
</div>
""", unsafe_allow_html=True)
