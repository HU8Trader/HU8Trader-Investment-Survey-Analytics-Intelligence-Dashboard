"""
06_business_metrics.py
============================================================

Investment Survey Analytics Project

Purpose
-------
This module converts the feature-engineered investment survey
data into business-ready analytical metrics.

Pipeline position
-----------------
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
07_visualization.py
        ↓
08_dashboard.py

IMPORTANT BUSINESS RULE
-----------------------
Preference Rank:

    1 = Highest Preference
    7 = Lowest Preference

Therefore:

    LOWER Average Preference Rank
    =
    STRONGER Investment Preference

Expected Return
---------------
The original survey contains categorical ranges such as:

    10%-20%
    20%-30%
    30%-40%

Therefore we DO NOT calculate an artificial numeric
"Average Expected Return".

Instead we calculate:

    Most Common Expected Return Range
    Expected Return Distribution

============================================================
"""


# ============================================================
# 1. IMPORTS
# ============================================================

from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# 2. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURES_DIR = PROJECT_ROOT / "data" / "features"

METRICS_DIR = PROJECT_ROOT / "data" / "metrics"

METRICS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. INPUT FILES
# ============================================================

RESPONDENT_FEATURE_FILE = (
    FEATURES_DIR / "respondent_features.csv"
)

INVESTMENT_FEATURE_FILE = (
    FEATURES_DIR / "investment_features.csv"
)


# ============================================================
# 4. OUTPUT FILES
# ============================================================

BUSINESS_METRICS_FILE = (
    METRICS_DIR / "business_metrics_summary.csv"
)

INVESTMENT_METRICS_FILE = (
    METRICS_DIR / "investment_metrics.csv"
)

DEMOGRAPHIC_METRICS_FILE = (
    METRICS_DIR / "demographic_metrics.csv"
)

BUSINESS_INSIGHTS_FILE = (
    METRICS_DIR / "business_insights.csv"
)

INVESTMENT_POPULARITY_FILE = (
    METRICS_DIR / "investment_popularity.csv"
)

EXPECTED_RETURN_FILE = (
    METRICS_DIR / "expected_return_distribution.csv"
)

DURATION_FILE = (
    METRICS_DIR / "duration_distribution.csv"
)

PURPOSE_FILE = (
    METRICS_DIR / "purpose_distribution.csv"
)

FACTOR_FILE = (
    METRICS_DIR / "decision_factor_distribution.csv"
)

SAVINGS_FILE = (
    METRICS_DIR / "savings_objective_distribution.csv"
)

SOURCE_FILE = (
    METRICS_DIR / "information_source_distribution.csv"
)

MONITORING_FILE = (
    METRICS_DIR / "monitoring_frequency_distribution.csv"
)


# ============================================================
# 5. HELPER — FIND COLUMN
# ============================================================

def find_column(df, candidates):
    """
    Find the first matching column from a list of possible names.

    This makes the pipeline more robust to minor naming differences.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = candidate.strip().lower()

        if key in normalized:

            return normalized[key]

    return None


# ============================================================
# 6. LOAD FEATURE DATA
# ============================================================

def load_feature_data():

    print("\nLoading feature-engineered data...")

    if not RESPONDENT_FEATURE_FILE.exists():

        raise FileNotFoundError(
            "\nRespondent feature file not found:\n"
            f"{RESPONDENT_FEATURE_FILE}\n\n"
            "Run 05_feature_engineering.py first."
        )

    if not INVESTMENT_FEATURE_FILE.exists():

        raise FileNotFoundError(
            "\nInvestment feature file not found:\n"
            f"{INVESTMENT_FEATURE_FILE}\n\n"
            "Run 05_feature_engineering.py first."
        )

    respondent_df = pd.read_csv(
        RESPONDENT_FEATURE_FILE
    )

    investment_df = pd.read_csv(
        INVESTMENT_FEATURE_FILE
    )

    print(
        f"Respondent rows : {len(respondent_df):,}"
    )

    print(
        f"Investment rows : {len(investment_df):,}"
    )

    return respondent_df, investment_df


# ============================================================
# 7. IDENTIFY RESPONDENT ID
# ============================================================

def get_respondent_id_column(df):

    candidates = [
        "Respondent_ID",
        "respondent_id",
        "Response_ID",
        "response_id",
        "ID",
        "id"
    ]

    column = find_column(
        df,
        candidates
    )

    if column is None:

        raise ValueError(
            "\nCould not find Respondent ID column.\n"
            f"Available columns:\n{list(df.columns)}"
        )

    return column


# ============================================================
# 8. IDENTIFY IMPORTANT COLUMNS
# ============================================================

def get_column_map(
    respondent_df,
    investment_df
):

    respondent_columns = {

        "id": get_respondent_id_column(
            respondent_df
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

        "source": find_column(
            respondent_df,
            [
                "Information_Source",
                "information_source",
                "Source",
                "source"
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

        "expected_return": find_column(
            respondent_df,
            [
                "Expected_Return_Range",
                "expected_return_range",
                "Expected Return",
                "Expected_Return",
                "expected_return",
                "Expected"
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
        )
    }

    investment_columns = {

        "id": get_respondent_id_column(
            investment_df
        ),

        "investment_type": find_column(
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
        ),

        "gender": find_column(
            investment_df,
            [
                "Gender",
                "gender"
            ]
        ),

        "age_group": find_column(
            investment_df,
            [
                "Age_Group",
                "age_group",
                "Age Group"
            ]
        ),

        "objective": find_column(
            investment_df,
            [
                "Investment_Objective",
                "investment_objective",
                "Objective"
            ]
        ),

        "age_segment": find_column(
            investment_df,
            [
                "Investor_Age_Segment",
                "investor_age_segment",
                "Age_Segment"
            ]
        ),

        "is_highest": find_column(
            investment_df,
            [
                "Is_Highest_Preference",
                "is_highest_preference"
            ]
        ),

        "is_top3": find_column(
            investment_df,
            [
                "Is_Top_3_Preference",
                "is_top_3_preference"
            ]
        )
    }

    return (
        respondent_columns,
        investment_columns
    )


# ============================================================
# 9. VALIDATE REQUIRED COLUMNS
# ============================================================

def validate_required_columns(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    required_respondent = [
        "id"
    ]

    required_investment = [
        "id",
        "investment_type",
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
            "Missing required respondent columns: "
            f"{missing_respondent}\n"
            f"Available columns: "
            f"{list(respondent_df.columns)}"
        )

    if missing_investment:

        raise ValueError(
            "Missing required investment columns: "
            f"{missing_investment}\n"
            f"Available columns: "
            f"{list(investment_df.columns)}"
        )


# ============================================================
# 10. NORMALIZE TEXT
# ============================================================

def normalize_text(series):

    return (

        series

        .astype("string")

        .str.strip()

        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA
            }
        )
    )


# ============================================================
# 11. MOST COMMON VALUE
# ============================================================

def most_common_value(
    df,
    column
):

    if column is None:
        return None

    if column not in df.columns:
        return None

    values = normalize_text(
        df[column]
    ).dropna()

    if values.empty:
        return None

    counts = (
        values
        .value_counts()
    )

    return counts.index[0]


# ============================================================
# 12. BASIC RESPONDENT KPIs
# ============================================================

def calculate_basic_kpis(
    respondent_df,
    columns
):

    metrics = {}

    id_column = columns["id"]

    # --------------------------------------------------------
    # Total Respondents
    # --------------------------------------------------------

    metrics[
        "Total Respondents"
    ] = int(
        respondent_df[
            id_column
        ].nunique()
    )

    # --------------------------------------------------------
    # Average Age
    # --------------------------------------------------------

    age_column = columns.get("age")

    if age_column is not None:

        age = pd.to_numeric(
            respondent_df[
                age_column
            ],
            errors="coerce"
        )

        metrics[
            "Average Investor Age"
        ] = round(
            age.mean(),
            2
        )

    else:

        metrics[
            "Average Investor Age"
        ] = np.nan

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    gender_column = columns.get("gender")

    if gender_column is not None:

        gender = normalize_text(
            respondent_df[
                gender_column
            ]
        ).str.lower()

        metrics[
            "Male Investors"
        ] = int(
            gender.eq("male").sum()
        )

        metrics[
            "Female Investors"
        ] = int(
            gender.eq("female").sum()
        )

    else:

        metrics[
            "Male Investors"
        ] = np.nan

        metrics[
            "Female Investors"
        ] = np.nan

    return metrics


# ============================================================
# 13. INVESTMENT PREFERENCE RANKING
# ============================================================

def calculate_preference_matrix(
    investment_df,
    columns
):

    """
    Main investment preference table.

    IMPORTANT:

        Lower average Preference Rank = stronger preference.

    Example:

        Mutual Fund = 2.15
        Equity      = 3.40
        Gold        = 5.98

    Result:

        Mutual Fund = Rank 1
        Equity      = Rank 2
        Gold        = Rank 3
    """

    id_column = columns["id"]

    type_column = columns["investment_type"]

    rank_column = columns["rank"]

    working = investment_df.copy()

    working[
        rank_column
    ] = pd.to_numeric(
        working[
            rank_column
        ],
        errors="coerce"
    )

    working = working.dropna(
        subset=[
            type_column,
            rank_column
        ]
    )

    ranking = (

        working

        .groupby(
            type_column,
            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank_column,
                "mean"
            ),

            Minimum_Preference_Rank=(
                rank_column,
                "min"
            ),

            Maximum_Preference_Rank=(
                rank_column,
                "max"
            )
        )
    )

    # --------------------------------------------------------
    # Preference Score
    # --------------------------------------------------------

    score_column = columns.get("score")

    if score_column is not None:

        working[
            score_column
        ] = pd.to_numeric(
            working[
                score_column
            ],
            errors="coerce"
        )

        score_summary = (

            working

            .groupby(
                type_column
            )

            .agg(
                Average_Preference_Score=(
                    score_column,
                    "mean"
                )
            )

            .reset_index()
        )

        ranking = ranking.merge(
            score_summary,
            on=type_column,
            how="left"
        )

    else:

        ranking[
            "Average_Preference_Score"
        ] = (
            8
            - ranking[
                "Average_Preference_Rank"
            ]
        )

    # --------------------------------------------------------
    # Highest preference count
    # --------------------------------------------------------

    if columns.get("is_highest") is not None:

        highest_column = columns[
            "is_highest"
        ]

        highest_summary = (

            working

            .groupby(
                type_column
            )

            .agg(
                Highest_Preference_Count=(
                    highest_column,
                    "sum"
                )
            )

            .reset_index()
        )

        ranking = ranking.merge(
            highest_summary,
            on=type_column,
            how="left"
        )

    else:

        ranking[
            "Highest_Preference_Count"
        ] = np.nan

    # --------------------------------------------------------
    # Top 3 count
    # --------------------------------------------------------

    if columns.get("is_top3") is not None:

        top3_column = columns[
            "is_top3"
        ]

        top3_summary = (

            working

            .groupby(
                type_column
            )

            .agg(
                Top_3_Preference_Count=(
                    top3_column,
                    "sum"
                )
            )

            .reset_index()
        )

        ranking = ranking.merge(
            top3_summary,
            on=type_column,
            how="left"
        )

    else:

        ranking[
            "Top_3_Preference_Count"
        ] = np.nan

    # --------------------------------------------------------
    # Overall Preference Rank
    # --------------------------------------------------------
    #
    # ASCENDING because lower average rank is better.

    ranking[
        "Overall_Preference_Rank"
    ] = (

        ranking[
            "Average_Preference_Rank"
        ]

        .rank(
            method="dense",
            ascending=True
        )

        .astype(int)
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    ranking = ranking.sort_values(
        [
            "Overall_Preference_Rank",
            "Average_Preference_Rank",
            type_column
        ],
        ascending=[
            True,
            True,
            True
        ]
    ).reset_index(
        drop=True
    )

    return ranking


# ============================================================
# 14. INVESTMENT POPULARITY
# ============================================================

def calculate_investment_popularity(
    investment_df,
    columns
):

    id_column = columns["id"]

    type_column = columns["investment_type"]

    popularity = (

        investment_df

        .groupby(
            type_column,
            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            )
        )

        .sort_values(
            "Respondent_Count",
            ascending=False
        )

        .reset_index(
            drop=True
        )
    )

    return popularity


# ============================================================
# 15. MOST / SECOND / LEAST PREFERRED
# ============================================================

def calculate_preference_kpis(
    ranking,
    type_column
):

    if ranking.empty:

        return {
            "Most Preferred Investment": None,
            "Second Most Preferred Investment": None,
            "Least Preferred Investment": None
        }

    return {

        "Most Preferred Investment":
            ranking.iloc[0][type_column],

        "Second Most Preferred Investment":
            ranking.iloc[1][type_column]
            if len(ranking) > 1
            else None,

        "Least Preferred Investment":
            ranking.iloc[-1][type_column]
    }


# ============================================================
# 16. BEHAVIOUR KPIs
# ============================================================

def calculate_behaviour_kpis(
    respondent_df,
    columns
):

    metrics = {}

    objective = columns.get(
        "objective"
    )

    purpose = columns.get(
        "purpose"
    )

    factor = columns.get(
        "factor"
    )

    duration = columns.get(
        "duration"
    )

    source = columns.get(
        "source"
    )

    savings = columns.get(
        "savings"
    )

    expected_return = columns.get(
        "expected_return"
    )

    metrics[
        "Most Common Investment Objective"
    ] = most_common_value(
        respondent_df,
        objective
    )

    metrics[
        "Most Common Investment Purpose"
    ] = most_common_value(
        respondent_df,
        purpose
    )

    metrics[
        "Most Important Decision Factor"
    ] = most_common_value(
        respondent_df,
        factor
    )

    metrics[
        "Most Common Investment Duration"
    ] = most_common_value(
        respondent_df,
        duration
    )

    metrics[
        "Most Trusted Information Source"
    ] = most_common_value(
        respondent_df,
        source
    )

    metrics[
        "Top Savings Objective"
    ] = most_common_value(
        respondent_df,
        savings
    )

    # --------------------------------------------------------
    # Expected Return
    # --------------------------------------------------------
    #
    # Categorical range only.
    #
    # No fake numerical average.

    metrics[
        "Most Common Expected Return Range"
    ] = most_common_value(
        respondent_df,
        expected_return
    )

    return metrics


# ============================================================
# 17. DISTRIBUTION TABLE
# ============================================================

def calculate_distribution(
    df,
    column,
    id_column
):

    if column is None:
        return pd.DataFrame()

    if column not in df.columns:
        return pd.DataFrame()

    result = (

        df

        .groupby(
            column,
            dropna=False,
            as_index=False
        )

        .agg(
            Respondent_Count=(
                id_column,
                "nunique"
            )
        )

        .sort_values(
            "Respondent_Count",
            ascending=False
        )
    )

    return result


# ============================================================
# 18. GENDER × INVESTMENT
# ============================================================

def calculate_gender_investment(
    investment_df,
    columns
):

    gender = columns.get("gender")

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    if gender is None:

        return pd.DataFrame()

    result = (

        investment_df

        .groupby(
            [
                gender,
                investment_type
            ],

            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank,
                "mean"
            )
        )
    )

    return result


# ============================================================
# 19. AGE GROUP × INVESTMENT
# ============================================================

def calculate_age_investment(
    investment_df,
    columns
):

    age_group = columns.get(
        "age_group"
    )

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    if age_group is None:

        return pd.DataFrame()

    result = (

        investment_df

        .groupby(
            [
                age_group,
                investment_type
            ],

            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank,
                "mean"
            )
        )
    )

    return result


# ============================================================
# 20. OBJECTIVE × INVESTMENT
# ============================================================

def calculate_objective_investment(
    investment_df,
    columns
):

    objective = columns.get(
        "objective"
    )

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    if objective is None:

        return pd.DataFrame()

    result = (

        investment_df

        .groupby(
            [
                objective,
                investment_type
            ],

            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank,
                "mean"
            )
        )
    )

    return result


# ============================================================
# 21. FEMALE INVESTMENT PREFERENCE
# ============================================================

def calculate_female_preference(
    investment_df,
    columns
):

    gender = columns.get(
        "gender"
    )

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    if gender is None:

        return pd.DataFrame()

    working = investment_df.copy()

    gender_values = normalize_text(
        working[gender]
    ).str.lower()

    working = working[
        gender_values.eq("female")
    ]

    if working.empty:

        return pd.DataFrame()

    result = (

        working

        .groupby(
            investment_type,
            as_index=False
        )

        .agg(

            Female_Respondents=(
                id_column,
                "nunique"
            ),

            Female_Average_Preference_Rank=(
                rank,
                "mean"
            )
        )

        .sort_values(
            "Female_Average_Preference_Rank",
            ascending=True
        )
    )

    return result


# ============================================================
# 22. YOUNG INVESTOR PREFERENCE
# ============================================================

def calculate_young_preference(
    investment_df,
    columns
):

    age_segment = columns.get(
        "age_segment"
    )

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    if age_segment is None:

        return pd.DataFrame()

    working = investment_df.copy()

    working = working[
        normalize_text(
            working[
                age_segment
            ]
        ).eq("Under 30")
    ]

    if working.empty:

        return pd.DataFrame()

    result = (

        working

        .groupby(
            investment_type,
            as_index=False
        )

        .agg(

            Young_Investor_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank,
                "mean"
            )
        )

        .sort_values(
            "Average_Preference_Rank",
            ascending=True
        )
    )

    return result


# ============================================================
# 23. BOND PREFERENCE
# ============================================================

def calculate_bond_preference(
    investment_df,
    columns
):

    investment_type = columns[
        "investment_type"
    ]

    rank = columns[
        "rank"
    ]

    id_column = columns[
        "id"
    ]

    bond_names = {
        "bond",
        "bonds",
        "government bond",
        "government bonds"
    }

    type_values = normalize_text(
        investment_df[
            investment_type
        ]
    )

    working = investment_df[
        type_values
        .str.lower()
        .isin(
            bond_names
        )
    ].copy()

    if working.empty:

        return pd.DataFrame()

    dimensions = []

    gender = columns.get(
        "gender"
    )

    age_group = columns.get(
        "age_group"
    )

    objective = columns.get(
        "objective"
    )

    if gender is not None:
        dimensions.append(gender)

    if age_group is not None:
        dimensions.append(age_group)

    if objective is not None:
        dimensions.append(objective)

    if not dimensions:

        return pd.DataFrame()

    result = (

        working

        .groupby(
            dimensions,
            as_index=False
        )

        .agg(

            Respondent_Count=(
                id_column,
                "nunique"
            ),

            Average_Preference_Rank=(
                rank,
                "mean"
            )
        )
    )

    return result


# ============================================================
# 24. EXPECTED RETURN DISTRIBUTION
# ============================================================

def calculate_expected_return_distribution(
    respondent_df,
    columns
):

    expected_return = columns.get(
        "expected_return"
    )

    id_column = columns[
        "id"
    ]

    result = calculate_distribution(
        respondent_df,
        expected_return,
        id_column
    )

    if result.empty:

        return result

    # --------------------------------------------------------
    # Extract lower bound where possible
    # --------------------------------------------------------

    result[
        "Return_Range_Lower_Bound"
    ] = (

        result[
            expected_return
        ]

        .astype("string")

        .str.extract(
            r"(\d+(?:\.\d+)?)"
        )[0]

        .astype(float)
    )

    result = result.sort_values(
        [
            "Return_Range_Lower_Bound",
            "Respondent_Count"
        ],
        ascending=[
            True,
            False
        ]
    )

    return result


# ============================================================
# 25. DURATION DISTRIBUTION
# ============================================================

def calculate_duration_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("duration"),
        columns["id"]
    )


# ============================================================
# 26. PURPOSE DISTRIBUTION
# ============================================================

def calculate_purpose_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("purpose"),
        columns["id"]
    )


# ============================================================
# 27. FACTOR DISTRIBUTION
# ============================================================

def calculate_factor_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("factor"),
        columns["id"]
    )


# ============================================================
# 28. SAVINGS DISTRIBUTION
# ============================================================

def calculate_savings_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("savings"),
        columns["id"]
    )


# ============================================================
# 29. INFORMATION SOURCE DISTRIBUTION
# ============================================================

def calculate_source_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("source"),
        columns["id"]
    )


# ============================================================
# 30. MONITORING FREQUENCY DISTRIBUTION
# ============================================================

def calculate_monitoring_distribution(
    respondent_df,
    columns
):

    return calculate_distribution(
        respondent_df,
        columns.get("monitoring"),
        columns["id"]
    )


# ============================================================
# 31. BUILD ALL EXECUTIVE KPIs
# ============================================================

def build_executive_kpis(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns,
    ranking
):

    kpis = {}

    # --------------------------------------------------------
    # Basic KPIs
    # --------------------------------------------------------

    kpis.update(
        calculate_basic_kpis(
            respondent_df,
            respondent_columns
        )
    )

    # --------------------------------------------------------
    # Investment Preference KPIs
    # --------------------------------------------------------

    investment_kpis = (
        calculate_preference_kpis(
            ranking,
            investment_columns[
                "investment_type"
            ]
        )
    )

    kpis.update(
        investment_kpis
    )

    # --------------------------------------------------------
    # Behaviour KPIs
    # --------------------------------------------------------

    behaviour_kpis = (
        calculate_behaviour_kpis(
            respondent_df,
            respondent_columns
        )
    )

    kpis.update(
        behaviour_kpis
    )

    return kpis


# ============================================================
# 32. EXECUTIVE KPI DATAFRAME
# ============================================================

def kpis_to_dataframe(kpis):

    rows = []

    for metric, value in kpis.items():

        rows.append({

            "Metric": metric,

            "Value": value

        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# 33. GENERATE BUSINESS INSIGHTS
# ============================================================

def generate_business_insights(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns,
    ranking,
    kpis
):

    insights = []

    investment_type = (
        investment_columns[
            "investment_type"
        ]
    )

    # --------------------------------------------------------
    # Investment Preference
    # --------------------------------------------------------

    if not ranking.empty:

        top = ranking.iloc[0]

        insights.append({

            "Insight_Type":
                "Investment Preference",

            "Insight":

                (
                    f"{top[investment_type]} has the "
                    f"strongest overall investment "
                    f"preference with an average "
                    f"preference rank of "
                    f"{top['Average_Preference_Rank']:.2f}. "
                    f"Lower rank indicates stronger preference."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------
    # Investment Objective
    # --------------------------------------------------------

    objective = kpis.get(
        "Most Common Investment Objective"
    )

    if objective:

        insights.append({

            "Insight_Type":
                "Investment Objective",

            "Insight":

                (
                    f"{objective} is the most common "
                    f"investment objective among the "
                    f"surveyed investors."
                ),

            "Priority":
                "High"
        })

    # --------------------------------------------------------
    # Information Source
    # --------------------------------------------------------

    source = kpis.get(
        "Most Trusted Information Source"
    )

    if source:

        insights.append({

            "Insight_Type":
                "Information Source",

            "Insight":

                (
                    f"{source} is the most frequently "
                    f"reported information source among "
                    f"survey respondents."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Investment Purpose
    # --------------------------------------------------------

    purpose = kpis.get(
        "Most Common Investment Purpose"
    )

    if purpose:

        insights.append({

            "Insight_Type":
                "Investment Purpose",

            "Insight":

                (
                    f"{purpose} is the most common "
                    f"reported investment purpose."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Decision Factor
    # --------------------------------------------------------

    factor = kpis.get(
        "Most Important Decision Factor"
    )

    if factor:

        insights.append({

            "Insight_Type":
                "Decision Factor",

            "Insight":

                (
                    f"{factor} is the leading reported "
                    f"decision factor influencing "
                    f"investment choices."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    duration = kpis.get(
        "Most Common Investment Duration"
    )

    if duration:

        insights.append({

            "Insight_Type":
                "Investment Horizon",

            "Insight":

                (
                    f"{duration} is the most common "
                    f"investment duration reported "
                    f"by respondents."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Expected Return
    # --------------------------------------------------------

    return_range = kpis.get(
        "Most Common Expected Return Range"
    )

    if return_range:

        insights.append({

            "Insight_Type":
                "Expected Return",

            "Insight":

                (
                    f"{return_range} is the most common "
                    f"expected-return range reported "
                    f"by respondents."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Female Preference
    # --------------------------------------------------------

    female = calculate_female_preference(
        investment_df,
        investment_columns
    )

    if not female.empty:

        top_female = female.iloc[0]

        insights.append({

            "Insight_Type":
                "Female Investment Preference",

            "Insight":

                (
                    f"Among female respondents, "
                    f"{top_female[investment_type]} "
                    f"has the strongest preference based "
                    f"on the lowest average preference rank "
                    f"of "
                    f"{top_female['Female_Average_Preference_Rank']:.2f}."
                ),

            "Priority":
                "Medium"
        })

    # --------------------------------------------------------
    # Young Investor Preference
    # --------------------------------------------------------

    young = calculate_young_preference(
        investment_df,
        investment_columns
    )

    if not young.empty:

        top_young = young.iloc[0]

        insights.append({

            "Insight_Type":
                "Young Investor Preference",

            "Insight":

                (
                    f"Among investors under 30, "
                    f"{top_young[investment_type]} "
                    f"has the strongest preference "
                    f"based on average preference rank."
                ),

            "Priority":
                "Medium"
        })

    return pd.DataFrame(
        insights
    )


# ============================================================
# 34. SAVE DATAFRAME
# ============================================================

def save_dataframe(
    dataframe,
    path
):

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8"
    )


# ============================================================
# 35. SAVE ALL OUTPUTS
# ============================================================

def save_outputs(
    executive_metrics,
    investment_metrics,
    demographic_metrics,
    insights,
    popularity,
    expected_return,
    duration,
    purpose,
    factor,
    savings,
    source,
    monitoring
):

    save_dataframe(
        executive_metrics,
        BUSINESS_METRICS_FILE
    )

    save_dataframe(
        investment_metrics,
        INVESTMENT_METRICS_FILE
    )

    save_dataframe(
        demographic_metrics,
        DEMOGRAPHIC_METRICS_FILE
    )

    save_dataframe(
        insights,
        BUSINESS_INSIGHTS_FILE
    )

    save_dataframe(
        popularity,
        INVESTMENT_POPULARITY_FILE
    )

    save_dataframe(
        expected_return,
        EXPECTED_RETURN_FILE
    )

    save_dataframe(
        duration,
        DURATION_FILE
    )

    save_dataframe(
        purpose,
        PURPOSE_FILE
    )

    save_dataframe(
        factor,
        FACTOR_FILE
    )

    save_dataframe(
        savings,
        SAVINGS_FILE
    )

    save_dataframe(
        source,
        SOURCE_FILE
    )

    save_dataframe(
        monitoring,
        MONITORING_FILE
    )

    print("\nOutput files created:")

    output_files = [

        BUSINESS_METRICS_FILE,

        INVESTMENT_METRICS_FILE,

        DEMOGRAPHIC_METRICS_FILE,

        BUSINESS_INSIGHTS_FILE,

        INVESTMENT_POPULARITY_FILE,

        EXPECTED_RETURN_FILE,

        DURATION_FILE,

        PURPOSE_FILE,

        FACTOR_FILE,

        SAVINGS_FILE,

        SOURCE_FILE,

        MONITORING_FILE
    ]

    for path in output_files:

        print(
            f"  ✓ {path}"
        )


# ============================================================
# 36. BUILD DEMOGRAPHIC METRICS
# ============================================================

def build_demographic_metrics(
    investment_df,
    investment_columns
):

    tables = []

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    gender = calculate_gender_investment(
        investment_df,
        investment_columns
    )

    if not gender.empty:

        temp = gender.copy()

        temp[
            "Analysis_Type"
        ] = "Gender × Investment"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    age = calculate_age_investment(
        investment_df,
        investment_columns
    )

    if not age.empty:

        temp = age.copy()

        temp[
            "Analysis_Type"
        ] = "Age Group × Investment"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Objective
    # --------------------------------------------------------

    objective = calculate_objective_investment(
        investment_df,
        investment_columns
    )

    if not objective.empty:

        temp = objective.copy()

        temp[
            "Analysis_Type"
        ] = "Objective × Investment"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Female
    # --------------------------------------------------------

    female = calculate_female_preference(
        investment_df,
        investment_columns
    )

    if not female.empty:

        temp = female.copy()

        temp[
            "Analysis_Type"
        ] = "Female Investment Preference"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Young
    # --------------------------------------------------------

    young = calculate_young_preference(
        investment_df,
        investment_columns
    )

    if not young.empty:

        temp = young.copy()

        temp[
            "Analysis_Type"
        ] = "Young Investor Preference"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Bonds
    # --------------------------------------------------------

    bonds = calculate_bond_preference(
        investment_df,
        investment_columns
    )

    if not bonds.empty:

        temp = bonds.copy()

        temp[
            "Analysis_Type"
        ] = "Bond Preference"

        tables.append(
            temp
        )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    if not tables:

        return pd.DataFrame()

    return pd.concat(
        tables,
        ignore_index=True,
        sort=False
    )


# ============================================================
# 37. PRINT EXECUTIVE REPORT
# ============================================================

def print_executive_report(
    kpis
):

    print("\n")
    print("=" * 80)
    print("EXECUTIVE KPI SUMMARY")
    print("=" * 80)

    for metric, value in kpis.items():

        print(
            f"{metric:<45} : {value}"
        )


# ============================================================
# 38. PRINT INVESTMENT RANKING
# ============================================================

def print_investment_ranking(
    ranking,
    investment_type
):

    print("\n")
    print("=" * 80)
    print("INVESTMENT PREFERENCE RANKING")
    print("=" * 80)

    if ranking.empty:

        print(
            "No investment ranking could be calculated."
        )

        return

    display_columns = [

        investment_type,

        "Respondent_Count",

        "Average_Preference_Rank",

        "Average_Preference_Score",

        "Overall_Preference_Rank"
    ]

    available_columns = [

        column

        for column in display_columns

        if column in ranking.columns
    ]

    print(
        ranking[
            available_columns
        ].to_string(
            index=False
        )
    )


# ============================================================
# 39. PRINT INSIGHTS
# ============================================================

def print_business_insights(
    insights
):

    print("\n")
    print("=" * 80)
    print("BUSINESS INSIGHTS")
    print("=" * 80)

    if insights.empty:

        print(
            "No business insights generated."
        )

        return

    for _, row in insights.iterrows():

        print(
            f"\n[{row['Priority']}] "
            f"{row['Insight_Type']}"
        )

        print(
            f"  {row['Insight']}"
        )


# ============================================================
# 40. MAIN
# ============================================================

def main():

    print("=" * 80)

    print(
        "INVESTMENT SURVEY — BUSINESS METRICS"
    )

    print("=" * 80)

    # ========================================================
    # STEP 1 — LOAD
    # ========================================================

    respondent_df, investment_df = (
        load_feature_data()
    )

    # ========================================================
    # STEP 2 — COLUMN MAPPING
    # ========================================================

    (
        respondent_columns,
        investment_columns
    ) = get_column_map(
        respondent_df,
        investment_df
    )

    print("\nDetected respondent columns:")

    for key, value in respondent_columns.items():

        print(
            f"  {key:<20}: {value}"
        )

    print("\nDetected investment columns:")

    for key, value in investment_columns.items():

        print(
            f"  {key:<20}: {value}"
        )

    # ========================================================
    # STEP 3 — VALIDATE
    # ========================================================

    validate_required_columns(

        respondent_df,

        investment_df,

        respondent_columns,

        investment_columns
    )

    # ========================================================
    # STEP 4 — INVESTMENT PREFERENCE RANKING
    # ========================================================

    ranking = calculate_preference_matrix(

        investment_df,

        investment_columns
    )

    investment_type = (
        investment_columns[
            "investment_type"
        ]
    )

    # ========================================================
    # STEP 5 — EXECUTIVE KPIs
    # ========================================================

    kpis = build_executive_kpis(

        respondent_df,

        investment_df,

        respondent_columns,

        investment_columns,

        ranking
    )

    executive_metrics = (
        kpis_to_dataframe(
            kpis
        )
    )

    # ========================================================
    # STEP 6 — INVESTMENT POPULARITY
    # ========================================================

    popularity = (
        calculate_investment_popularity(

            investment_df,

            investment_columns
        )
    )

    # ========================================================
    # STEP 7 — INVESTMENT METRICS
    # ========================================================

    investment_metrics = ranking.copy()

    # ========================================================
    # STEP 8 — DEMOGRAPHIC ANALYSIS
    # ========================================================

    demographic_metrics = (
        build_demographic_metrics(

            investment_df,

            investment_columns
        )
    )

    # ========================================================
    # STEP 9 — BEHAVIOUR DISTRIBUTIONS
    # ========================================================

    expected_return = (
        calculate_expected_return_distribution(

            respondent_df,

            respondent_columns
        )
    )

    duration = (
        calculate_duration_distribution(

            respondent_df,

            respondent_columns
        )
    )

    purpose = (
        calculate_purpose_distribution(

            respondent_df,

            respondent_columns
        )
    )

    factor = (
        calculate_factor_distribution(

            respondent_df,

            respondent_columns
        )
    )

    savings = (
        calculate_savings_distribution(

            respondent_df,

            respondent_columns
        )
    )

    source = (
        calculate_source_distribution(

            respondent_df,

            respondent_columns
        )
    )

    monitoring = (
        calculate_monitoring_distribution(

            respondent_df,

            respondent_columns
        )
    )

    # ========================================================
    # STEP 10 — BUSINESS INSIGHTS
    # ========================================================

    insights = generate_business_insights(

        respondent_df,

        investment_df,

        respondent_columns,

        investment_columns,

        ranking,

        kpis
    )

    # ========================================================
    # STEP 11 — SAVE
    # ========================================================

    save_outputs(

        executive_metrics,

        investment_metrics,

        demographic_metrics,

        insights,

        popularity,

        expected_return,

        duration,

        purpose,

        factor,

        savings,

        source,

        monitoring
    )

    # ========================================================
    # STEP 12 — CONSOLE REPORT
    # ========================================================

    print_executive_report(
        kpis
    )

    print_investment_ranking(

        ranking,

        investment_type
    )

    print_business_insights(
        insights
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print("\n")
    print("=" * 80)

    print(
        "BUSINESS METRICS PIPELINE COMPLETED SUCCESSFULLY"
    )

    print("=" * 80)


# ============================================================
# 41. ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()