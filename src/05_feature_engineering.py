"""
Investment Survey Analytics Project
====================================

File:
    05_feature_engineering.py

Purpose:
    Create reusable analytical features from the transformed
    Investment Survey datasets.

Input:
    data/transformed/respondent_analysis.csv
    data/transformed/investment_long.csv
    data/transformed/expected_return_analysis.csv

Output:
    data/features/respondent_features.csv
    data/features/investment_features.csv

IMPORTANT:
    This file creates FEATURES.

    It does NOT calculate final dashboard KPIs.

    KPI/business-metric calculations belong in a later layer.

Core business rules:

    1. One Respondent_ID = one survey respondent.

    2. Investment_Long is at:
           Respondent × Investment Type
       grain.

    3. Preference Rank:
           1 = Highest Preference
           7 = Lowest Preference

    4. Therefore:
           LOWER average rank
           =
           HIGHER investment preference

    5. Expected Return is categorical:
           10%-20%
           20%-30%
           30%-40%

       It is NOT converted into a numeric average.

The goal is to create reusable analytical features that
can be consumed by the business-metrics and dashboard layers.
"""


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

from pathlib import Path
import re
import pandas as pd


# ============================================================
# 2. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRANSFORMED_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "transformed"
)

FEATURES_DIR = (
    PROJECT_ROOT
    / "data"
    / "features"
)

FEATURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. INPUT FILES
# ============================================================

RESPONDENT_FILE = (
    TRANSFORMED_DATA_DIR
    / "respondent_analysis.csv"
)

INVESTMENT_FILE = (
    TRANSFORMED_DATA_DIR
    / "investment_long.csv"
)

EXPECTED_RETURN_FILE = (
    TRANSFORMED_DATA_DIR
    / "expected_return_analysis.csv"
)


# ============================================================
# 4. OUTPUT FILES
# ============================================================

RESPONDENT_FEATURE_FILE = (
    FEATURES_DIR
    / "respondent_features.csv"
)

INVESTMENT_FEATURE_FILE = (
    FEATURES_DIR
    / "investment_features.csv"
)


# ============================================================
# 5. EXPECTED RETURN ORDER
# ============================================================

# Your source contains text ranges such as:
#
#     10%-20%
#     20%-30%
#     30%-40%
#
# We create an ORDERING feature only.
#
# We are NOT saying:
#
#     10%-20% = 15%
#
# because that would introduce an analytical assumption.

EXPECTED_RETURN_ORDER = {

    "10%-20%": 1,

    "20%-30%": 2,

    "30%-40%": 3,

    "40%-50%": 4,

    "50%-60%": 5
}


# ============================================================
# 6. INVESTMENT RANK ORDER
# ============================================================

INVESTMENT_RANK_MAP = {

    "Mutual Fund": 1,

    "Equity": 2,

    "Debenture": 3,

    "Government Bond": 4,

    "Fixed Deposit": 5,

    "PPF": 6,

    "Gold": 7
}


# ============================================================
# 7. INVESTMENT PREFERENCE CATEGORIES
# ============================================================

def classify_preference_rank(rank):
    """
    Convert numerical preference rank into a business-friendly
    category.

    Business rule:

        1 = Highest
        7 = Lowest
    """

    if pd.isna(rank):
        return pd.NA

    rank = int(rank)

    if rank == 1:
        return "Highest Preference"

    if rank == 2:
        return "High Preference"

    if rank in [3, 4, 5]:
        return "Moderate Preference"

    if rank == 6:
        return "Low Preference"

    if rank == 7:
        return "Lowest Preference"

    return "Unknown"


# ============================================================
# 8. LOAD DATA
# ============================================================

def load_input_data():

    if not RESPONDENT_FILE.exists():

        raise FileNotFoundError(
            "\nRespondent feature source not found:\n"
            f"{RESPONDENT_FILE}\n\n"
            "Run 04_data_transformation.py first."
        )

    if not INVESTMENT_FILE.exists():

        raise FileNotFoundError(
            "\nInvestment transformation source not found:\n"
            f"{INVESTMENT_FILE}\n\n"
            "Run 04_data_transformation.py first."
        )

    respondent_df = pd.read_csv(
        RESPONDENT_FILE
    )

    investment_df = pd.read_csv(
        INVESTMENT_FILE
    )

    return respondent_df, investment_df


# ============================================================
# 9. VALIDATE INPUT DATA
# ============================================================

def validate_input_data(
    respondent_df,
    investment_df
):

    respondent_required = [
        "Respondent_ID"
    ]

    investment_required = [
        "Respondent_ID",
        "Investment_Type",
        "Preference_Rank"
    ]

    for column in respondent_required:

        if column not in respondent_df.columns:

            raise ValueError(
                f"Required respondent column missing: "
                f"{column}"
            )

    for column in investment_required:

        if column not in investment_df.columns:

            raise ValueError(
                f"Required investment column missing: "
                f"{column}"
            )


# ============================================================
# 10. AGE FEATURE ENGINEERING
# ============================================================

def create_age_features(df):

    df = df.copy()

    if "age" not in df.columns:
        return df

    # --------------------------------------------------------
    # Ensure numeric age
    # --------------------------------------------------------

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Age Group
    # --------------------------------------------------------
    #
    # These bands are designed for business analysis:
    #
    # Under 25
    # 25-34
    # 35-44
    # 45-54
    # 55+
    #
    # We keep the categories broad enough to avoid excessive
    # fragmentation in dashboard visuals.

    df["Age_Group"] = pd.cut(

        df["age"],

        bins=[
            0,
            24,
            34,
            44,
            54,
            float("inf")
        ],

        labels=[
            "Under 25",
            "25-34",
            "35-44",
            "45-54",
            "55+"
        ],

        right=True,

        include_lowest=True
    )

    # --------------------------------------------------------
    # Numeric age group sort order
    # --------------------------------------------------------

    df["Age_Group_Sort"] = pd.cut(

        df["age"],

        bins=[
            0,
            24,
            34,
            44,
            54,
            float("inf")
        ],

        labels=[
            1,
            2,
            3,
            4,
            5
        ],

        right=True,

        include_lowest=True
    )

    # --------------------------------------------------------
    # Younger Investor Flag
    # --------------------------------------------------------

    df["Is_Young_Investor"] = (

        df["age"] < 30
    ).astype("int8")

    # --------------------------------------------------------
    # Young Investor Label
    # --------------------------------------------------------

    df["Investor_Age_Segment"] = (

        df["age"]

        .apply(

            lambda age:

                "Under 30"
                if pd.notna(age) and age < 30

                else "30+"
                if pd.notna(age)

                else "Unknown"
        )
    )

    return df


# ============================================================
# 11. GENDER FEATURES
# ============================================================

def create_gender_features(df):

    df = df.copy()

    if "gender" not in df.columns:
        return df

    # --------------------------------------------------------
    # Clean gender
    # --------------------------------------------------------

    df["Gender"] = (

        df["gender"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Gender Key
    # --------------------------------------------------------

    df["Gender_Key"] = (

        df["Gender"]
        .str.lower()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    # --------------------------------------------------------
    # Gender flags
    # --------------------------------------------------------

    df["Is_Male"] = (

        df["Gender_Key"]
        .eq("male")
        .astype("int8")
    )

    df["Is_Female"] = (

        df["Gender_Key"]
        .eq("female")
        .astype("int8")
    )

    return df


# ============================================================
# 12. INVESTMENT DURATION FEATURES
# ============================================================

def create_duration_features(df):

    df = df.copy()

    if "Duration" not in df.columns:
        return df

    df["Investment_Duration"] = (

        df["Duration"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Duration ordering
    # --------------------------------------------------------
    #
    # Your source is categorical.
    #
    # We therefore create an explicit business ordering.

    duration_order = {

        "Less than 1 year": 1,

        "1-3 years": 2,

        "3-5 years": 3,

        "More than 5 years": 4
    }

    df["Duration_Order"] = (

        df["Investment_Duration"]
        .map(duration_order)
    )

    # --------------------------------------------------------
    # Duration segment
    # --------------------------------------------------------

    df["Duration_Segment"] = (

        df["Duration_Order"]

        .map(

            lambda x:

                "Short Term"
                if x == 1

                else "Medium Term"
                if x in [2, 3]

                else "Long Term"
                if x == 4

                else "Unknown"
        )
    )

    return df


# ============================================================
# 13. EXPECTED RETURN FEATURES
# ============================================================

def create_expected_return_features(df):

    df = df.copy()

    if "Expect" not in df.columns:
        return df

    df["Expected_Return_Range"] = (

        df["Expect"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Expected return ordering
    # --------------------------------------------------------

    df["Expected_Return_Order"] = (

        df["Expected_Return_Range"]
        .map(EXPECTED_RETURN_ORDER)
    )

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    #
    # We intentionally DO NOT create:
    #
    #     Average_Expected_Return
    #
    # because your source does not contain numeric return
    # values.

    return df


# ============================================================
# 14. OBJECTIVE FEATURES
# ============================================================

def create_objective_features(df):

    df = df.copy()

    if "Objective" not in df.columns:
        return df

    df["Investment_Objective"] = (

        df["Objective"]
        .astype("string")
        .str.strip()
    )

    df["Investment_Objective_Key"] = (

        df["Investment_Objective"]
        .str.lower()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    return df


# ============================================================
# 15. PURPOSE FEATURES
# ============================================================

def create_purpose_features(df):

    df = df.copy()

    if "Purpose" not in df.columns:
        return df

    df["Investment_Purpose"] = (

        df["Purpose"]
        .astype("string")
        .str.strip()
    )

    return df


# ============================================================
# 16. DECISION FACTOR FEATURES
# ============================================================

def create_factor_features(df):

    df = df.copy()

    if "Factor" not in df.columns:
        return df

    df["Decision_Factor"] = (

        df["Factor"]
        .astype("string")
        .str.strip()
    )

    return df


# ============================================================
# 17. INVESTMENT AVENUE FEATURES
# ============================================================

def create_avenue_features(df):

    df = df.copy()

    if "Investment_Avenues" in df.columns:

        df["Investment_Avenue"] = (

            df["Investment_Avenues"]
            .astype("string")
            .str.strip()
        )

    if "Avenue" in df.columns:

        df["Preferred_Avenue"] = (

            df["Avenue"]
            .astype("string")
            .str.strip()
        )

    return df


# ============================================================
# 18. MONITORING FREQUENCY FEATURES
# ============================================================

def create_monitoring_features(df):

    df = df.copy()

    if "Invest_Monitor" not in df.columns:
        return df

    df["Investment_Monitoring_Frequency"] = (

        df["Invest_Monitor"]
        .astype("string")
        .str.strip()
    )

    monitoring_order = {

        "Daily": 1,

        "Weekly": 2,

        "Monthly": 3,

        "Quarterly": 4,

        "Yearly": 5,

        "Rarely": 6
    }

    df["Monitoring_Order"] = (

        df[
            "Investment_Monitoring_Frequency"
        ]
        .map(monitoring_order)
    )

    return df


# ============================================================
# 19. SAVINGS OBJECTIVE FEATURES
# ============================================================

def create_savings_features(df):

    df = df.copy()

    source_column = (
        "What are your savings objectives?"
    )

    if source_column not in df.columns:
        return df

    df["Savings_Objective"] = (

        df[source_column]
        .astype("string")
        .str.strip()
    )

    df["Savings_Objective_Key"] = (

        df["Savings_Objective"]
        .str.lower()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    return df


# ============================================================
# 20. INFORMATION SOURCE FEATURES
# ============================================================

def create_source_features(df):

    df = df.copy()

    if "Source" not in df.columns:
        return df

    df["Information_Source"] = (

        df["Source"]
        .astype("string")
        .str.strip()
    )

    df["Information_Source_Key"] = (

        df["Information_Source"]
        .str.lower()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    return df


# ============================================================
# 21. INVESTMENT FEATURES
# ============================================================

def create_investment_features(df):

    df = df.copy()

    # --------------------------------------------------------
    # Ensure rank is numeric
    # --------------------------------------------------------

    df["Preference_Rank"] = pd.to_numeric(

        df["Preference_Rank"],

        errors="coerce"
    )

    # --------------------------------------------------------
    # Preference classification
    # --------------------------------------------------------

    df["Preference_Category"] = (

        df["Preference_Rank"]
        .apply(
            classify_preference_rank
        )
    )

    # --------------------------------------------------------
    # Preference Score
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Rank 1 should have the highest score.
    #
    # With maximum rank 7:
    #
    #     Score = 8 - Rank
    #
    # Therefore:
    #
    #     Rank 1 -> Score 7
    #     Rank 2 -> Score 6
    #     ...
    #     Rank 7 -> Score 1
    #
    # This creates a positive score where HIGHER is better.

    df["Preference_Score"] = (

        8
        -
        df["Preference_Rank"]
    )

    # --------------------------------------------------------
    # Investment Rank
    # --------------------------------------------------------
    #
    # This is the fixed display order for the investment
    # categories, NOT preference ranking.

    df["Investment_Display_Order"] = (

        df["Investment_Type"]
        .map(INVESTMENT_RANK_MAP)
    )

    # --------------------------------------------------------
    # Highest preference flag
    # --------------------------------------------------------

    df["Is_Highest_Preference"] = (

        df["Preference_Rank"]
        .eq(1)
        .astype("int8")
    )

    # --------------------------------------------------------
    # Top 3 preference flag
    # --------------------------------------------------------

    df["Is_Top_3_Preference"] = (

        df["Preference_Rank"]
        .le(3)
        .astype("int8")
    )

    return df


# ============================================================
# 22. INVESTMENT TYPE KEY
# ============================================================

def create_investment_keys(df):

    df = df.copy()

    if "Investment_Type" not in df.columns:
        return df

    df["Investment_Type_Key"] = (

        df["Investment_Type"]
        .astype("string")
        .str.lower()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    return df


# ============================================================
# 23. RESPONDENT × INVESTMENT FEATURES
# ============================================================

def create_cross_analysis_features(
    respondent_df,
    investment_df
):

    """
    Bring selected respondent-level demographic attributes
    into the investment preference table.

    This allows analysis such as:

        Investment Preference by Gender
        Investment Preference by Age Group
        Investment Preference by Objective
        Investment Preference by Savings Objective
    """

    demographic_columns = [

        "Respondent_ID",

        "Gender",

        "age",

        "Age_Group",

        "Age_Group_Sort",

        "Investor_Age_Segment",

        "Investment_Objective",

        "Investment_Purpose",

        "Decision_Factor",

        "Savings_Objective",

        "Information_Source",

        "Expected_Return_Range",

        "Investment_Duration",

        "Duration_Segment",

        "Investment_Avenue"
    ]

    available_columns = [

        column

        for column in demographic_columns

        if column in respondent_df.columns
    ]

    demographic_df = (

        respondent_df[
            available_columns
        ]

        .drop_duplicates(
            subset=[
                "Respondent_ID"
            ]
        )
    )

    investment_df = (

        investment_df

        .drop(
            columns=[
                column
                for column in available_columns
                if column != "Respondent_ID"
                and column in investment_df.columns
            ],
            errors="ignore"
        )

        .merge(

            demographic_df,

            on="Respondent_ID",

            how="left",

            validate="many_to_one"
        )
    )

    return investment_df


# ============================================================
# 24. FEATURE QUALITY CHECK
# ============================================================

def validate_features(
    respondent_df,
    investment_df
):

    print("\n")
    print("=" * 75)
    print("FEATURE VALIDATION")
    print("=" * 75)

    # --------------------------------------------------------
    # Respondent uniqueness
    # --------------------------------------------------------

    respondent_count = (
        respondent_df[
            "Respondent_ID"
        ]
        .nunique()
    )

    respondent_rows = (
        len(respondent_df)
    )

    print(
        f"\nRespondent rows       : "
        f"{respondent_rows}"
    )

    print(
        f"Unique respondents   : "
        f"{respondent_count}"
    )

    if respondent_rows != respondent_count:

        print(
            "WARNING: respondent table "
            "contains duplicate Respondent_ID values."
        )

    else:

        print(
            "✓ Respondent grain validated."
        )

    # --------------------------------------------------------
    # Investment rows
    # --------------------------------------------------------

    investment_rows = (
        len(investment_df)
    )

    investment_types = (

        investment_df[
            "Investment_Type"
        ]
        .nunique()
    )

    print(
        f"\nInvestment rows      : "
        f"{investment_rows}"
    )

    print(
        f"Investment types     : "
        f"{investment_types}"
    )

    # --------------------------------------------------------
    # Preference rank
    # --------------------------------------------------------

    invalid_rank = (

        investment_df[
            "Preference_Rank"
        ]
        .notna()

        & (

            (
                investment_df[
                    "Preference_Rank"
                ] < 1
            )

            |

            (
                investment_df[
                    "Preference_Rank"
                ] > 7
            )
        )
    )

    print(
        f"\nInvalid preference ranks: "
        f"{invalid_rank.sum()}"
    )

    # --------------------------------------------------------
    # Preference score
    # --------------------------------------------------------

    invalid_score = (

        investment_df[
            "Preference_Score"
        ]
        .notna()

        & (

            (
                investment_df[
                    "Preference_Score"
                ] < 1
            )

            |

            (
                investment_df[
                    "Preference_Score"
                ] > 7
            )
        )
    )

    print(
        f"Invalid preference scores: "
        f"{invalid_score.sum()}"
    )

    # --------------------------------------------------------
    # Expected return
    # --------------------------------------------------------

    if "Expected_Return_Range" in respondent_df.columns:

        print(
            "\nExpected Return:"
        )

        print(
            "✓ Preserved as categorical range."
        )

        print(
            "✓ No artificial average created."
        )

    print("\n" + "=" * 75)


# ============================================================
# 25. SAVE FEATURES
# ============================================================

def save_features(
    respondent_df,
    investment_df
):

    respondent_df.to_csv(

        RESPONDENT_FEATURE_FILE,

        index=False,

        encoding="utf-8"
    )

    investment_df.to_csv(

        INVESTMENT_FEATURE_FILE,

        index=False,

        encoding="utf-8"
    )

    print(
        f"\nRespondent features saved:"
        f"\n{RESPONDENT_FEATURE_FILE}"
    )

    print(
        f"\nInvestment features saved:"
        f"\n{INVESTMENT_FEATURE_FILE}"
    )


# ============================================================
# 26. MAIN PIPELINE
# ============================================================

def main():

    print("=" * 75)

    print(
        "INVESTMENT SURVEY — FEATURE ENGINEERING"
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    (
        respondent_df,
        investment_df
    ) = load_input_data()

    print(
        f"\nInput respondent rows:"
        f" {len(respondent_df)}"
    )

    print(
        f"Input investment rows:"
        f" {len(investment_df)}"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_input_data(

        respondent_df,

        investment_df
    )

    # ========================================================
    # RESPONDENT FEATURES
    # ========================================================

    print(
        "\nCreating respondent features..."
    )

    respondent_df = create_age_features(
        respondent_df
    )

    respondent_df = create_gender_features(
        respondent_df
    )

    respondent_df = create_duration_features(
        respondent_df
    )

    respondent_df = create_expected_return_features(
        respondent_df
    )

    respondent_df = create_objective_features(
        respondent_df
    )

    respondent_df = create_purpose_features(
        respondent_df
    )

    respondent_df = create_factor_features(
        respondent_df
    )

    respondent_df = create_avenue_features(
        respondent_df
    )

    respondent_df = create_monitoring_features(
        respondent_df
    )

    respondent_df = create_savings_features(
        respondent_df
    )

    respondent_df = create_source_features(
        respondent_df
    )

    # ========================================================
    # INVESTMENT FEATURES
    # ========================================================

    print(
        "\nCreating investment features..."
    )

    investment_df = create_investment_features(
        investment_df
    )

    investment_df = create_investment_keys(
        investment_df
    )

    # ========================================================
    # CROSS-ANALYSIS FEATURES
    # ========================================================

    print(
        "\nCombining respondent attributes "
        "with investment preferences..."
    )

    investment_df = create_cross_analysis_features(

        respondent_df,

        investment_df
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    validate_features(

        respondent_df,

        investment_df
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_features(

        respondent_df,

        investment_df
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 75)

    print(
        "FEATURE ENGINEERING COMPLETED"
    )

    print("=" * 75)

    print(
        "\nRespondent Feature Columns:"
    )

    for column in respondent_df.columns:

        print(
            f"  - {column}"
        )

    print(
        "\nInvestment Feature Columns:"
    )

    for column in investment_df.columns:

        print(
            f"  - {column}"
        )

    print("\nImportant business rules preserved:")

    print(
        "  ✓ Rank 1 = Highest Preference"
    )

    print(
        "  ✓ Lower Average Rank = Better Preference"
    )

    print(
        "  ✓ Preference Score: 8 - Rank"
    )

    print(
        "  ✓ Expected Return remains categorical"
    )

    print(
        "  ✓ No artificial average return created"
    )

    print(
        "  ✓ Respondent-level grain preserved"
    )

    print(
        "  ✓ Investment-level grain preserved"
    )

    print("\n" + "=" * 75)


# ============================================================
# 27. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()