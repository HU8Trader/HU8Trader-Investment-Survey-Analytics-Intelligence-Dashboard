"""
================================================================================
INVESTMENT SURVEY — ADVANCED BUSINESS ANALYSIS
================================================================================

Pipeline:

01_data_loader.py
        ↓
02_data_audit.py
        ↓
03_data_cleaning.py
        ↓
04_data_transformation.py
        ↓
05_feature_engineering.py
        ↓
06_business_metrics.py
        ↓
07_analysis.py
        ↓
08_visualization.py
        ↓
09_dashboard.py

================================================================================
PURPOSE
================================================================================

This module performs advanced business analysis after the business metrics layer.

It answers questions such as:

1. Which investments are most preferred?
2. Do females prefer Gold?
3. Do younger investors prefer Equity?
4. Who prefers Bonds?
5. How does investment preference vary by age?
6. How does preference vary by gender?
7. How does preference vary by investment objective?
8. Which objectives dominate different investments?
9. How do demographics relate to investment behaviour?
10. What insights can support executive recommendations?

================================================================================
IMPORTANT BUSINESS RULES
================================================================================

Preference Rank:

    1 = Highest Preference
    7 = Lowest Preference

Therefore:

    LOWER Average Preference Rank
    =
    STRONGER Preference

================================================================================
EXPECTED RETURN
================================================================================

Expected return is categorical in the source survey:

    10%-20%
    20%-30%
    30%-40%

Therefore this module DOES NOT calculate an artificial
average expected return.

================================================================================
UNPIVOT / DUPLICATION RULE
================================================================================

The investment table contains multiple investment rows per respondent.

Example:

    Respondent 1
        Equity
        Gold
        Mutual Fund
        PPF
        ...

Therefore:

    len(investment_df)

or

    COUNTROWS(investment_df)

must NOT be interpreted as respondent count.

Whenever respondent counts are required:

    nunique(Respondent_ID)

is used.

================================================================================
DATA-GRAIN RULE
================================================================================

RESPONDENT-LEVEL ATTRIBUTES:

    Age
    Gender
    Investment_Objective
    Investment_Purpose
    Decision_Factor
    Investment_Duration
    Expected_Return_Range
    Savings_Objective
    Information_Source
    Investment_Monitoring_Frequency

INVESTMENT-LEVEL ATTRIBUTES:

    Investment_Type
    Preference_Rank
    Preference_Score

Whenever a respondent-level attribute is analyzed against
Investment_Type, the respondent table is joined to the
investment table using Respondent_ID.

================================================================================
"""

# ==============================================================================
# 1. IMPORTS
# ==============================================================================

from pathlib import Path

import numpy as np
import pandas as pd


# ==============================================================================
# 2. PROJECT PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURES_DIR = PROJECT_ROOT / "data" / "features"
METRICS_DIR = PROJECT_ROOT / "data" / "metrics"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"

ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================================================================
# 3. INPUT FILES
# ==============================================================================

RESPONDENT_FILE = (
    FEATURES_DIR / "respondent_features.csv"
)

INVESTMENT_FILE = (
    FEATURES_DIR / "investment_features.csv"
)


# ==============================================================================
# 4. OUTPUT FILES
# ==============================================================================

OUTPUTS = {

    "investment_analysis":
        ANALYSIS_DIR /
        "investment_preference_analysis.csv",

    "gender_analysis":
        ANALYSIS_DIR /
        "gender_investment_analysis.csv",

    "age_analysis":
        ANALYSIS_DIR /
        "age_investment_analysis.csv",

    "objective_analysis":
        ANALYSIS_DIR /
        "objective_investment_analysis.csv",

    "female_analysis":
        ANALYSIS_DIR /
        "female_investment_preference.csv",

    "young_analysis":
        ANALYSIS_DIR /
        "young_investor_preference.csv",

    "bond_analysis":
        ANALYSIS_DIR /
        "bond_preference_analysis.csv",

    "gender_preference_summary":
        ANALYSIS_DIR /
        "gender_preference_summary.csv",

    "age_preference_summary":
        ANALYSIS_DIR /
        "age_preference_summary.csv",

    "objective_preference_summary":
        ANALYSIS_DIR /
        "objective_preference_summary.csv",

    "purpose_analysis":
        ANALYSIS_DIR /
        "purpose_investment_analysis.csv",

    "factor_analysis":
        ANALYSIS_DIR /
        "factor_investment_analysis.csv",

    "duration_analysis":
        ANALYSIS_DIR /
        "duration_investment_analysis.csv",

    "expected_return_analysis":
        ANALYSIS_DIR /
        "expected_return_analysis.csv",

    "savings_analysis":
        ANALYSIS_DIR /
        "savings_investment_analysis.csv",

    "source_analysis":
        ANALYSIS_DIR /
        "source_investment_analysis.csv",

    "monitoring_analysis":
        ANALYSIS_DIR /
        "monitoring_investment_analysis.csv",

    "gender_gap":
        ANALYSIS_DIR /
        "gender_preference_gap.csv",

    "executive_insights":
        ANALYSIS_DIR /
        "executive_analytical_insights.csv",

    "recommendations":
        ANALYSIS_DIR /
        "analytical_recommendations.csv",

    "analysis_summary":
        ANALYSIS_DIR /
        "analysis_summary.csv"
}


# ==============================================================================
# 5. COLUMN FINDER
# ==============================================================================

def find_column(df, candidates):
    """
    Find a column using case-insensitive matching.
    """

    if df is None or df.empty:
        return None

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = str(candidate).strip().lower()

        if key in normalized:
            return normalized[key]

    return None


# ==============================================================================
# 6. COLUMN IDENTIFICATION
# ==============================================================================

def identify_columns(respondent_df, investment_df):
    """
    Identify logical columns in respondent and investment tables.
    """

    # --------------------------------------------------------------------------
    # RESPONDENT COLUMNS
    # --------------------------------------------------------------------------

    respondent = {

        "id": find_column(
            respondent_df,
            [
                "Respondent_ID",
                "respondent_id",
                "Response_ID",
                "response_id",
                "ID",
                "id"
            ]
        ),

        "age": find_column(
            respondent_df,
            [
                "Age",
                "age"
            ]
        ),

        "gender": find_column(
            respondent_df,
            [
                "Gender",
                "gender"
            ]
        ),

        "objective": find_column(
            respondent_df,
            [
                "Investment_Objective",
                "investment_objective",
                "Objective",
                "objective"
            ]
        ),

        "purpose": find_column(
            respondent_df,
            [
                "Investment_Purpose",
                "investment_purpose",
                "Purpose",
                "purpose"
            ]
        ),

        "factor": find_column(
            respondent_df,
            [
                "Decision_Factor",
                "decision_factor",
                "Factor",
                "factor"
            ]
        ),

        "duration": find_column(
            respondent_df,
            [
                "Investment_Duration",
                "investment_duration",
                "Duration",
                "duration"
            ]
        ),

        "expected": find_column(
            respondent_df,
            [
                "Expected_Return_Range",
                "expected_return_range",
                "Expected_Return",
                "expected_return",
                "Expected",
                "expected"
            ]
        ),

        "savings": find_column(
            respondent_df,
            [
                "Savings_Objective",
                "savings_objective",
                "Savings Objective"
            ]
        ),

        "source": find_column(
            respondent_df,
            [
                "Information_Source",
                "information_source",
                "Source",
                "source"
            ]
        ),

        "monitoring": find_column(
            respondent_df,
            [
                "Investment_Monitoring_Frequency",
                "investment_monitoring_frequency",
                "Monitoring_Frequency",
                "monitoring_frequency"
            ]
        ),

        "age_group": find_column(
            respondent_df,
            [
                "Age_Group",
                "age_group",
                "Age Group"
            ]
        ),

        "age_segment": find_column(
            respondent_df,
            [
                "Investor_Age_Segment",
                "investor_age_segment",
                "Age_Segment",
                "age_segment"
            ]
        )
    }


    # --------------------------------------------------------------------------
    # INVESTMENT COLUMNS
    # --------------------------------------------------------------------------

    investment = {

        "id": find_column(
            investment_df,
            [
                "Respondent_ID",
                "respondent_id",
                "Response_ID",
                "response_id",
                "ID",
                "id"
            ]
        ),

        "type": find_column(
            investment_df,
            [
                "Investment_Type",
                "investment_type",
                "Investment Type"
            ]
        ),

        "rank": find_column(
            investment_df,
            [
                "Preference_Rank",
                "preference_rank",
                "Preference Rank"
            ]
        ),

        "score": find_column(
            investment_df,
            [
                "Preference_Score",
                "preference_score",
                "Preference Score"
            ]
        )
    }

    return respondent, investment


# ==============================================================================
# 7. LOAD DATA
# ==============================================================================

def load_data():

    print("\nLoading feature data...")

    if not RESPONDENT_FILE.exists():

        raise FileNotFoundError(
            f"\nMissing respondent feature file:\n"
            f"{RESPONDENT_FILE}\n\n"
            f"Run 05_feature_engineering.py first."
        )

    if not INVESTMENT_FILE.exists():

        raise FileNotFoundError(
            f"\nMissing investment feature file:\n"
            f"{INVESTMENT_FILE}\n\n"
            f"Run 05_feature_engineering.py first."
        )

    respondent_df = pd.read_csv(
        RESPONDENT_FILE
    )

    investment_df = pd.read_csv(
        INVESTMENT_FILE
    )

    print(
        f"Respondent records : {len(respondent_df):,}"
    )

    print(
        f"Investment records : {len(investment_df):,}"
    )

    return respondent_df, investment_df


# ==============================================================================
# 8. NORMALIZE TEXT
# ==============================================================================

def normalize_text(series):

    return (
        series
        .astype("string")
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "none": pd.NA
            }
        )
    )


# ==============================================================================
# 9. PREPARE INVESTMENT DATA
# ==============================================================================

def prepare_investment_data(
    investment_df,
    columns
):

    df = investment_df.copy()

    rank_column = columns.get("rank")

    if rank_column is not None:

        df[rank_column] = pd.to_numeric(
            df[rank_column],
            errors="coerce"
        )

    score_column = columns.get("score")

    if score_column is not None:

        df[score_column] = pd.to_numeric(
            df[score_column],
            errors="coerce"
        )

    return df


# ==============================================================================
# 10. CREATE RESPONDENT LOOKUP
# ==============================================================================

def create_respondent_lookup(
    respondent_df,
    respondent_columns,
    attributes
):
    """
    Creates a one-row-per-respondent lookup table.

    This prevents duplication when respondent-level
    attributes are joined with the unpivoted investment table.
    """

    respondent_id = respondent_columns.get("id")

    if respondent_id is None:

        raise ValueError(
            "Respondent ID column could not be identified."
        )

    available = [
        respondent_id
    ]

    for attribute in attributes:

        column = respondent_columns.get(
            attribute
        )

        if (
            column is not None
            and column not in available
        ):

            available.append(column)

    lookup = (
        respondent_df[available]
        .drop_duplicates(
            subset=[respondent_id]
        )
        .copy()
    )

    return lookup


# ==============================================================================
# 11. ATTACH RESPONDENT ATTRIBUTE
# ==============================================================================

def attach_respondent_attribute(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns,
    attribute
):
    """
    Safely attaches a respondent-level attribute
    to investment-level data.

    Example:

        Investment_Purpose

    exists in respondent_df but not necessarily
    in investment_df.

    The join is performed using Respondent_ID.
    """

    respondent_id = respondent_columns.get("id")

    investment_id = investment_columns.get("id")

    attribute_column = respondent_columns.get(
        attribute
    )

    if not all(
        [
            respondent_id,
            investment_id,
            attribute_column
        ]
    ):

        return pd.DataFrame()

    lookup = create_respondent_lookup(
        respondent_df,
        respondent_columns,
        [attribute]
    )

    working = investment_df.merge(
        lookup,
        left_on=investment_id,
        right_on=respondent_id,
        how="left",
        suffixes=("", "_respondent")
    )

    return working


# ==============================================================================
# 12. ATTACH MULTIPLE RESPONDENT ATTRIBUTES
# ==============================================================================

def attach_respondent_attributes(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns,
    attributes
):
    """
    Attach multiple respondent-level attributes
    to investment-level data in a single controlled join.
    """

    respondent_id = respondent_columns.get("id")
    investment_id = investment_columns.get("id")

    if not respondent_id or not investment_id:
        return pd.DataFrame()

    valid_attributes = []

    for attribute in attributes:

        column = respondent_columns.get(attribute)

        if column is not None:
            valid_attributes.append(attribute)

    if not valid_attributes:
        return pd.DataFrame()

    lookup = create_respondent_lookup(
        respondent_df,
        respondent_columns,
        valid_attributes
    )

    working = investment_df.merge(
        lookup,
        left_on=investment_id,
        right_on=respondent_id,
        how="left",
        suffixes=("", "_respondent")
    )

    return working


# ==============================================================================
# 13. OVERALL INVESTMENT PREFERENCE
# ==============================================================================

def analyze_overall_preference(
    investment_df,
    columns
):
    """
    Overall investment preference.

    Lower average preference rank = stronger preference.
    """

    type_column = columns.get("type")
    id_column = columns.get("id")
    rank_column = columns.get("rank")

    if not all(
        [
            type_column,
            id_column,
            rank_column
        ]
    ):

        return pd.DataFrame()

    working = investment_df[
        [
            id_column,
            type_column,
            rank_column
        ]
    ].copy()

    working = working.dropna(
        subset=[
            type_column,
            rank_column
        ]
    )

    if working.empty:
        return pd.DataFrame()

    result = (

        working

        .groupby(
            type_column,
            as_index=False
        )

        .agg(

            Unique_Respondents=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            ),

            Median_Preference_Rank=(
                rank_column,
                "median"
            ),

            Best_Preference_Rank=(
                rank_column,
                "min"
            ),

            Worst_Preference_Rank=(
                rank_column,
                "max"
            )
        )
    )

    result[
        "Overall_Preference_Rank"
    ] = (

        result[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return (

        result

        .sort_values(
            [
                "Overall_Preference_Rank",
                "Average_Preference_Rank"
            ]
        )

        .reset_index(drop=True)
    )


# ==============================================================================
# 14. GENERIC SEGMENT × INVESTMENT ANALYSIS
# ==============================================================================

def analyze_segment_investment(
    investment_df,
    segment_column,
    type_column,
    id_column,
    rank_column
):
    """
    Generic segment × investment analysis.

    Lower average preference rank = stronger preference.
    """

    if not all(
        [
            segment_column,
            type_column,
            id_column,
            rank_column
        ]
    ):

        return pd.DataFrame()

    working = investment_df[
        [
            segment_column,
            type_column,
            id_column,
            rank_column
        ]
    ].copy()

    working = working.dropna(
        subset=[
            segment_column,
            type_column,
            rank_column
        ]
    )

    if working.empty:
        return pd.DataFrame()

    result = (

        working

        .groupby(
            [
                segment_column,
                type_column
            ],
            as_index=False
        )

        .agg(

            Unique_Respondents=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            )
        )
    )

    result[
        "Segment_Preference_Rank"
    ] = (

        result

        .groupby(
            segment_column
        )[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return result


# ==============================================================================
# 15. GENDER × INVESTMENT
# ==============================================================================

def analyze_gender_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):
    """
    Gender is a respondent-level attribute.

    Therefore gender is first joined to the investment table.
    """

    working = attach_respondent_attribute(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "gender"
    )

    if working.empty:
        return pd.DataFrame()

    gender_column = respondent_columns.get("gender")
    type_column = investment_columns.get("type")
    id_column = investment_columns.get("id")
    rank_column = investment_columns.get("rank")

    return analyze_segment_investment(
        working,
        gender_column,
        type_column,
        id_column,
        rank_column
    )


# ==============================================================================
# 16. AGE GROUP × INVESTMENT
# ==============================================================================

def analyze_age_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):
    """
    Age group is a respondent-level attribute.
    """

    age_group_column = respondent_columns.get(
        "age_group"
    )

    if age_group_column is not None:

        working = attach_respondent_attribute(
            respondent_df,
            investment_df,
            respondent_columns,
            investment_columns,
            "age_group"
        )

        if not working.empty:

            return analyze_segment_investment(
                working,
                age_group_column,
                investment_columns.get("type"),
                investment_columns.get("id"),
                investment_columns.get("rank")
            )

    # --------------------------------------------------------------------------
    # Fallback: derive age groups from actual Age
    # --------------------------------------------------------------------------

    age_column = respondent_columns.get("age")

    if age_column is None:
        return pd.DataFrame()

    working = attach_respondent_attribute(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "age"
    )

    if working.empty:
        return pd.DataFrame()

    working[age_column] = pd.to_numeric(
        working[age_column],
        errors="coerce"
    )

    working["Derived_Age_Group"] = pd.cut(
        working[age_column],
        bins=[
            -np.inf,
            29,
            39,
            49,
            59,
            np.inf
        ],
        labels=[
            "Under 30",
            "30-39",
            "40-49",
            "50-59",
            "60+"
        ]
    )

    return analyze_segment_investment(
        working,
        "Derived_Age_Group",
        investment_columns.get("type"),
        investment_columns.get("id"),
        investment_columns.get("rank")
    )


# ==============================================================================
# 17. OBJECTIVE × INVESTMENT
# ==============================================================================

def analyze_objective_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    working = attach_respondent_attribute(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "objective"
    )

    if working.empty:
        return pd.DataFrame()

    return analyze_segment_investment(
        working,
        respondent_columns.get("objective"),
        investment_columns.get("type"),
        investment_columns.get("id"),
        investment_columns.get("rank")
    )


# ==============================================================================
# 18. FEMALE INVESTMENT ANALYSIS
# ==============================================================================

def analyze_female_preference(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    working = attach_respondent_attribute(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "gender"
    )

    if working.empty:
        return pd.DataFrame()

    gender_column = respondent_columns.get("gender")
    type_column = investment_columns.get("type")
    id_column = investment_columns.get("id")
    rank_column = investment_columns.get("rank")

    if not all(
        [
            gender_column,
            type_column,
            id_column,
            rank_column
        ]
    ):
        return pd.DataFrame()

    gender_values = normalize_text(
        working[gender_column]
    ).str.lower()

    female_df = working[
        gender_values.eq("female")
    ].copy()

    if female_df.empty:
        return pd.DataFrame()

    result = (

        female_df

        .dropna(
            subset=[
                type_column,
                rank_column
            ]
        )

        .groupby(
            type_column,
            as_index=False
        )

        .agg(

            Female_Respondents=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            )
        )
    )

    result[
        "Female_Preference_Rank"
    ] = (

        result[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return (
        result
        .sort_values(
            [
                "Female_Preference_Rank",
                "Average_Preference_Rank"
            ]
        )
        .reset_index(drop=True)
    )


# ==============================================================================
# 19. YOUNG INVESTOR ANALYSIS
# ==============================================================================

def analyze_young_investors(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):
    """
    Analyze investment preferences among investors under 30.

    Business Rule:

        Age < 30 = Young Investor

    Preference Rule:

        Lower Average_Preference_Rank
        =
        Stronger Preference
    """

    respondent_id = respondent_columns.get("id")
    age_column = respondent_columns.get("age")

    investment_id = investment_columns.get("id")
    type_column = investment_columns.get("type")
    rank_column = investment_columns.get("rank")

    if not all(
        [
            respondent_id,
            age_column,
            investment_id,
            type_column,
            rank_column
        ]
    ):
        return pd.DataFrame()

    respondent_lookup = (
        respondent_df[
            [
                respondent_id,
                age_column
            ]
        ]
        .drop_duplicates(
            subset=[respondent_id]
        )
        .copy()
    )

    respondent_lookup[age_column] = pd.to_numeric(
        respondent_lookup[age_column],
        errors="coerce"
    )

    young_respondents = respondent_lookup[
        respondent_lookup[age_column] < 30
    ].copy()

    if young_respondents.empty:
        return pd.DataFrame()

    working = investment_df.merge(
        young_respondents,
        left_on=investment_id,
        right_on=respondent_id,
        how="inner"
    )

    working = working.dropna(
        subset=[
            type_column,
            rank_column
        ]
    )

    if working.empty:
        return pd.DataFrame()

    result = (

        working

        .groupby(
            type_column,
            as_index=False
        )

        .agg(

            Young_Investor_Count=(
                investment_id,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            )
        )
    )

    result[
        "Young_Preference_Rank"
    ] = (

        result[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return (
        result

        .sort_values(
            [
                "Young_Preference_Rank",
                "Average_Preference_Rank"
            ]
        )

        .reset_index(drop=True)
    )


# ==============================================================================
# 20. BOND ANALYSIS
# ==============================================================================

def analyze_bond_preference(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):
    """
    Analyze bond preference across respondent-level dimensions.

    Bond rows are identified from Investment_Type.

    Respondent-level dimensions are attached through Respondent_ID.
    """

    type_column = investment_columns.get("type")
    rank_column = investment_columns.get("rank")
    id_column = investment_columns.get("id")

    if not all(
        [
            type_column,
            rank_column,
            id_column
        ]
    ):
        return pd.DataFrame()

    type_values = normalize_text(
        investment_df[type_column]
    ).str.lower()

    bond_mask = (
        type_values.str.contains(
            "bond",
            na=False
        )
    )

    bond_df = investment_df[
        bond_mask
    ].copy()

    if bond_df.empty:
        return pd.DataFrame()

    dimensions = [
        "gender",
        "age_group",
        "objective"
    ]

    available_dimensions = [
        dimension
        for dimension in dimensions
        if respondent_columns.get(dimension) is not None
    ]

    if not available_dimensions:
        return pd.DataFrame()

    working = attach_respondent_attributes(
        respondent_df,
        bond_df,
        respondent_columns,
        investment_columns,
        available_dimensions
    )

    if working.empty:
        return pd.DataFrame()

    dimension_columns = [
        respondent_columns[dimension]
        for dimension in available_dimensions
    ]

    result = (

        working

        .dropna(
            subset=dimension_columns + [rank_column]
        )

        .groupby(
            dimension_columns,
            as_index=False
        )

        .agg(

            Unique_Respondents=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            )
        )
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return result


# ==============================================================================
# 21. GENERIC RESPONDENT ATTRIBUTE × INVESTMENT
# ==============================================================================

def analyze_category_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns,
    respondent_category
):
    """
    Correctly connects respondent-level attributes to
    the unpivoted investment table.

    Examples:

        Purpose × Investment
        Factor × Investment
        Duration × Investment
        Expected Return × Investment
        Savings Objective × Investment
        Information Source × Investment
        Monitoring × Investment
    """

    category_column = respondent_columns.get(
        respondent_category
    )

    respondent_id = respondent_columns.get(
        "id"
    )

    investment_id = investment_columns.get(
        "id"
    )

    type_column = investment_columns.get(
        "type"
    )

    rank_column = investment_columns.get(
        "rank"
    )

    if not all(
        [
            category_column,
            respondent_id,
            investment_id,
            type_column,
            rank_column
        ]
    ):

        return pd.DataFrame()

    working = attach_respondent_attribute(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        respondent_category
    )

    if working.empty:
        return pd.DataFrame()

    working = working.dropna(
        subset=[
            category_column,
            type_column,
            rank_column
        ]
    )

    if working.empty:
        return pd.DataFrame()

    result = (

        working

        .groupby(
            [
                category_column,
                type_column
            ],
            as_index=False
        )

        .agg(

            Unique_Respondents=(
                investment_id,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            )
        )
    )

    result[
        "Category_Preference_Rank"
    ] = (

        result

        .groupby(
            category_column
        )[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return result


# ==============================================================================
# 22. PURPOSE × INVESTMENT
# ==============================================================================

def analyze_purpose_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "purpose"
    )


# ==============================================================================
# 23. FACTOR × INVESTMENT
# ==============================================================================

def analyze_factor_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "factor"
    )


# ==============================================================================
# 24. DURATION × INVESTMENT
# ==============================================================================

def analyze_duration_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "duration"
    )


# ==============================================================================
# 25. SAVINGS OBJECTIVE × INVESTMENT
# ==============================================================================

def analyze_savings_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "savings"
    )


# ==============================================================================
# 26. INFORMATION SOURCE × INVESTMENT
# ==============================================================================

def analyze_source_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "source"
    )


# ==============================================================================
# 27. MONITORING × INVESTMENT
# ==============================================================================

def analyze_monitoring_investment(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "monitoring"
    )


# ==============================================================================
# 28. EXPECTED RETURN × INVESTMENT
# ==============================================================================

def analyze_expected_return(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):
    """
    Expected return remains categorical.

    NO artificial numeric conversion is performed.

    Examples:

        10%-20%
        20%-30%
        30%-40%
    """

    return analyze_category_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns,
        "expected"
    )


# ==============================================================================
# 29. CATEGORY PREFERENCE SUMMARY
# ==============================================================================

def create_preference_summary(
    dataframe,
    category_column
):
    """
    Creates a category-level summary.

    This summarizes average preference rank across
    investment types within each category.

    Lower average rank = stronger preference.
    """

    if dataframe.empty:
        return pd.DataFrame()

    if category_column not in dataframe.columns:
        return pd.DataFrame()

    if "Average_Preference_Rank" not in dataframe.columns:
        return pd.DataFrame()

    result = (

        dataframe

        .groupby(
            category_column,
            as_index=False
        )

        .agg(

            Average_Preference_Rank=(
                "Average_Preference_Rank",
                "mean"
            )
        )
    )

    result[
        "Preference_Rank"
    ] = (

        result[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    result[
        "Average_Preference_Rank"
    ] = (
        result[
            "Average_Preference_Rank"
        ]
        .round(2)
    )

    return (
        result

        .sort_values(
            [
                "Preference_Rank",
                "Average_Preference_Rank"
            ]
        )

        .reset_index(drop=True)
    )


# ==============================================================================
# 30. GENDER PREFERENCE GAP
# ==============================================================================

def calculate_gender_gap(
    gender_analysis,
    respondent_columns,
    investment_columns
):
    """
    Calculates Female vs Male preference rank gap.

    Interpretation:

        Female_Male_Rank_Gap < 0
            Female preference is stronger.

        Female_Male_Rank_Gap > 0
            Male preference is stronger.

    Because lower rank = stronger preference.
    """

    if gender_analysis.empty:
        return pd.DataFrame()

    gender_column = respondent_columns.get(
        "gender"
    )

    type_column = investment_columns.get(
        "type"
    )

    if not gender_column or not type_column:
        return pd.DataFrame()

    if (
        gender_column not in gender_analysis.columns
        or
        type_column not in gender_analysis.columns
    ):
        return pd.DataFrame()

    pivot = (

        gender_analysis

        .pivot_table(
            index=type_column,
            columns=gender_column,
            values="Average_Preference_Rank",
            aggfunc="mean"
        )

        .reset_index()
    )

    # Normalize gender column names.

    normalized_gender = {
        str(column).strip().lower(): column
        for column in pivot.columns
    }

    male_column = normalized_gender.get(
        "male"
    )

    female_column = normalized_gender.get(
        "female"
    )

    if male_column is None:
        pivot["Male"] = np.nan
        male_column = "Male"

    if female_column is None:
        pivot["Female"] = np.nan
        female_column = "Female"

    if male_column != "Male":

        pivot = pivot.rename(
            columns={
                male_column: "Male"
            }
        )

        male_column = "Male"

    if female_column != "Female":

        pivot = pivot.rename(
            columns={
                female_column: "Female"
            }
        )

        female_column = "Female"

    pivot[
        "Female_Male_Rank_Gap"
    ] = (
        pivot["Female"] -
        pivot["Male"]
    )

    pivot[
        "Absolute_Rank_Gap"
    ] = (
        pivot[
            "Female_Male_Rank_Gap"
        ]
        .abs()
    )

    return pivot


# ==============================================================================
# 31. EXECUTIVE INSIGHTS
# ==============================================================================

def generate_insights(
    overall,
    female_analysis,
    young_analysis,
    bond_analysis,
    gender_analysis,
    investment_columns
):

    insights = []

    type_column = investment_columns.get(
        "type"
    )

    # --------------------------------------------------------------------------
    # Overall
    # --------------------------------------------------------------------------

    if not overall.empty:

        top = overall.iloc[0]

        insights.append({

            "Insight_Category":
                "Overall Preference",

            "Finding":
                (
                    f"{top[type_column]} has the "
                    f"strongest overall preference "
                    f"with an average preference rank "
                    f"of {top['Average_Preference_Rank']:.2f}."
                ),

            "Interpretation":
                (
                    "Lower average preference rank "
                    "indicates stronger preference."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------------------------
    # Female
    # --------------------------------------------------------------------------

    if not female_analysis.empty:

        female_top = female_analysis.iloc[0]

        insights.append({

            "Insight_Category":
                "Female Investors",

            "Finding":
                (
                    f"{female_top[type_column]} is the "
                    f"highest-ranked investment among "
                    f"female respondents."
                ),

            "Interpretation":
                (
                    "Female respondents show their "
                    "strongest preference for this "
                    "investment."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------------------------
    # Young
    # --------------------------------------------------------------------------

    if not young_analysis.empty:

        young_top = young_analysis.iloc[0]

        insights.append({

            "Insight_Category":
                "Young Investors",

            "Finding":
                (
                    f"{young_top[type_column]} is the "
                    f"highest-ranked investment among "
                    f"investors under 30."
                ),

            "Interpretation":
                (
                    "Younger investors may have "
                    "different investment preferences "
                    "from the overall population."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------------------------
    # Gender comparison
    # --------------------------------------------------------------------------

    if not gender_analysis.empty:

        insights.append({

            "Insight_Category":
                "Gender Comparison",

            "Finding":
                (
                    "Investment preferences vary "
                    "across gender segments and can "
                    "be evaluated using average "
                    "preference rank."
                ),

            "Interpretation":
                (
                    "Lower average rank represents "
                    "stronger preference."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------------------------
    # Bond analysis
    # --------------------------------------------------------------------------

    if not bond_analysis.empty:

        insights.append({

            "Insight_Category":
                "Bond Preference",

            "Finding":
                (
                    "Bond preference has been analyzed "
                    "across demographic segments."
                ),

            "Interpretation":
                (
                    "The analysis can identify segments "
                    "with relatively stronger bond "
                    "preference."
                ),

            "Priority":
                "Medium"
        })

    return pd.DataFrame(
        insights
    )


# ==============================================================================
# 32. RECOMMENDATIONS
# ==============================================================================

def generate_recommendations(
    overall,
    female_analysis,
    young_analysis,
    bond_analysis,
    investment_columns
):

    recommendations = []

    type_column = investment_columns.get(
        "type"
    )

    # --------------------------------------------------------------------------
    # Recommendation 1
    # --------------------------------------------------------------------------

    if not overall.empty:

        top = overall.iloc[0]

        recommendations.append({

            "Recommendation_ID":
                "REC-001",

            "Area":
                "Product Strategy",

            "Recommendation":
                (
                    f"Prioritize {top[type_column]} "
                    "in investor-facing campaigns "
                    "because it demonstrates the "
                    "strongest overall preference."
                ),

            "Business_Rationale":
                (
                    "The recommendation is based on "
                    "the lowest average preference rank."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------------------------
    # Recommendation 2
    # --------------------------------------------------------------------------

    if not female_analysis.empty:

        top_female = female_analysis.iloc[0]

        recommendations.append({

            "Recommendation_ID":
                "REC-002",

            "Area":
                "Female Investor Strategy",

            "Recommendation":
                (
                    f"Develop targeted communication "
                    f"around {top_female[type_column]} "
                    "for female investor segments."
                ),

            "Business_Rationale":
                (
                    "This investment has the strongest "
                    "average preference among female "
                    "respondents."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------------------------
    # Recommendation 3
    # --------------------------------------------------------------------------

    if not young_analysis.empty:

        top_young = young_analysis.iloc[0]

        recommendations.append({

            "Recommendation_ID":
                "REC-003",

            "Area":
                "Young Investor Strategy",

            "Recommendation":
                (
                    f"Create digitally focused "
                    f"investment education and "
                    f"marketing around "
                    f"{top_young[type_column]} "
                    "for investors under 30."
                ),

            "Business_Rationale":
                (
                    "This investment has the strongest "
                    "preference among younger investors."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------------------------
    # Recommendation 4
    # --------------------------------------------------------------------------

    if not bond_analysis.empty:

        recommendations.append({

            "Recommendation_ID":
                "REC-004",

            "Area":
                "Fixed Income Strategy",

            "Recommendation":
                (
                    "Identify demographic segments "
                    "with comparatively stronger bond "
                    "preference and create targeted "
                    "fixed-income communication."
                ),

            "Business_Rationale":
                (
                    "Bond preference should be evaluated "
                    "by segment rather than assuming one "
                    "universal customer profile."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------------------------
    # Recommendation 5
    # --------------------------------------------------------------------------

    recommendations.append({

        "Recommendation_ID":
            "REC-005",

        "Area":
            "Data-Driven Marketing",

        "Recommendation":
            (
                "Use demographic and behavioural "
                "segmentation instead of treating "
                "all investors as a single customer group."
            ),

        "Business_Rationale":
            (
                "Investment preferences can differ "
                "by gender, age, objectives and "
                "behavioural characteristics."
            ),

        "Priority":
            "High"
    })

    return pd.DataFrame(
        recommendations
    )


# ==============================================================================
# 33. ANALYSIS SUMMARY
# ==============================================================================

def create_analysis_summary(
    respondent_df,
    investment_df,
    overall,
    female_analysis,
    young_analysis,
    bond_analysis,
    respondent_columns,
    investment_columns
):

    respondent_id = respondent_columns.get(
        "id"
    )

    type_column = investment_columns.get(
        "type"
    )

    summary = {

        "Total_Respondent_Rows":
            len(respondent_df),

        "Unique_Respondents":
            (
                respondent_df[
                    respondent_id
                ].nunique()
                if respondent_id
                else 0
            ),

        "Investment_Rows":
            len(investment_df),

        "Investment_Types_Analyzed":
            (
                investment_df[
                    type_column
                ].nunique()
                if type_column
                else 0
            ),

        "Female_Analysis_Available":
            not female_analysis.empty,

        "Young_Investor_Analysis_Available":
            not young_analysis.empty,

        "Bond_Analysis_Available":
            not bond_analysis.empty,

        "Overall_Preference_Analysis_Available":
            not overall.empty
    }

    return pd.DataFrame(
        [summary]
    )


# ==============================================================================
# 34. SAVE OUTPUT
# ==============================================================================

def save_output(
    dataframe,
    key
):

    if key not in OUTPUTS:

        print(
            f"  ! Unknown output key: {key}"
        )

        return

    path = OUTPUTS[key]

    if dataframe is None:
        dataframe = pd.DataFrame()

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"  ✓ {path.name}"
    )


# ==============================================================================
# 35. PRINT OVERALL RANKING
# ==============================================================================

def print_ranking(
    overall,
    type_column
):

    print("\n")
    print("=" * 80)
    print("OVERALL INVESTMENT PREFERENCE")
    print("=" * 80)

    if overall.empty:

        print(
            "No investment preference data available."
        )

        return

    display_columns = [

        type_column,

        "Unique_Respondents",

        "Average_Preference_Rank",

        "Overall_Preference_Rank"
    ]

    display_columns = [

        column

        for column in display_columns

        if column in overall.columns
    ]

    print(
        overall[
            display_columns
        ].to_string(
            index=False
        )
    )

    print(
        "\nNOTE: Lower Average_Preference_Rank "
        "means stronger preference."
    )


# ==============================================================================
# 36. PRINT BUSINESS QUESTIONS
# ==============================================================================

def print_business_questions(
    female_analysis,
    young_analysis,
    bond_analysis,
    type_column
):

    print("\n")
    print("=" * 80)
    print("KEY BUSINESS QUESTIONS")
    print("=" * 80)

    # ==========================================================================
    # FEMALE → GOLD
    # ==========================================================================

    print(
        "\n1. Do females prefer Gold?"
    )

    if female_analysis.empty:

        print(
            "   Female analysis unavailable."
        )

    else:

        values = normalize_text(
            female_analysis[
                type_column
            ]
        ).str.lower()

        gold = female_analysis[
            values.eq("gold")
        ]

        if gold.empty:

            print(
                "   Gold is not available in "
                "the female analysis."
            )

        else:

            gold_rank = gold.iloc[0][
                "Average_Preference_Rank"
            ]

            top = female_analysis.iloc[0][
                type_column
            ]

            print(
                f"   Female Gold average rank : "
                f"{gold_rank}"
            )

            print(
                f"   Female top investment     : "
                f"{top}"
            )

            if (
                str(top)
                .strip()
                .lower()
                == "gold"
            ):

                print(
                    "   Result: YES — Gold has the "
                    "strongest female preference."
                )

            else:

                print(
                    "   Result: NO — another investment "
                    "has stronger female preference."
                )

    # ==========================================================================
    # YOUNG → EQUITY
    # ==========================================================================

    print(
        "\n2. Do younger investors prefer Equity?"
    )

    if young_analysis.empty:

        print(
            "   Young investor analysis unavailable."
        )

    else:

        values = normalize_text(
            young_analysis[
                type_column
            ]
        ).str.lower()

        equity = young_analysis[
            values.eq("equity")
        ]

        top = young_analysis.iloc[0][
            type_column
        ]

        print(
            f"   Young top investment : {top}"
        )

        if equity.empty:

            print(
                "   Equity data is not available."
            )

        else:

            equity_rank = equity.iloc[0][
                "Average_Preference_Rank"
            ]

            print(
                f"   Young Equity average rank : "
                f"{equity_rank}"
            )

            if (
                str(top)
                .strip()
                .lower()
                == "equity"
            ):

                print(
                    "   Result: YES"
                )

            else:

                print(
                    "   Result: NO"
                )

    # ==========================================================================
    # BONDS
    # ==========================================================================

    print(
        "\n3. Who prefers Bonds?"
    )

    if bond_analysis.empty:

        print(
            "   Bond analysis unavailable."
        )

    else:

        print(
            bond_analysis.to_string(
                index=False
            )
        )


# ==============================================================================
# 37. MAIN
# ==============================================================================

def main():

    print("=" * 80)
    print("INVESTMENT SURVEY — ADVANCED ANALYSIS")
    print("=" * 80)

    # ==========================================================================
    # STEP 1 — LOAD DATA
    # ==========================================================================

    respondent_df, investment_df = load_data()

    # ==========================================================================
    # STEP 2 — IDENTIFY COLUMNS
    # ==========================================================================

    (
        respondent_columns,
        investment_columns
    ) = identify_columns(
        respondent_df,
        investment_df
    )

    print("\nDetected respondent columns:")

    for key, value in respondent_columns.items():

        print(
            f"  {key:<20} : {value}"
        )

    print("\nDetected investment columns:")

    for key, value in investment_columns.items():

        print(
            f"  {key:<20} : {value}"
        )

    # ==========================================================================
    # STEP 3 — VALIDATE REQUIRED COLUMNS
    # ==========================================================================

    required_respondent = [
        "id"
    ]

    required_investment = [
        "id",
        "type",
        "rank"
    ]

    missing_respondent = [

        key

        for key in required_respondent

        if respondent_columns.get(key) is None
    ]

    missing_investment = [

        key

        for key in required_investment

        if investment_columns.get(key) is None
    ]

    if missing_respondent:

        raise ValueError(
            "\nMissing required respondent columns:\n"
            f"{missing_respondent}\n\n"
            "Available respondent columns:\n"
            f"{list(respondent_df.columns)}"
        )

    if missing_investment:

        raise ValueError(
            "\nMissing required investment columns:\n"
            f"{missing_investment}\n\n"
            "Available investment columns:\n"
            f"{list(investment_df.columns)}"
        )

    # ==========================================================================
    # STEP 4 — PREPARE INVESTMENT DATA
    # ==========================================================================

    investment_df = prepare_investment_data(
        investment_df,
        investment_columns
    )

    # ==========================================================================
    # STEP 5 — OVERALL PREFERENCE
    # ==========================================================================

    overall = analyze_overall_preference(
        investment_df,
        investment_columns
    )

    # ==========================================================================
    # STEP 6 — GENDER
    # ==========================================================================

    gender_analysis = analyze_gender_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 7 — AGE
    # ==========================================================================

    age_analysis = analyze_age_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 8 — OBJECTIVE
    # ==========================================================================

    objective_analysis = analyze_objective_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 9 — FEMALE
    # ==========================================================================

    female_analysis = analyze_female_preference(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 10 — YOUNG INVESTORS
    # ==========================================================================

    young_analysis = analyze_young_investors(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 11 — BONDS
    # ==========================================================================

    bond_analysis = analyze_bond_preference(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 12 — PURPOSE
    # ==========================================================================

    purpose_analysis = analyze_purpose_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 13 — FACTOR
    # ==========================================================================

    factor_analysis = analyze_factor_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 14 — DURATION
    # ==========================================================================

    duration_analysis = analyze_duration_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 15 — EXPECTED RETURN
    # ==========================================================================

    expected_return_analysis = analyze_expected_return(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 16 — SAVINGS
    # ==========================================================================

    savings_analysis = analyze_savings_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 17 — INFORMATION SOURCE
    # ==========================================================================

    source_analysis = analyze_source_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 18 — MONITORING
    # ==========================================================================

    monitoring_analysis = analyze_monitoring_investment(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 19 — GENDER GAP
    # ==========================================================================

    gender_gap = calculate_gender_gap(
        gender_analysis,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 20 — CATEGORY SUMMARIES
    # ==========================================================================

    gender_column = respondent_columns.get(
        "gender"
    )

    age_column = respondent_columns.get(
        "age_group"
    )

    objective_column = respondent_columns.get(
        "objective"
    )

    if gender_column is not None:

        gender_preference_summary = (
            create_preference_summary(
                gender_analysis,
                gender_column
            )
        )

    else:

        gender_preference_summary = pd.DataFrame()

    if age_column is not None:

        age_preference_summary = (
            create_preference_summary(
                age_analysis,
                age_column
            )
        )

    else:

        age_preference_summary = pd.DataFrame()

    if objective_column is not None:

        objective_preference_summary = (
            create_preference_summary(
                objective_analysis,
                objective_column
            )
        )

    else:

        objective_preference_summary = pd.DataFrame()

    # ==========================================================================
    # STEP 21 — EXECUTIVE INSIGHTS
    # ==========================================================================

    insights = generate_insights(
        overall,
        female_analysis,
        young_analysis,
        bond_analysis,
        gender_analysis,
        investment_columns
    )

    # ==========================================================================
    # STEP 22 — RECOMMENDATIONS
    # ==========================================================================

    recommendations = generate_recommendations(
        overall,
        female_analysis,
        young_analysis,
        bond_analysis,
        investment_columns
    )

    # ==========================================================================
    # STEP 23 — SUMMARY
    # ==========================================================================

    analysis_summary = create_analysis_summary(
        respondent_df,
        investment_df,
        overall,
        female_analysis,
        young_analysis,
        bond_analysis,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 24 — SAVE OUTPUTS
    # ==========================================================================

    print("\n")
    print("=" * 80)
    print("SAVING ANALYTICAL OUTPUTS")
    print("=" * 80)

    save_output(
        overall,
        "investment_analysis"
    )

    save_output(
        gender_analysis,
        "gender_analysis"
    )

    save_output(
        age_analysis,
        "age_analysis"
    )

    save_output(
        objective_analysis,
        "objective_analysis"
    )

    save_output(
        female_analysis,
        "female_analysis"
    )

    save_output(
        young_analysis,
        "young_analysis"
    )

    save_output(
        bond_analysis,
        "bond_analysis"
    )

    save_output(
        gender_preference_summary,
        "gender_preference_summary"
    )

    save_output(
        age_preference_summary,
        "age_preference_summary"
    )

    save_output(
        objective_preference_summary,
        "objective_preference_summary"
    )

    save_output(
        purpose_analysis,
        "purpose_analysis"
    )

    save_output(
        factor_analysis,
        "factor_analysis"
    )

    save_output(
        duration_analysis,
        "duration_analysis"
    )

    save_output(
        expected_return_analysis,
        "expected_return_analysis"
    )

    save_output(
        savings_analysis,
        "savings_analysis"
    )

    save_output(
        source_analysis,
        "source_analysis"
    )

    save_output(
        monitoring_analysis,
        "monitoring_analysis"
    )

    save_output(
        gender_gap,
        "gender_gap"
    )

    save_output(
        insights,
        "executive_insights"
    )

    save_output(
        recommendations,
        "recommendations"
    )

    save_output(
        analysis_summary,
        "analysis_summary"
    )

    # ==========================================================================
    # STEP 25 — CONSOLE REPORT
    # ==========================================================================

    type_column = investment_columns[
        "type"
    ]

    print_ranking(
        overall,
        type_column
    )

    print_business_questions(
        female_analysis,
        young_analysis,
        bond_analysis,
        type_column
    )

    # ==========================================================================
    # FINAL
    # ==========================================================================

    print("\n")
    print("=" * 80)
    print("07_analysis.py COMPLETED SUCCESSFULLY")
    print("=" * 80)

    print(
        f"\nAnalysis files saved to:\n"
        f"{ANALYSIS_DIR}"
    )


# ==============================================================================
# 38. ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    main()