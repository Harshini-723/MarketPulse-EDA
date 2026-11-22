
import os

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

/* Hero */

.market-hero {
    background: linear-gradient(115deg, #102f38, #147765);
    padding: 55px 48px;
    border-radius: 25px;
    color: white;
    margin-bottom: 35px;
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
    font-size: 43px;
    line-height: 1.2;
    font-weight: 800;
    color: white;
    margin-bottom: 18px;
}

.market-hero p {
    font-size: 16px;
    line-height: 1.8;
    max-width: 750px;
    color: #e0f0ed;
}

/* Metric cards */

.metric-card {
    background: white;
    border: 1px solid #e1ebea;
    border-radius: 18px;
    padding: 22px;
    min-height: 135px;
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
    font-size: 30px;
    font-weight: 800;
    margin-top: 12px;
}

.metric-description {
    color: #82949a;
    font-size: 12px;
    margin-top: 5px;
}

/* Feature cards */

.feature-card {
    background: white;
    border: 1px solid #e1ebea;
    border-radius: 18px;
    padding: 23px;
    min-height: 165px;
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

.stButton > button {
    background: #126354;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #0d4b40;
    color: white;
    border: none;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "data" not in st.session_state:
    st.session_state.data = None

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = None

if "resampled_data" not in st.session_state:
    st.session_state.resampled_data = None

if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def load_sample_dataset():

    sample_path = os.path.join(
        "data",
        "sample_market_prices.csv"
    )

    if os.path.exists(sample_path):
        return pd.read_csv(sample_path)

    return None


def get_data():

    if st.session_state.data is None:
        st.warning(
            "Please upload a dataset or load the sample dataset first."
        )
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

        try:
            converted = pd.to_datetime(
                df[col],
                errors="coerce"
            )

            if converted.notna().mean() >= 0.7:
                date_columns.append(col)

        except Exception:
            pass

    categorical_columns = [
        col for col in df.columns
        if col not in numeric_columns
        and col not in date_columns
    ]

    return numeric_columns, categorical_columns, date_columns


def show_metric(label, value, description=""):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def create_chart():

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    ax.grid(
        axis="y",
        alpha=0.2
    )

    return fig, ax


def download_csv(df, filename):

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
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

        st.success(st.session_state.dataset_name)

        st.caption(
            f"{len(st.session_state.data)} rows | "
            f"{len(st.session_state.data.columns)} columns"
        )

    else:

        st.caption("No dataset selected")

    st.markdown("---")

    st.caption("MarketPulse | Analytics Dashboard")


# =========================================================
# HOME PAGE
# =========================================================

if page == "Home":

    st.html("""
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
            food-price dataset.
        </p>

    </div>
    """)

    st.markdown("## Your EDA Workspace")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.html("""
        <div class="feature-card">
            <div class="feature-label">RELATIONSHIPS</div>
            <div class="feature-number">01</div>
            <div class="feature-description">
                Explore pairs of numeric variables and
                analyze their correlations.
            </div>
        </div>
        """)

    with col2:

        st.html("""
        <div class="feature-card">
            <div class="feature-label">MULTIPLE VARIABLES</div>
            <div class="feature-number">02</div>
            <div class="feature-description">
                Compare categories and analyze
                multiple variables together.
            </div>
        </div>
        """)

    with col3:

        st.html("""
        <div class="feature-card">
            <div class="feature-label">TIME & SEASONALITY</div>
            <div class="feature-number">03</div>
            <div class="feature-description">
                Track price trends and resample
                time-series data.
            </div>
        </div>
        """)

    st.markdown("## Dashboard Capabilities")

    capabilities = [
        ("📂", "Dataset Management",
         "Upload CSV files and inspect dataset structure."),

        ("📊", "Statistical Analysis",
         "Calculate descriptive statistics and distributions."),

        ("🔗", "Relationship Analysis",
         "Explore correlations between variables."),

        ("🧮", "Multivariate Analysis",
         "Compare numerical data across categories."),

        ("📅", "Time-Series Analysis",
         "Analyze changes in prices over time."),

        ("⬇", "Export Results",
         "Download processed datasets and results.")
    ]

    cols = st.columns(3)

    for i, (icon, title, description) in enumerate(capabilities):

        with cols[i % 3]:

            st.html(f"""
            <div class="feature-card">
                <h3>{icon} {title}</h3>
                <p class="feature-description">
                    {description}
                </p>
            </div>
            """)

    st.markdown("---")

    if st.button("Load Sample Dataset"):

        sample = load_sample_dataset()

        if sample is not None:

            st.session_state.data = sample
            st.session_state.dataset_name = "Sample Market Prices"

            st.success("Sample dataset loaded successfully!")

            st.rerun()

        else:

            st.error(
                "Sample dataset not found. "
                "Check data/sample_market_prices.csv."
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

        try:

            uploaded_df = pd.read_csv(uploaded_file)

            st.session_state.data = uploaded_df
            st.session_state.dataset_name = uploaded_file.name

            st.success("Dataset uploaded successfully!")

            st.markdown("## Dataset Preview")

            st.dataframe(
                uploaded_df.head(10),
                use_container_width=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                show_metric("Total Rows", f"{len(uploaded_df):,}")

            with c2:
                show_metric("Total Columns", f"{len(uploaded_df.columns):,}")

            with c3:
                show_metric(
                    "Missing Values",
                    f"{uploaded_df.isna().sum().sum():,}"
                )

        except Exception as e:

            st.error(f"Unable to read CSV: {e}")

    st.markdown("---")

    st.markdown("### Load Included Sample Dataset")

    if st.button("Load Sample Market Dataset"):

        sample = load_sample_dataset()

        if sample is not None:

            st.session_state.data = sample
            st.session_state.dataset_name = "Sample Market Prices"

            st.success("Sample dataset loaded!")

            st.rerun()

        else:

            st.error("Sample dataset file was not found.")


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

            st.pyplot(fig)
            plt.close(fig)

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

            fig, ax = create_chart()

            if chart_type == "Histogram":

                sns.histplot(
                    df[selected_column].dropna(),
                    kde=True,
                    ax=ax
                )

            elif chart_type == "Box Plot":

                sns.boxplot(
                    x=df[selected_column],
                    ax=ax
                )

            elif chart_type == "Density Plot":

                sns.kdeplot(
                    df[selected_column].dropna(),
                    fill=True,
                    ax=ax
                )

            elif chart_type == "Violin Plot":

                sns.violinplot(
                    x=df[selected_column],
                    ax=ax
                )

            ax.set_title(
                f"{chart_type} of {selected_column}"
            )

            st.pyplot(fig)
            plt.close(fig)

            st.markdown("## Statistical Summary")

            st.dataframe(
                df[selected_column].describe().to_frame("Value"),
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

                y_options = [
                    col for col in numeric_cols
                    if col != x_col
                ]

                y_col = st.selectbox(
                    "Select Y Variable",
                    y_options
                )

            fig, ax = create_chart()

            sns.scatterplot(
                data=df,
                x=x_col,
                y=y_col,
                ax=ax
            )

            ax.set_title(f"{x_col} vs {y_col}")

            st.pyplot(fig)
            plt.close(fig)

            correlation = df[x_col].corr(df[y_col])

            st.metric(
                "Pearson Correlation",
                f"{correlation:.4f}" if pd.notna(correlation) else "N/A"
            )

            st.markdown("## Correlation Matrix")

            corr = df[numeric_cols].corr()

            fig, ax = plt.subplots(figsize=(10, 6))

            sns.heatmap(
                corr,
                annot=True,
                cmap="YlGnBu",
                fmt=".2f",
                ax=ax
            )

            ax.set_title("Correlation Heatmap")

            st.pyplot(fig)
            plt.close(fig)


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

                    pair_df = df[selected_numeric].dropna()

                    if len(pair_df) > 500:
                        pair_df = pair_df.sample(
                            500,
                            random_state=42
                        )

                    fig = sns.pairplot(
                        pair_df,
                        diag_kind="hist"
                    )

                    st.pyplot(fig)
                    plt.close(fig)

                else:

                    st.info(
                        "Select at least two variables for a pair plot."
                    )

                st.markdown("## Multivariable Correlation")

                corr = df[selected_numeric].corr()

                fig, ax = plt.subplots(figsize=(9, 5))

                sns.heatmap(
                    corr,
                    annot=True,
                    cmap="crest",
                    fmt=".2f",
                    ax=ax
                )

                st.pyplot(fig)
                plt.close(fig)

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

                grouped = (
                    df.groupby(category_col, observed=True)[value_col]
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

                st.pyplot(fig)
                plt.close(fig)


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

            counts = df[selected_column].value_counts(
                dropna=False
            )

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

            fig, ax = plt.subplots(figsize=(8, 6))

            counts.head(15).plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax
            )

            ax.set_ylabel("")
            ax.set_title(
                f"Percentage Distribution of {selected_column}"
            )

            st.pyplot(fig)
            plt.close(fig)

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
                df[row_col],
                df[column_col],
                dropna=False
            )

            if table_type == "Row Percentage":

                result = cross_tab.div(
                    cross_tab.sum(axis=1),
                    axis=0
                ) * 100

            elif table_type == "Column Percentage":

                result = cross_tab.div(
                    cross_tab.sum(axis=0),
                    axis=1
                ) * 100

            else:

                result = cross_tab

            st.markdown("## Contingency Table")

            st.dataframe(
                result.round(2),
                use_container_width=True
            )

            fig, ax = plt.subplots(figsize=(10, 6))

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

            st.pyplot(fig)
            plt.close(fig)

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
                "No date column detected. "
                "Please upload a dataset containing a date column."
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

                fig, ax = create_chart()

                sns.lineplot(
                    data=plot_df,
                    x=date_col,
                    y=value_col,
                    ax=ax
                )

                ax.set_title(f"{value_col} Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel(value_col)

                plt.xticks(rotation=45)

                st.pyplot(fig)
                plt.close(fig)

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

                    st.pyplot(fig)
                    plt.close(fig)

                    monthly_df = monthly.reset_index()

                    monthly_df.columns = [
                        "Month",
                        "Average"
                    ]

                    st.dataframe(
                        monthly_df,
                        use_container_width=True
                    )

                st.markdown("## Date Range")

                st.write(
                    f"Start Date: {plot_df[date_col].min()}"
                )

                st.write(
                    f"End Date: {plot_df[date_col].max()}"
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
                    date_cols
                )

            with c2:

                value_col = st.selectbox(
                    "Select Numeric Column",
                    numeric_cols
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

            if st.button("Generate Resampled Data"):

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

                        working_df = working_df.sort_values(
                            date_col
                        )

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
                                .groupby(group_col)[value_col]
                                .resample(freq)
                                .agg(agg)
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

                st.pyplot(fig)
                plt.close(fig)

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

            for col in cleaned_df.select_dtypes(
                include=np.number
            ).columns:

                median = cleaned_df[col].median()

                if pd.notna(median):

                    cleaned_df[col] = cleaned_df[col].fillna(
                        median
                    )

            for col in cleaned_df.select_dtypes(
                include=["object", "category"]
            ).columns:

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

st.html("""
<div style="
    text-align:center;
    color:#82949a;
    font-size:12px;
    padding:15px;
">
    MarketPulse | Food Price & Seasonal Trend Explorer
    <br>
    Interactive Exploratory Data Analysis Dashboard
</div>
""")
