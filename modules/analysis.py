
"""
Reusable analysis helpers for MarketPulse.
EDA Units 4 and 5
"""

import pandas as pd
import numpy as np


# --------------------------------------------------
# 1. AUTOMATIC COLUMN DETECTION
# --------------------------------------------------

def detect_columns(df):
    numeric = []
    dates = []
    categorical = []

    for col in df.columns:
        s = df[col]

        if pd.api.types.is_datetime64_any_dtype(s):
            dates.append(col)
            continue

        if pd.api.types.is_numeric_dtype(s):
            numeric.append(col)
            continue

        nonempty = s.dropna()

        # Detect date columns
        if len(nonempty) >= 2:
            parsed = pd.to_datetime(nonempty, errors="coerce")

            if parsed.notna().mean() >= 0.8:
                dates.append(col)
                continue

        # Detect numeric columns stored as text
        converted = pd.to_numeric(s, errors="coerce")

        if len(nonempty) > 0:
            ratio = converted.notna().sum() / len(nonempty)

            if ratio >= 0.85:
                numeric.append(col)
            else:
                categorical.append(col)
        else:
            categorical.append(col)

    return {
        "numeric": numeric,
        "categorical": categorical,
        "dates": dates
    }


# --------------------------------------------------
# 2. DATASET PROFILE
# --------------------------------------------------

def dataset_profile(df):
    det = detect_columns(df)

    return pd.DataFrame({
        "Column": list(df.columns),

        "Data type": [
            str(t) for t in df.dtypes
        ],

        "Detected as": [
            "Date" if c in det["dates"]
            else "Numeric" if c in det["numeric"]
            else "Categorical"
            for c in df.columns
        ],

        "Non-missing": [
            int(df[c].notna().sum())
            for c in df.columns
        ],

        "Missing": [
            int(df[c].isna().sum())
            for c in df.columns
        ],

        "Unique values": [
            int(df[c].nunique(dropna=True))
            for c in df.columns
        ]
    })


# --------------------------------------------------
# 3. DATE PREPARATION
# --------------------------------------------------

def prepare_dates(df, date_col):
    out = df.copy()

    out["_date"] = pd.to_datetime(
        out[date_col],
        errors="coerce"
    )

    valid_count = int(out["_date"].notna().sum())

    out = out.dropna(
        subset=["_date"]
    ).copy()

    return out, valid_count


# --------------------------------------------------
# 4. PERCENTAGE ANALYSIS
# --------------------------------------------------

def percentage_table(df, column):
    counts = (
        df[column]
        .fillna("(Missing)")
        .astype(str)
        .value_counts()
    )

    if counts.empty:
        return pd.DataFrame(
            columns=["Percentage"]
        )

    percentages = (
        counts / counts.sum() * 100
    ).round(1)

    return percentages.rename(
        "Percentage"
    ).to_frame()


# --------------------------------------------------
# 5. CONTINGENCY TABLE
# --------------------------------------------------

def contingency_table(df, row, col, mode="Counts"):

    tab = pd.crosstab(
        df[row].fillna("(Missing)"),
        df[col].fillna("(Missing)"),
        dropna=False
    )

    if mode == "Row percentages":

        return (
            tab.div(
                tab.sum(axis=1).replace(0, np.nan),
                axis=0
            ) * 100
        ).round(1)

    elif mode == "Column percentages":

        return (
            tab.div(
                tab.sum(axis=0).replace(0, np.nan),
                axis=1
            ) * 100
        ).round(1)

    return tab


# --------------------------------------------------
# 6. CORRELATION ANALYSIS
# --------------------------------------------------

def correlation_summary(df, columns):

    if not columns:
        return pd.DataFrame()

    numeric_data = df[columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    return numeric_data.corr()


# --------------------------------------------------
# 7. SAFE GROUP ANALYSIS
# --------------------------------------------------

def safe_groupby(
    df,
    group_col,
    value_col,
    agg="mean"
):

    if group_col not in df.columns:
        return pd.Series(dtype=float)

    if value_col not in df.columns:
        return pd.Series(dtype=float)

    values = pd.to_numeric(
        df[value_col],
        errors="coerce"
    )

    temp = pd.DataFrame({
        "group": df[group_col],
        "value": values
    })

    return temp.groupby(
        "group",
        dropna=False
    )["value"].agg(agg)


# --------------------------------------------------
# 8. TIME SERIES RESAMPLING
# --------------------------------------------------

def resample_series(
    df,
    value_col,
    freq="Weekly",
    agg="Mean",
    group_col=None
):

    # Supported time intervals
    rules = {
        "Daily": "D",
        "Weekly": "W",
        "Monthly": "M"
    }

    # Supported aggregation methods
    aggs = {
        "Mean": "mean",
        "Median": "median",
        "Sum": "sum",
        "Minimum": "min",
        "Maximum": "max",
        "Count": "count"
    }

    # Validate columns
    if "_date" not in df.columns:
        return pd.DataFrame(
            columns=["Period", "Value"]
        )

    if value_col not in df.columns:
        return pd.DataFrame(
            columns=["Period", "Value"]
        )

    work = df.copy()

    # Convert date and numeric columns
    work["_date"] = pd.to_datetime(
        work["_date"],
        errors="coerce"
    )

    work["_value"] = pd.to_numeric(
        work[value_col],
        errors="coerce"
    )

    # Remove invalid observations
    work = work.dropna(
        subset=["_date", "_value"]
    )

    if work.empty:
        return pd.DataFrame(
            columns=["Period", "Value"]
        )

    # Select frequency
    rule = rules.get(freq, "W")

    # Create time buckets
    if rule == "M":

        work["_period"] = (
            work["_date"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

    elif rule == "W":

        work["_period"] = (
            work["_date"]
            .dt.to_period("W")
            .dt.start_time
        )

    else:

        work["_period"] = (
            work["_date"].dt.floor("D")
        )

    # Select aggregation method
    aggregation = aggs.get(
        agg,
        "mean"
    )

    # Check optional grouping column
    use_group = (
        group_col is not None
        and str(group_col).strip().lower() != "none"
        and str(group_col).strip() != ""
        and group_col in work.columns
    )

    # Grouped resampling
    if use_group:

        out = (
            work.groupby(
                ["_period", group_col],
                dropna=False
            )["_value"]
            .agg(aggregation)
            .reset_index()
        )

    # Normal resampling without category grouping
    else:

        out = (
            work.groupby(
                "_period",
                dropna=False
            )["_value"]
            .agg(aggregation)
            .reset_index()
        )

    # Rename output columns
    out = out.rename(
        columns={
            "_period": "Period",
            "_value": "Value"
        }
    )

    return (
        out.sort_values("Period")
        .reset_index(drop=True)
    )
