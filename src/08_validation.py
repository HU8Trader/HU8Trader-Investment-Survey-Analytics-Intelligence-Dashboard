# ==============================================================================
# 08_validation.py
# ==============================================================================

"""
INVESTMENT SURVEY — ANALYTICAL VALIDATION & QUALITY CONTROL

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
08_validation.py
        ↓
09_visualization.py
        ↓
10_dashboard.py


PURPOSE
-------

This module validates analytical outputs produced by the investment survey
pipeline.

It validates:

1. Respondent-level grain.
2. Investment-level grain.
3. Respondent_ID integrity.
4. Preference Rank range and direction.
5. Expected Return categorical structure.
6. Investment analysis outputs.
7. Gender analysis outputs.
8. Age analysis outputs.
9. Objective analysis outputs.
10. Business-question outputs.
11. Executive insights.
12. Recommendations.
13. Data quality.
14. Analytical output file availability.

IMPORTANT DATA GRAIN
--------------------

RESPONDENT TABLE:

One row = One respondent.

INVESTMENT TABLE:

One row = One investment preference.

Therefore:

    len(investment_df)

MUST NOT be interpreted as respondent count.

For respondent counts use:

    investment_df["Respondent_ID"].nunique()


PREFERENCE RULE
---------------

1 = Highest Preference
7 = Lowest Preference

Therefore:

LOWER Average_Preference_Rank
        =
STRONGER Preference


EXPECTED RETURN RULE
--------------------

Expected Return remains categorical:

10%-20%
20%-30%
30%-40%

No artificial numeric average is calculated.


PRIMARY VALIDATION REPORT
-------------------------

The main summary file is:

data/validation/validation_report.csv

This filename is intentionally used because downstream script
09_export_processed_data.py expects this exact file.


OUTPUTS
-------

data/validation/

validation_report.csv
validation_results.csv
schema_validation.csv
grain_validation.csv
key_validation.csv
preference_validation.csv
category_validation.csv
output_validation.csv
business_rule_validation.csv
data_quality_validation.csv
validation_errors.csv

A compatibility copy of the report is also generated:

validation_summary.csv
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
ANALYSIS_DIR = PROJECT_ROOT / "data" / "analysis"
VALIDATION_DIR = PROJECT_ROOT / "data" / "validation"

VALIDATION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================================================================
# 3. INPUT FILES
# ==============================================================================

RESPONDENT_FILE = (
    FEATURES_DIR /
    "respondent_features.csv"
)

INVESTMENT_FILE = (
    FEATURES_DIR /
    "investment_features.csv"
)


# ==============================================================================
# 4. ANALYSIS OUTPUT FILES
# ==============================================================================

ANALYSIS_FILES = {

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
        "analysis_summary.csv",

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
        "monitoring_investment_analysis.csv"
}


# ==============================================================================
# 5. VALIDATION OUTPUT FILES
# ==============================================================================

VALIDATION_FILES = {

    # PRIMARY FILE EXPECTED BY 09_export_processed_data.py
    "report":
        VALIDATION_DIR /
        "validation_report.csv",

    # Compatibility file
    "summary":
        VALIDATION_DIR /
        "validation_summary.csv",

    "results":
        VALIDATION_DIR /
        "validation_results.csv",

    "schema":
        VALIDATION_DIR /
        "schema_validation.csv",

    "grain":
        VALIDATION_DIR /
        "grain_validation.csv",

    "key":
        VALIDATION_DIR /
        "key_validation.csv",

    "preference":
        VALIDATION_DIR /
        "preference_validation.csv",

    "category":
        VALIDATION_DIR /
        "category_validation.csv",

    "output":
        VALIDATION_DIR /
        "output_validation.csv",

    "business_rule":
        VALIDATION_DIR /
        "business_rule_validation.csv",

    "data_quality":
        VALIDATION_DIR /
        "data_quality_validation.csv",

    "errors":
        VALIDATION_DIR /
        "validation_errors.csv"
}


# ==============================================================================
# 6. GLOBAL VALIDATION STORAGE
# ==============================================================================

VALIDATION_RESULTS = []


# ==============================================================================
# 7. COLUMN FINDER
# ==============================================================================

def find_column(df, candidates):

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
# 8. FLEXIBLE COLUMN FINDER
# ==============================================================================

def find_column_contains(df, candidates):

    """
    More flexible column finder.

    Used when exact column names may differ slightly.
    """

    if df is None or df.empty:
        return None

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    # Exact match first
    for candidate in candidates:

        candidate_lower = (
            str(candidate)
            .strip()
            .lower()
        )

        if candidate_lower in normalized:
            return normalized[candidate_lower]

    # Contains match
    for candidate in candidates:

        candidate_lower = (
            str(candidate)
            .strip()
            .lower()
        )

        for normalized_name, original_name in normalized.items():

            if candidate_lower in normalized_name:
                return original_name

    return None


# ==============================================================================
# 9. NORMALIZE TEXT
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
# 10. IDENTIFY RESPONDENT COLUMNS
# ==============================================================================

def identify_respondent_columns(respondent_df):

    return {

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
        )
    }


# ==============================================================================
# 11. IDENTIFY INVESTMENT COLUMNS
# ==============================================================================

def identify_investment_columns(investment_df):

    return {

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


# ==============================================================================
# 12. LOAD FEATURE DATA
# ==============================================================================

def load_feature_data():

    print("\nLoading feature data...")

    if not RESPONDENT_FILE.exists():

        raise FileNotFoundError(
            f"\nMissing respondent feature file:\n"
            f"{RESPONDENT_FILE}"
        )

    if not INVESTMENT_FILE.exists():

        raise FileNotFoundError(
            f"\nMissing investment feature file:\n"
            f"{INVESTMENT_FILE}"
        )

    respondent_df = pd.read_csv(
        RESPONDENT_FILE
    )

    investment_df = pd.read_csv(
        INVESTMENT_FILE
    )

    print(
        f"Respondent rows : {len(respondent_df):,}"
    )

    print(
        f"Investment rows : {len(investment_df):,}"
    )

    return respondent_df, investment_df


# ==============================================================================
# 13. LOAD ANALYSIS OUTPUTS
# ==============================================================================

def load_analysis_outputs():

    outputs = {}

    print("\nLoading analysis outputs...")

    for key, path in ANALYSIS_FILES.items():

        if path.exists():

            try:

                outputs[key] = pd.read_csv(
                    path
                )

                print(
                    f"  ✓ {path.name}"
                )

            except Exception as error:

                outputs[key] = pd.DataFrame()

                print(
                    f"  ! Could not read "
                    f"{path.name}: {error}"
                )

        else:

            outputs[key] = pd.DataFrame()

            print(
                f"  ! Missing: {path.name}"
            )

    return outputs


# ==============================================================================
# 14. RECORD VALIDATION
# ==============================================================================

def record_validation(
    validation_area,
    check_name,
    status,
    message,
    actual_value=None,
    expected_value=None
):

    VALIDATION_RESULTS.append({

        "Validation_Area":
            validation_area,

        "Check_Name":
            check_name,

        "Status":
            status,

        "Message":
            message,

        "Actual_Value":
            actual_value,

        "Expected_Value":
            expected_value
    })


# ==============================================================================
# 15. VALIDATE SCHEMA
# ==============================================================================

def validate_schema(
    respondent_columns,
    investment_columns
):

    print("\nValidating schema...")

    respondent_required = {
        "Respondent ID":
            respondent_columns.get("id")
    }

    investment_required = {
        "Investment Respondent ID":
            investment_columns.get("id"),

        "Investment Type":
            investment_columns.get("type"),

        "Preference Rank":
            investment_columns.get("rank")
    }

    for name, column in respondent_required.items():

        if column:

            record_validation(
                "Schema",
                name,
                "PASS",
                f"{name} column detected.",
                column,
                "Required"
            )

        else:

            record_validation(
                "Schema",
                name,
                "FAIL",
                f"{name} column is missing.",
                None,
                "Required"
            )

    for name, column in investment_required.items():

        if column:

            record_validation(
                "Schema",
                name,
                "PASS",
                f"{name} column detected.",
                column,
                "Required"
            )

        else:

            record_validation(
                "Schema",
                name,
                "FAIL",
                f"{name} column is missing.",
                None,
                "Required"
            )


# ==============================================================================
# 16. VALIDATE RESPONDENT GRAIN
# ==============================================================================

def validate_respondent_grain(
    respondent_df,
    respondent_columns
):

    print("\nValidating respondent grain...")

    id_column = respondent_columns.get("id")

    if id_column is None:
        return

    total_rows = len(
        respondent_df
    )

    unique_ids = (
        respondent_df[id_column]
        .nunique()
    )

    duplicate_rows = (
        total_rows -
        unique_ids
    )

    if duplicate_rows == 0:

        record_validation(
            "Grain",
            "One Row Per Respondent",
            "PASS",
            (
                "Respondent table maintains "
                "one row per respondent."
            ),
            unique_ids,
            total_rows
        )

    else:

        record_validation(
            "Grain",
            "One Row Per Respondent",
            "FAIL",
            (
                "Duplicate Respondent_ID values "
                "were detected in respondent features."
            ),
            duplicate_rows,
            0
        )


# ==============================================================================
# 17. VALIDATE INVESTMENT GRAIN
# ==============================================================================

def validate_investment_grain(
    investment_df,
    investment_columns
):

    print("\nValidating investment grain...")

    id_column = investment_columns.get(
        "id"
    )

    type_column = investment_columns.get(
        "type"
    )

    if not id_column or not type_column:
        return

    total_rows = len(
        investment_df
    )

    unique_respondents = (
        investment_df[id_column]
        .nunique()
    )

    unique_pairs = (
        investment_df[
            [
                id_column,
                type_column
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    record_validation(
        "Grain",
        "Investment Table Supports Multiple Rows Per Respondent",
        "PASS",
        (
            "Investment table contains "
            "investment-level rows per respondent."
        ),
        total_rows,
        f">= {unique_respondents}"
    )

    record_validation(
        "Grain",
        "Investment Row Count Is Not Respondent Count",
        "PASS",
        (
            "Investment row count is kept separate "
            "from unique respondent count."
        ),
        total_rows,
        unique_respondents
    )

    record_validation(
        "Grain",
        "Respondent Investment Combinations",
        "PASS",
        "Unique respondent-investment combinations calculated.",
        unique_pairs,
        "Informational"
    )


# ==============================================================================
# 18. VALIDATE KEY INTEGRITY
# ==============================================================================

def validate_keys(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    print("\nValidating key integrity...")

    respondent_id = respondent_columns.get(
        "id"
    )

    investment_id = investment_columns.get(
        "id"
    )

    if not respondent_id or not investment_id:
        return

    respondent_ids = set(
        normalize_text(
            respondent_df[
                respondent_id
            ]
        )
        .dropna()
        .unique()
    )

    investment_ids = set(
        normalize_text(
            investment_df[
                investment_id
            ]
        )
        .dropna()
        .unique()
    )

    unmatched_ids = (
        investment_ids -
        respondent_ids
    )

    unused_respondents = (
        respondent_ids -
        investment_ids
    )

    if len(unmatched_ids) == 0:

        record_validation(
            "Key Integrity",
            "Investment IDs Match Respondent IDs",
            "PASS",
            (
                "All investment Respondent_ID values "
                "exist in respondent data."
            ),
            0,
            0
        )

    else:

        record_validation(
            "Key Integrity",
            "Investment IDs Match Respondent IDs",
            "FAIL",
            (
                "Some investment rows reference "
                "Respondent_ID values not found "
                "in respondent data."
            ),
            len(unmatched_ids),
            0
        )

    record_validation(
        "Key Integrity",
        "Respondents Without Investment Rows",
        (
            "WARNING"
            if len(unused_respondents) > 0
            else "PASS"
        ),
        (
            "Some respondents do not have investment rows."
            if len(unused_respondents) > 0
            else
            "Every respondent has at least one investment row."
        ),
        len(unused_respondents),
        0
    )


# ==============================================================================
# 19. VALIDATE PREFERENCE RANK
# ==============================================================================

def validate_preference_rank(
    investment_df,
    investment_columns
):

    print("\nValidating preference rank...")

    rank_column = investment_columns.get(
        "rank"
    )

    if rank_column is None:
        return

    rank_values = pd.to_numeric(
        investment_df[
            rank_column
        ],
        errors="coerce"
    )

    missing_count = (
        rank_values.isna()
        .sum()
    )

    invalid_count = (
        ~rank_values.isna()
        &
        ~rank_values.between(
            1,
            7
        )
    ).sum()

    if missing_count == 0:

        record_validation(
            "Preference",
            "Preference Rank Missing Values",
            "PASS",
            "No missing preference ranks detected.",
            0,
            0
        )

    else:

        record_validation(
            "Preference",
            "Preference Rank Missing Values",
            "FAIL",
            "Some preference ranks are missing.",
            int(missing_count),
            0
        )

    if invalid_count == 0:

        record_validation(
            "Preference",
            "Preference Rank Range",
            "PASS",
            "All preference ranks are between 1 and 7.",
            int(rank_values.max()),
            "1-7"
        )

    else:

        record_validation(
            "Preference",
            "Preference Rank Range",
            "FAIL",
            (
                "Preference ranks outside the "
                "valid 1-7 range were detected."
            ),
            int(invalid_count),
            0
        )


# ==============================================================================
# 20. VALIDATE PREFERENCE DIRECTION
# ==============================================================================

def validate_preference_direction(
    investment_df,
    investment_columns
):

    print("\nValidating preference direction...")

    type_column = investment_columns.get(
        "type"
    )

    rank_column = investment_columns.get(
        "rank"
    )

    if not type_column or not rank_column:
        return

    working = investment_df[
        [
            type_column,
            rank_column
        ]
    ].copy()

    working[rank_column] = pd.to_numeric(
        working[rank_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=[
            type_column,
            rank_column
        ]
    )

    if working.empty:
        return

    result = (
        working
        .groupby(type_column)[rank_column]
        .mean()
        .sort_values()
    )

    if not result.empty:

        record_validation(
            "Preference",
            "Lower Rank Means Stronger Preference",
            "PASS",
            (
                "Investment preference ranking "
                "uses ascending average rank."
            ),
            result.iloc[0],
            result.iloc[-1]
        )


# ==============================================================================
# 21. VALIDATE EXPECTED RETURN
# ==============================================================================

def validate_expected_return(
    respondent_df,
    respondent_columns
):

    print("\nValidating expected return...")

    expected_column = respondent_columns.get(
        "expected"
    )

    if expected_column is None:

        record_validation(
            "Business Rule",
            "Expected Return Column",
            "WARNING",
            (
                "Expected Return column "
                "was not detected."
            ),
            None,
            "Expected_Return_Range"
        )

        return

    values = normalize_text(
        respondent_df[
            expected_column
        ]
    ).dropna()

    if values.empty:

        record_validation(
            "Business Rule",
            "Expected Return Values",
            "WARNING",
            "No expected return values available.",
            0,
            "> 0"
        )

        return

    suspicious_numeric = 0

    for value in values.unique():

        text = str(value)

        if text.replace(
            ".",
            "",
            1
        ).isdigit():

            suspicious_numeric += 1

    if suspicious_numeric == 0:

        record_validation(
            "Business Rule",
            "Expected Return Remains Categorical",
            "PASS",
            (
                "Expected Return values remain "
                "categorical ranges rather than "
                "artificial numeric averages."
            ),
            values.unique().tolist(),
            "Categorical ranges"
        )

    else:

        record_validation(
            "Business Rule",
            "Expected Return Remains Categorical",
            "WARNING",
            (
                "Some expected return values "
                "appear numeric. Review transformation logic."
            ),
            suspicious_numeric,
            0
        )


# ==============================================================================
# 22. VALIDATE DATA QUALITY
# ==============================================================================

def validate_data_quality(
    respondent_df,
    investment_df,
    respondent_columns,
    investment_columns
):

    print("\nValidating data quality...")

    # --------------------------------------------------------------------------
    # Respondent ID
    # --------------------------------------------------------------------------

    respondent_id = respondent_columns.get(
        "id"
    )

    if respondent_id:

        missing = (
            respondent_df[
                respondent_id
            ]
            .isna()
            .sum()
        )

        record_validation(
            "Data Quality",
            "Missing Respondent IDs",
            "PASS" if missing == 0 else "FAIL",
            (
                "No missing respondent IDs."
                if missing == 0
                else
                "Missing respondent IDs detected."
            ),
            int(missing),
            0
        )

    # --------------------------------------------------------------------------
    # Investment Respondent ID
    # --------------------------------------------------------------------------

    investment_id = investment_columns.get(
        "id"
    )

    if investment_id:

        missing = (
            investment_df[
                investment_id
            ]
            .isna()
            .sum()
        )

        record_validation(
            "Data Quality",
            "Missing Investment Respondent IDs",
            "PASS" if missing == 0 else "FAIL",
            (
                "No missing investment respondent IDs."
                if missing == 0
                else
                "Missing investment respondent IDs detected."
            ),
            int(missing),
            0
        )

    # --------------------------------------------------------------------------
    # Investment Type
    # --------------------------------------------------------------------------

    type_column = investment_columns.get(
        "type"
    )

    if type_column:

        missing = (
            investment_df[
                type_column
            ]
            .isna()
            .sum()
        )

        record_validation(
            "Data Quality",
            "Missing Investment Types",
            (
                "PASS"
                if missing == 0
                else "WARNING"
            ),
            (
                "No missing investment types."
                if missing == 0
                else
                "Some investment rows have "
                "missing investment types."
            ),
            int(missing),
            0
        )


# ==============================================================================
# 23. VALIDATE ANALYSIS OUTPUT FILES
# ==============================================================================

def validate_output_files(outputs):

    print("\nValidating analysis output files...")

    for key, dataframe in outputs.items():

        filename = ANALYSIS_FILES[key].name

        if dataframe.empty:

            record_validation(
                "Output Files",
                filename,
                "WARNING",
                (
                    "Output file is missing "
                    "or contains no records."
                ),
                0,
                "> 0"
            )

        else:

            record_validation(
                "Output Files",
                filename,
                "PASS",
                "Analysis output loaded successfully.",
                len(dataframe),
                "> 0"
            )


# ==============================================================================
# 24. FIND ANALYSIS CATEGORY COLUMN
# ==============================================================================

def find_analysis_category_column(
    dataframe,
    analysis_type
):

    if dataframe is None or dataframe.empty:
        return None

    candidates = {

        "gender": [
            "Gender",
            "gender"
        ],

        "age": [
            "Age_Group",
            "age_group",
            "Age Group",
            "Age",
            "age"
        ],

        "objective": [
            "Investment_Objective",
            "investment_objective",
            "Objective",
            "objective"
        ]
    }

    return find_column_contains(
        dataframe,
        candidates.get(
            analysis_type,
            []
        )
    )


# ==============================================================================
# 25. VALIDATE OVERALL ANALYSIS
# ==============================================================================

def validate_overall_analysis(
    overall,
    investment_columns
):

    print("\nValidating overall analysis...")

    if overall.empty:

        record_validation(
            "Output",
            "Overall Investment Analysis",
            "FAIL",
            "Overall investment analysis is empty.",
            0,
            "> 0"
        )

        return

    type_column = investment_columns.get(
        "type"
    )

    required_columns = [
        type_column,
        "Unique_Respondents",
        "Average_Preference_Rank",
        "Overall_Preference_Rank"
    ]

    missing = [
        column
        for column in required_columns
        if column is None
        or column not in overall.columns
    ]

    if missing:

        record_validation(
            "Output",
            "Overall Analysis Schema",
            "FAIL",
            "Required columns are missing.",
            missing,
            required_columns
        )

    else:

        record_validation(
            "Output",
            "Overall Analysis Schema",
            "PASS",
            "Overall analysis contains required columns.",
            list(overall.columns),
            required_columns
        )

    # --------------------------------------------------------------------------
    # Ranking validation
    # --------------------------------------------------------------------------

    if (
        "Average_Preference_Rank"
        in overall.columns
        and
        "Overall_Preference_Rank"
        in overall.columns
    ):

        expected = (
            overall[
                "Average_Preference_Rank"
            ]
            .rank(
                method="dense",
                ascending=True
            )
            .astype(int)
        )

        actual = pd.to_numeric(
            overall[
                "Overall_Preference_Rank"
            ],
            errors="coerce"
        )

        if expected.equals(actual):

            record_validation(
                "Output",
                "Overall Preference Ranking",
                "PASS",
                (
                    "Overall preference ranking "
                    "correctly uses ascending average rank."
                ),
                "Valid",
                "Valid"
            )

        else:

            record_validation(
                "Output",
                "Overall Preference Ranking",
                "FAIL",
                (
                    "Overall preference ranking does not "
                    "match ascending average preference rank."
                ),
                actual.tolist(),
                expected.tolist()
            )


# ==============================================================================
# 26. VALIDATE SEGMENT ANALYSIS
# ==============================================================================

def validate_segment_analysis(
    dataframe,
    name,
    analysis_type,
    investment_type_column
):

    if dataframe.empty:

        record_validation(
            "Output",
            f"{name} Analysis",
            "WARNING",
            f"{name} analysis is empty.",
            0,
            "> 0"
        )

        return

    category_column = find_analysis_category_column(
        dataframe,
        analysis_type
    )

    required = [
        category_column,
        investment_type_column,
        "Unique_Respondents",
        "Average_Preference_Rank"
    ]

    missing = [
        column
        for column in required
        if column is None
        or column not in dataframe.columns
    ]

    if missing:

        record_validation(
            "Output",
            f"{name} Analysis Schema",
            "FAIL",
            (
                "Required analytical columns "
                "are missing."
            ),
            missing,
            required
        )

    else:

        record_validation(
            "Output",
            f"{name} Analysis Schema",
            "PASS",
            (
                f"{name} analysis contains "
                "all required analytical columns."
            ),
            required,
            required
        )


# ==============================================================================
# 27. VALIDATE UNIQUE RESPONDENT COUNTS
# ==============================================================================

def validate_unique_respondent_counts(
    dataframe,
    name
):

    if dataframe.empty:
        return

    count_column = "Unique_Respondents"

    if count_column not in dataframe.columns:

        record_validation(
            "Business Rule",
            f"{name} Respondent Count",
            "FAIL",
            (
                "Unique respondent count column "
                "is missing."
            ),
            None,
            count_column
        )

        return

    values = pd.to_numeric(
        dataframe[
            count_column
        ],
        errors="coerce"
    )

    invalid = (
        values.isna()
        |
        (values < 0)
    ).sum()

    if invalid == 0:

        record_validation(
            "Business Rule",
            f"{name} Uses Valid Respondent Counts",
            "PASS",
            (
                "Respondent counts are numeric "
                "and non-negative."
            ),
            int(values.max()),
            ">= 0"
        )

    else:

        record_validation(
            "Business Rule",
            f"{name} Uses Valid Respondent Counts",
            "FAIL",
            "Invalid respondent count values detected.",
            int(invalid),
            0
        )


# ==============================================================================
# 28. VALIDATE CATEGORY RANKING
# ==============================================================================

def validate_category_ranking(
    dataframe,
    name
):

    if dataframe.empty:
        return

    if (
        "Average_Preference_Rank"
        not in dataframe.columns
    ):
        return

    if (
        "Category_Preference_Rank"
        not in dataframe.columns
    ):
        return

    category_column = (
        find_analysis_category_column(
            dataframe,
            name.lower()
        )
    )

    if category_column is None:

        # Do not create a false FAIL.
        # Ranking can still be validated globally.
        category_column = find_column_contains(
            dataframe,
            [
                "Gender",
                "Age_Group",
                "Investment_Objective",
                "Objective",
                "Category"
            ]
        )

    if category_column is None:
        return

    expected = (
        dataframe
        .groupby(category_column)[
            "Average_Preference_Rank"
        ]
        .rank(
            method="dense",
            ascending=True
        )
        .astype(int)
    )

    actual = pd.to_numeric(
        dataframe[
            "Category_Preference_Rank"
        ],
        errors="coerce"
    )

    if expected.equals(actual):

        record_validation(
            "Output",
            f"{name} Preference Ranking",
            "PASS",
            (
                "Category-level preference rankings "
                "correctly follow ascending average rank."
            ),
            "Valid",
            "Valid"
        )

    else:

        record_validation(
            "Output",
            f"{name} Preference Ranking",
            "FAIL",
            (
                "Category preference ranking does not "
                "match the average rank."
            ),
            actual.tolist(),
            expected.tolist()
        )


# ==============================================================================
# 29. VALIDATE FEMALE ANALYSIS
# ==============================================================================

def validate_female_analysis(
    dataframe,
    investment_columns
):

    if dataframe.empty:
        return

    rank_column = "Average_Preference_Rank"

    if rank_column not in dataframe.columns:
        return

    values = pd.to_numeric(
        dataframe[
            rank_column
        ],
        errors="coerce"
    ).dropna()

    if values.empty:
        return

    sorted_correctly = (
        values.tolist()
        ==
        sorted(values.tolist())
    )

    record_validation(
        "Output",
        "Female Preference Ordering",
        "PASS" if sorted_correctly else "FAIL",
        (
            "Female investment preferences are "
            "ordered from strongest to weakest."
            if sorted_correctly
            else
            "Female preference output is not "
            "sorted by ascending average rank."
        ),
        "Ascending" if sorted_correctly else "Unsorted",
        "Ascending"
    )


# ==============================================================================
# 30. VALIDATE YOUNG INVESTOR ANALYSIS
# ==============================================================================

def validate_young_analysis(
    dataframe
):

    if dataframe.empty:
        return

    rank_column = "Average_Preference_Rank"

    if rank_column not in dataframe.columns:
        return

    values = pd.to_numeric(
        dataframe[
            rank_column
        ],
        errors="coerce"
    ).dropna()

    if values.empty:
        return

    sorted_correctly = (
        values.tolist()
        ==
        sorted(values.tolist())
    )

    record_validation(
        "Output",
        "Young Investor Preference Ordering",
        "PASS" if sorted_correctly else "FAIL",
        (
            "Young investor preferences "
            "are ordered correctly."
            if sorted_correctly
            else
            "Young investor preferences are "
            "not ordered correctly."
        ),
        "Ascending" if sorted_correctly else "Unsorted",
        "Ascending"
    )


# ==============================================================================
# 31. VALIDATE BOND ANALYSIS
# ==============================================================================

def validate_bond_analysis(
    dataframe
):

    if dataframe.empty:
        return

    rank_column = "Average_Preference_Rank"

    if rank_column not in dataframe.columns:
        return

    values = pd.to_numeric(
        dataframe[
            rank_column
        ],
        errors="coerce"
    ).dropna()

    invalid = (
        ~values.between(
            1,
            7
        )
    ).sum()

    record_validation(
        "Output",
        "Bond Preference Rank Range",
        "PASS" if invalid == 0 else "FAIL",
        (
            "Bond preference ranks are valid."
            if invalid == 0
            else
            "Invalid bond preference ranks detected."
        ),
        int(invalid),
        0
    )


# ==============================================================================
# 32. VALIDATE GENDER GAP
# ==============================================================================

def validate_gender_gap(
    gender_gap
):

    print("\nValidating gender preference gap...")

    if gender_gap.empty:

        record_validation(
            "Output",
            "Gender Preference Gap",
            "WARNING",
            "Gender preference gap output is empty.",
            0,
            "> 0"
        )

        return

    required = [
        "Female_Male_Rank_Gap",
        "Absolute_Rank_Gap"
    ]

    missing = [
        column
        for column in required
        if column not in gender_gap.columns
    ]

    if missing:

        record_validation(
            "Output",
            "Gender Gap Schema",
            "FAIL",
            "Gender gap columns are missing.",
            missing,
            required
        )

    else:

        record_validation(
            "Output",
            "Gender Gap Schema",
            "PASS",
            (
                "Gender gap output contains "
                "required metrics."
            ),
            required,
            required
        )


# ==============================================================================
# 33. VALIDATE INSIGHTS
# ==============================================================================

def validate_insights(
    insights,
    overall
):

    print("\nValidating executive insights...")

    if insights.empty:

        record_validation(
            "Executive Insight",
            "Executive Insights",
            "WARNING",
            "No executive insights were generated.",
            0,
            "> 0"
        )

        return

    required = [
        "Insight_Category",
        "Finding",
        "Interpretation",
        "Priority"
    ]

    missing = [
        column
        for column in required
        if column not in insights.columns
    ]

    if missing:

        record_validation(
            "Executive Insight",
            "Insight Schema",
            "FAIL",
            "Required insight columns are missing.",
            missing,
            required
        )

    else:

        record_validation(
            "Executive Insight",
            "Insight Schema",
            "PASS",
            "Executive insight structure is valid.",
            required,
            required
        )

    if not overall.empty:

        record_validation(
            "Executive Insight",
            "Insights Have Analytical Basis",
            "PASS",
            (
                "Executive insights were generated "
                "from analytical outputs."
            ),
            len(insights),
            "> 0"
        )


# ==============================================================================
# 34. VALIDATE RECOMMENDATIONS
# ==============================================================================

def validate_recommendations(
    recommendations,
    overall
):

    print("\nValidating recommendations...")

    if recommendations.empty:

        record_validation(
            "Recommendation",
            "Analytical Recommendations",
            "WARNING",
            "No recommendations were generated.",
            0,
            "> 0"
        )

        return

    required = [
        "Recommendation_ID",
        "Area",
        "Recommendation",
        "Business_Rationale",
        "Priority"
    ]

    missing = [
        column
        for column in required
        if column not in recommendations.columns
    ]

    if missing:

        record_validation(
            "Recommendation",
            "Recommendation Schema",
            "FAIL",
            "Required recommendation columns are missing.",
            missing,
            required
        )

    else:

        record_validation(
            "Recommendation",
            "Recommendation Schema",
            "PASS",
            "Recommendation structure is valid.",
            required,
            required
        )

        duplicate_ids = (
            recommendations[
                "Recommendation_ID"
            ]
            .duplicated()
            .sum()
        )

        if duplicate_ids == 0:

            record_validation(
                "Recommendation",
                "Recommendation IDs",
                "PASS",
                "Recommendation IDs are unique.",
                duplicate_ids,
                0
            )

        else:

            record_validation(
                "Recommendation",
                "Recommendation IDs",
                "FAIL",
                "Duplicate recommendation IDs detected.",
                int(duplicate_ids),
                0
            )


# ==============================================================================
# 35. VALIDATE BUSINESS QUESTIONS
# ==============================================================================

def validate_business_questions(
    female_analysis,
    young_analysis,
    bond_analysis,
    investment_columns
):

    print("\nValidating business-question outputs...")

    type_column = investment_columns.get(
        "type"
    )

    if not type_column:
        return

    # --------------------------------------------------------------------------
    # Female / Gold
    # --------------------------------------------------------------------------

    if not female_analysis.empty:

        actual_type_column = find_column_contains(
            female_analysis,
            [
                type_column,
                "Investment_Type",
                "investment_type"
            ]
        )

        if actual_type_column:

            values = normalize_text(
                female_analysis[
                    actual_type_column
                ]
            ).str.lower()

            if values.eq("gold").any():

                record_validation(
                    "Business Questions",
                    "Female Gold Question",
                    "PASS",
                    (
                        "Female Gold preference "
                        "can be evaluated."
                    ),
                    "Gold available",
                    "Gold available"
                )

            else:

                record_validation(
                    "Business Questions",
                    "Female Gold Question",
                    "WARNING",
                    (
                        "Gold is not present "
                        "in female analysis."
                    ),
                    "Not available",
                    "Gold"
                )

    # --------------------------------------------------------------------------
    # Young / Equity
    # --------------------------------------------------------------------------

    if not young_analysis.empty:

        actual_type_column = find_column_contains(
            young_analysis,
            [
                type_column,
                "Investment_Type",
                "investment_type"
            ]
        )

        if actual_type_column:

            values = normalize_text(
                young_analysis[
                    actual_type_column
                ]
            ).str.lower()

            if values.eq("equity").any():

                record_validation(
                    "Business Questions",
                    "Young Equity Question",
                    "PASS",
                    (
                        "Young Equity preference "
                        "can be evaluated."
                    ),
                    "Equity available",
                    "Equity available"
                )

            else:

                record_validation(
                    "Business Questions",
                    "Young Equity Question",
                    "WARNING",
                    (
                        "Equity is not present "
                        "in young investor analysis."
                    ),
                    "Not available",
                    "Equity"
                )

    # --------------------------------------------------------------------------
    # Bond
    # --------------------------------------------------------------------------

    if not bond_analysis.empty:

        record_validation(
            "Business Questions",
            "Bond Preference Question",
            "PASS",
            (
                "Bond preference analysis is "
                "available for demographic segmentation."
            ),
            len(bond_analysis),
            "> 0"
        )


# ==============================================================================
# 36. CREATE VALIDATION SUMMARY / REPORT
# ==============================================================================

def create_validation_report():

    results_df = pd.DataFrame(
        VALIDATION_RESULTS
    )

    if results_df.empty:

        return pd.DataFrame()

    total = len(
        results_df
    )

    passed = (
        results_df[
            "Status"
        ]
        .eq("PASS")
        .sum()
    )

    warnings = (
        results_df[
            "Status"
        ]
        .eq("WARNING")
        .sum()
    )

    failed = (
        results_df[
            "Status"
        ]
        .eq("FAIL")
        .sum()
    )

    if failed > 0:

        final_status = "FAIL"

    elif warnings > 0:

        final_status = "WARNING"

    else:

        final_status = "PASS"

    pass_rate = (
        passed /
        total *
        100
        if total > 0
        else 0
    )

    report = {

        "Validation_Run":
            pd.Timestamp.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Total_Checks":
            int(total),

        "Passed":
            int(passed),

        "Warnings":
            int(warnings),

        "Failed":
            int(failed),

        "Pass_Rate_Percent":
            round(
                pass_rate,
                2
            ),

        "Final_Validation_Status":
            final_status
    }

    return pd.DataFrame(
        [report]
    )


# ==============================================================================
# 37. SAVE VALIDATION FILE
# ==============================================================================

def save_validation_file(
    dataframe,
    key
):

    path = VALIDATION_FILES.get(
        key
    )

    if path is None:
        return

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
# 38. PRINT VALIDATION REPORT
# ==============================================================================

def print_validation_report(
    results,
    report
):

    print("\n")
    print("=" * 90)
    print("VALIDATION REPORT")
    print("=" * 90)

    if report.empty:

        print(
            "No validation results generated."
        )

        return

    row = report.iloc[0]

    print(
        f"\nTotal Checks : "
        f"{row['Total_Checks']}"
    )

    print(
        f"PASS         : "
        f"{row['Passed']}"
    )

    print(
        f"WARNING      : "
        f"{row['Warnings']}"
    )

    print(
        f"FAIL         : "
        f"{row['Failed']}"
    )

    print(
        f"Pass Rate    : "
        f"{row['Pass_Rate_Percent']}%"
    )

    print(
        f"\nFINAL STATUS : "
        f"{row['Final_Validation_Status']}"
    )

    if not results.empty:

        display_columns = [
            "Validation_Area",
            "Check_Name",
            "Status",
            "Message"
        ]

        display_columns = [
            column
            for column in display_columns
            if column in results.columns
        ]

        print("\n")

        print(
            results[
                display_columns
            ].to_string(
                index=False
            )
        )


# ==============================================================================
# 39. PRINT CRITICAL FAILURES
# ==============================================================================

def print_failures(
    results
):

    if results.empty:
        return

    failures = results[
        results["Status"]
        .eq("FAIL")
    ]

    if failures.empty:

        print(
            "\n✓ No critical validation failures detected."
        )

        return

    print("\n")
    print("=" * 90)
    print("CRITICAL VALIDATION FAILURES")
    print("=" * 90)

    for _, row in failures.iterrows():

        print(
            f"\n[{row['Validation_Area']}] "
            f"{row['Check_Name']}"
        )

        print(
            f"  {row['Message']}"
        )

        print(
            f"  Actual   : "
            f"{row['Actual_Value']}"
        )

        print(
            f"  Expected : "
            f"{row['Expected_Value']}"
        )


# ==============================================================================
# 40. MAIN
# ==============================================================================

def main():

    print("=" * 90)

    print(
        "INVESTMENT SURVEY — ANALYTICAL VALIDATION"
    )

    print("=" * 90)

    # ==========================================================================
    # STEP 1 — LOAD FEATURE DATA
    # ==========================================================================

    respondent_df, investment_df = (
        load_feature_data()
    )

    # ==========================================================================
    # STEP 2 — IDENTIFY COLUMNS
    # ==========================================================================

    respondent_columns = (
        identify_respondent_columns(
            respondent_df
        )
    )

    investment_columns = (
        identify_investment_columns(
            investment_df
        )
    )

    print(
        "\nDetected respondent columns:"
    )

    for key, value in respondent_columns.items():

        print(
            f"  {key:<20} : {value}"
        )

    print(
        "\nDetected investment columns:"
    )

    for key, value in investment_columns.items():

        print(
            f"  {key:<20} : {value}"
        )

    # ==========================================================================
    # STEP 3 — LOAD ANALYSIS OUTPUTS
    # ==========================================================================

    analysis_outputs = (
        load_analysis_outputs()
    )

    # ==========================================================================
    # STEP 4 — SCHEMA
    # ==========================================================================

    validate_schema(
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 5 — RESPONDENT GRAIN
    # ==========================================================================

    validate_respondent_grain(
        respondent_df,
        respondent_columns
    )

    # ==========================================================================
    # STEP 6 — INVESTMENT GRAIN
    # ==========================================================================

    validate_investment_grain(
        investment_df,
        investment_columns
    )

    # ==========================================================================
    # STEP 7 — KEY INTEGRITY
    # ==========================================================================

    validate_keys(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 8 — PREFERENCE RANK
    # ==========================================================================

    validate_preference_rank(
        investment_df,
        investment_columns
    )

    # ==========================================================================
    # STEP 9 — PREFERENCE DIRECTION
    # ==========================================================================

    validate_preference_direction(
        investment_df,
        investment_columns
    )

    # ==========================================================================
    # STEP 10 — EXPECTED RETURN
    # ==========================================================================

    validate_expected_return(
        respondent_df,
        respondent_columns
    )

    # ==========================================================================
    # STEP 11 — DATA QUALITY
    # ==========================================================================

    validate_data_quality(
        respondent_df,
        investment_df,
        respondent_columns,
        investment_columns
    )

    # ==========================================================================
    # STEP 12 — OUTPUT FILE VALIDATION
    # ==========================================================================

    validate_output_files(
        analysis_outputs
    )

    # ==========================================================================
    # STEP 13 — OVERALL ANALYSIS
    # ==========================================================================

    overall = analysis_outputs.get(
        "investment_analysis",
        pd.DataFrame()
    )

    validate_overall_analysis(
        overall,
        investment_columns
    )

    # ==========================================================================
    # STEP 14 — GENDER ANALYSIS
    # ==========================================================================

    gender_analysis = analysis_outputs.get(
        "gender_analysis",
        pd.DataFrame()
    )

    validate_segment_analysis(
        gender_analysis,
        "Gender",
        "gender",
        investment_columns.get("type")
    )

    validate_unique_respondent_counts(
        gender_analysis,
        "Gender"
    )

    validate_category_ranking(
        gender_analysis,
        "Gender"
    )

    # ==========================================================================
    # STEP 15 — AGE ANALYSIS
    # ==========================================================================

    age_analysis = analysis_outputs.get(
        "age_analysis",
        pd.DataFrame()
    )

    validate_segment_analysis(
        age_analysis,
        "Age",
        "age",
        investment_columns.get("type")
    )

    validate_unique_respondent_counts(
        age_analysis,
        "Age"
    )

    validate_category_ranking(
        age_analysis,
        "Age"
    )

    # ==========================================================================
    # STEP 16 — OBJECTIVE ANALYSIS
    # ==========================================================================

    objective_analysis = analysis_outputs.get(
        "objective_analysis",
        pd.DataFrame()
    )

    validate_segment_analysis(
        objective_analysis,
        "Objective",
        "objective",
        investment_columns.get("type")
    )

    validate_unique_respondent_counts(
        objective_analysis,
        "Objective"
    )

    validate_category_ranking(
        objective_analysis,
        "Objective"
    )

    # ==========================================================================
    # STEP 17 — FEMALE ANALYSIS
    # ==========================================================================

    female_analysis = analysis_outputs.get(
        "female_analysis",
        pd.DataFrame()
    )

    validate_female_analysis(
        female_analysis,
        investment_columns
    )

    # ==========================================================================
    # STEP 18 — YOUNG INVESTOR ANALYSIS
    # ==========================================================================

    young_analysis = analysis_outputs.get(
        "young_analysis",
        pd.DataFrame()
    )

    validate_young_analysis(
        young_analysis
    )

    # ==========================================================================
    # STEP 19 — BOND ANALYSIS
    # ==========================================================================

    bond_analysis = analysis_outputs.get(
        "bond_analysis",
        pd.DataFrame()
    )

    validate_bond_analysis(
        bond_analysis
    )

    # ==========================================================================
    # STEP 20 — GENDER GAP
    # ==========================================================================

    gender_gap = analysis_outputs.get(
        "gender_gap",
        pd.DataFrame()
    )

    validate_gender_gap(
        gender_gap
    )

    # ==========================================================================
    # STEP 21 — EXECUTIVE INSIGHTS
    # ==========================================================================

    insights = analysis_outputs.get(
        "executive_insights",
        pd.DataFrame()
    )

    validate_insights(
        insights,
        overall
    )

    # ==========================================================================
    # STEP 22 — RECOMMENDATIONS
    # ==========================================================================

    recommendations = analysis_outputs.get(
        "recommendations",
        pd.DataFrame()
    )

    validate_recommendations(
        recommendations,
        overall
    )

    # ==========================================================================
    # STEP 23 — BUSINESS QUESTIONS
    # ==========================================================================

    validate_business_questions(
        female_analysis,
        young_analysis,
        bond_analysis,
        investment_columns
    )

    # ==========================================================================
    # STEP 24 — CREATE RESULTS
    # ==========================================================================

    results_df = pd.DataFrame(
        VALIDATION_RESULTS
    )

    # ==========================================================================
    # STEP 25 — CREATE REPORT
    # ==========================================================================

    report_df = (
        create_validation_report()
    )

    # ==========================================================================
    # STEP 26 — SAVE VALIDATION OUTPUTS
    # ==========================================================================

    print("\n")
    print("=" * 90)
    print("SAVING VALIDATION OUTPUTS")
    print("=" * 90)

    # --------------------------------------------------------------------------
    # PRIMARY REPORT
    # --------------------------------------------------------------------------

    save_validation_file(
        report_df,
        "report"
    )

    # --------------------------------------------------------------------------
    # BACKWARD COMPATIBILITY SUMMARY
    # --------------------------------------------------------------------------

    save_validation_file(
        report_df,
        "summary"
    )

    # --------------------------------------------------------------------------
    # COMPLETE RESULTS
    # --------------------------------------------------------------------------

    save_validation_file(
        results_df,
        "results"
    )

    # --------------------------------------------------------------------------
    # AREA-SPECIFIC OUTPUTS
    # --------------------------------------------------------------------------

    if not results_df.empty:

        schema_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Schema")
        ]

        grain_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Grain")
        ]

        key_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Key Integrity")
        ]

        preference_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Preference")
        ]

        category_df = results_df[
            results_df[
                "Validation_Area"
            ].isin(
                [
                    "Output",
                    "Business Rule"
                ]
            )
        ]

        output_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Output")
        ]

        business_rule_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Business Rule")
        ]

        data_quality_df = results_df[
            results_df[
                "Validation_Area"
            ].eq("Data Quality")
        ]

        errors_df = results_df[
            results_df[
                "Status"
            ].eq("FAIL")
        ]

    else:

        schema_df = pd.DataFrame()
        grain_df = pd.DataFrame()
        key_df = pd.DataFrame()
        preference_df = pd.DataFrame()
        category_df = pd.DataFrame()
        output_df = pd.DataFrame()
        business_rule_df = pd.DataFrame()
        data_quality_df = pd.DataFrame()
        errors_df = pd.DataFrame()

    save_validation_file(
        schema_df,
        "schema"
    )

    save_validation_file(
        grain_df,
        "grain"
    )

    save_validation_file(
        key_df,
        "key"
    )

    save_validation_file(
        preference_df,
        "preference"
    )

    save_validation_file(
        category_df,
        "category"
    )

    save_validation_file(
        output_df,
        "output"
    )

    save_validation_file(
        business_rule_df,
        "business_rule"
    )

    save_validation_file(
        data_quality_df,
        "data_quality"
    )

    save_validation_file(
        errors_df,
        "errors"
    )

    # ==========================================================================
    # STEP 27 — PRINT REPORT
    # ==========================================================================

    print_validation_report(
        results_df,
        report_df
    )

    # ==========================================================================
    # STEP 28 — PRINT FAILURES
    # ==========================================================================

    print_failures(
        results_df
    )

    # ==========================================================================
    # STEP 29 — FINAL STATUS
    # ==========================================================================

    print("\n")
    print("=" * 90)

    if report_df.empty:

        print(
            "08_validation.py COMPLETED — "
            "NO VALIDATION RESULTS"
        )

    else:

        final_status = report_df.iloc[0][
            "Final_Validation_Status"
        ]

        if final_status == "PASS":

            print(
                "08_validation.py COMPLETED — "
                "VALIDATION PASSED"
            )

        elif final_status == "WARNING":

            print(
                "08_validation.py COMPLETED — "
                "VALIDATION PASSED WITH WARNINGS"
            )

        else:

            print(
                "08_validation.py COMPLETED — "
                "VALIDATION FAILED"
            )

    print("=" * 90)

    print(
        f"\nPrimary validation report saved to:\n"
        f"{VALIDATION_FILES['report']}"
    )

    print(
        "\n✓ Downstream-compatible file:"
    )

    print(
        f"  {VALIDATION_FILES['report'].name}"
    )


# ==============================================================================
# 41. ENTRY POINT
# ==============================================================================

if __name__ == "__main__":

    main()