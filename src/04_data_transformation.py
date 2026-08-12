"""
Investment Survey Analytics Project
------------------------------------

File:
    04_data_transformation.py

Purpose:
    Transform the cleaned Investment Survey dataset into
    analytical structures required for business analysis.

Main transformation:
    Wide investment preference columns
        ->
    Long investment preference table

Example:

    BEFORE

    Respondent_ID | Mutual_Funds | Equity_Market | Gold
    ----------------------------------------------------
    1              | 1            | 3             | 5
    2              | 4            | 1             | 2


    AFTER

    Respondent_ID | Investment_Type | Preference_Rank
    --------------------------------------------------
    1              | Mutual Funds    | 1
    1              | Equity Market   | 3
    1              | Gold            | 5
    2              | Mutual Funds    | 4
    2              | Equity Market   | 1
    2              | Gold            | 2


IMPORTANT BUSINESS RULE:

    Preference Rank 1 = Highest Preference
    Preference Rank 7 = Lowest Preference

Therefore:

    Lower Average Preference Rank
            =
    Higher Investment Preference

This script DOES NOT:
    - Create KPIs
    - Create dashboard visuals
    - Create recommendations
    - Calculate final business metrics

Those responsibilities belong to later modules.
"""


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

from pathlib import Path
import pandas as pd


# ============================================================
# 2. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA_DIR = (
    PROJECT_ROOT /
    "data" /
    "processed"
)

TRANSFORMED_DATA_DIR = (
    PROJECT_ROOT /
    "data" /
    "transformed"
)

TRANSFORMED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. INPUT / OUTPUT FILES
# ============================================================

INPUT_FILE = (
    PROCESSED_DATA_DIR /
    "investment_cleaned.csv"
)

INVESTMENT_LONG_FILE = (
    TRANSFORMED_DATA_DIR /
    "investment_long.csv"
)

RESPONDENT_FILE = (
    TRANSFORMED_DATA_DIR /
    "respondent_analysis.csv"
)

EXPECTED_RETURN_FILE = (
    TRANSFORMED_DATA_DIR /
    "expected_return_analysis.csv"
)


# ============================================================
# 4. INVESTMENT PREFERENCE COLUMNS
# ============================================================

# These are the original wide-format investment preference
# columns from your survey.

INVESTMENT_PREFERENCE_COLUMNS = [

    "Mutual_Funds",

    "Equity_Market",

    "Debentures",

    "Government_Bonds",

    "Fixed_Deposits",

    "PPF",

    "Gold"
]


# ============================================================
# 5. BUSINESS-FRIENDLY INVESTMENT NAMES
# ============================================================

# We preserve the original source column names internally,
# but expose professional business names in the analytical
# table.

INVESTMENT_NAME_MAP = {

    "Mutual_Funds":
        "Mutual Fund",

    "Equity_Market":
        "Equity",

    "Debentures":
        "Debenture",

    "Government_Bonds":
        "Government Bond",

    "Fixed_Deposits":
        "Fixed Deposit",

    "PPF":
        "PPF",

    "Gold":
        "Gold"
}


# ============================================================
# 6. LOAD CLEAN DATA
# ============================================================

def load_clean_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(

            "\nCleaned dataset not found.\n\n"

            f"Expected file:\n"
            f"{INPUT_FILE}\n\n"

            "Run 03_data_cleaning.py first."
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    return df


# ============================================================
# 7. VALIDATE INPUT
# ============================================================

def validate_input(df):

    required_columns = [

        "Respondent_ID",

        *INVESTMENT_PREFERENCE_COLUMNS
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(

            "\nRequired transformation columns "
            "are missing:\n"

            +
            "\n".join(

                f"  - {column}"

                for column in missing_columns
            )
        )


# ============================================================
# 8. CREATE INVESTMENT LONG TABLE
# ============================================================

def create_investment_long_table(df):

    """
    Convert investment preference columns from wide format
    into long analytical format.

    This reproduces the Power BI UNPIVOT operation.

    IMPORTANT:
        Respondent_ID is retained.

    Therefore each transformed row can still be traced
    back to its original respondent.
    """

    investment_long = df[
        [
            "Respondent_ID",

            *INVESTMENT_PREFERENCE_COLUMNS
        ]
    ].copy()

    # --------------------------------------------------------
    # UNPIVOT
    # --------------------------------------------------------

    investment_long = investment_long.melt(

        id_vars=[
            "Respondent_ID"
        ],

        value_vars=
            INVESTMENT_PREFERENCE_COLUMNS,

        var_name=
            "Investment_Type_Raw",

        value_name=
            "Preference_Rank"
    )

    # --------------------------------------------------------
    # Business-friendly investment name
    # --------------------------------------------------------

    investment_long[
        "Investment_Type"
    ] = (

        investment_long[
            "Investment_Type_Raw"
        ]

        .map(
            INVESTMENT_NAME_MAP
        )
    )

    # --------------------------------------------------------
    # Ensure preference rank is numeric
    # --------------------------------------------------------

    investment_long[
        "Preference_Rank"
    ] = pd.to_numeric(

        investment_long[
            "Preference_Rank"
        ],

        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove rows where no rank exists
    # --------------------------------------------------------

    investment_long = (
        investment_long[
            investment_long[
                "Preference_Rank"
            ].notna()
        ]
        .copy()
    )

    # --------------------------------------------------------
    # Validate ranking range
    # --------------------------------------------------------

    invalid_rank = (

        investment_long[
            "Preference_Rank"
        ].notna()

        & (

            (
                investment_long[
                    "Preference_Rank"
                ] < 1
            )

            |

            (
                investment_long[
                    "Preference_Rank"
                ] > 7
            )
        )
    )

    if invalid_rank.any():

        invalid_count = int(
            invalid_rank.sum()
        )

        raise ValueError(

            f"\n{invalid_count} invalid "
            "preference ranks detected.\n"

            "Expected ranking range: 1-7."
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    investment_long = (
        investment_long
        .sort_values(
            [
                "Respondent_ID",
                "Preference_Rank"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    return investment_long


# ============================================================
# 9. VALIDATE INVESTMENT RANKING STRUCTURE
# ============================================================

def validate_ranking_structure(
    investment_long
):

    """
    Check whether every respondent has a valid investment
    preference structure.

    Expected:

        7 investment categories
        per respondent.

    We don't silently fix violations.
    We report them.
    """

    respondent_counts = (

        investment_long
        .groupby(
            "Respondent_ID"
        )
        .size()
    )

    invalid_respondents = (
        respondent_counts[
            respondent_counts !=
            len(INVESTMENT_PREFERENCE_COLUMNS)
        ]
    )

    if not invalid_respondents.empty:

        print(
            "\nWARNING:"
        )

        print(
            f"{len(invalid_respondents)} "
            "respondents do not have exactly "
            f"{len(INVESTMENT_PREFERENCE_COLUMNS)} "
            "investment records."
        )

        print(
            "\nThis can occur because of missing "
            "preference values."
        )

    else:

        print(
            "\nRanking structure validated:"
        )

        print(
            "Every respondent has 7 investment records."
        )


# ============================================================
# 10. CREATE RESPONDENT ANALYSIS TABLE
# ============================================================

def create_respondent_analysis_table(
    df
):

    """
    Preserve one-row-per-respondent data.

    This table is critical for respondent-level KPIs.

    Examples:

        Total Respondents
        Average Investor Age
        Male Investors
        Female Investors
        Most Common Objective
        Most Trusted Information Source

    DO NOT use the investment_long table directly for
    respondent counts without DISTINCT Respondent_ID logic.
    """

    respondent_columns = [

        "Respondent_ID",

        "gender",

        "age",

        "Investment_Avenues",

        "Factor",

        "Objective",

        "Purpose",

        "Duration",

        "Invest_Monitor",

        "Expect",

        "Avenue",

        "What are your savings objectives?",

        "Reason_Equity",

        "Reason_Mutual",

        "Reason_Bonds",

        "Reason_FD",

        "Source"
    ]

    available_columns = [

        column

        for column in respondent_columns

        if column in df.columns
    ]

    respondent_analysis = (
        df[
            available_columns
        ]
        .drop_duplicates(
            subset=[
                "Respondent_ID"
            ]
        )
        .copy()
    )

    return respondent_analysis


# ============================================================
# 11. CREATE EXPECTED RETURN ANALYSIS TABLE
# ============================================================

def create_expected_return_table(
    df
):

    """
    Preserve Expected Return as a categorical range.

    Examples:

        10%-20%
        20%-30%
        30%-40%

    We do NOT convert these into numeric averages.

    This table is useful for:
        - Expected Return distribution
        - Most common expected return range
        - Expected return by gender
        - Expected return by age group
        - Expected return by investment objective
    """

    if "Expect" not in df.columns:

        return pd.DataFrame()

    expected_return = (

        df[
            [
                "Respondent_ID",
                "Expect"
            ]
        ]

        .copy()
    )

    expected_return = (
        expected_return
        .dropna(
            subset=[
                "Expect"
            ]
        )
    )

    expected_return = (
        expected_return
        .drop_duplicates(
            subset=[
                "Respondent_ID"
            ]
        )
    )

    return expected_return


# ============================================================
# 12. ADD INVESTMENT PREFERENCE ORDER
# ============================================================

def add_preference_order(
    investment_long
):

    """
    Create a business-friendly preference indicator.

    Lower rank = higher preference.

    Example:

        Rank 1 -> Preference Order 1
        Rank 7 -> Preference Order 7

    This may appear redundant, but explicitly naming the
    business rule makes downstream calculations safer.
    """

    investment_long = (
        investment_long
        .copy()
    )

    investment_long[
        "Preference_Level"
    ] = investment_long[
        "Preference_Rank"
    ].map(

        lambda x:

            "Highest Preference"
            if x == 1

            else

            "High Preference"
            if x == 2

            else

            "Moderate Preference"
            if x in [3, 4, 5]

            else

            "Low Preference"
            if x == 6

            else

            "Lowest Preference"
            if x == 7

            else

            "Unknown"
    )

    return investment_long


# ============================================================
# 13. ADD RESPONDENT INVESTMENT COUNT
# ============================================================

def add_investment_count(
    investment_long
):

    """
    Add the number of valid investment records associated
    with each respondent.

    This is NOT the same as respondent count.
    """

    counts = (

        investment_long
        .groupby(
            "Respondent_ID"
        )
        .size()
        .rename(
            "Investment_Record_Count"
        )
    )

    investment_long = (
        investment_long
        .merge(
            counts,
            on="Respondent_ID",
            how="left"
        )
    )

    return investment_long


# ============================================================
# 14. CREATE ANALYTICAL KEYS
# ============================================================

def create_analysis_keys(
    respondent_df,
    investment_df
):

    """
    Create simple analytical keys without changing business
    values.

    These keys will help later with joins and dashboard
    filtering.
    """

    respondent_df = respondent_df.copy()

    investment_df = investment_df.copy()

    # --------------------------------------------------------
    # Gender key
    # --------------------------------------------------------

    if "gender" in respondent_df.columns:

        respondent_df[
            "Gender_Key"
        ] = (

            respondent_df[
                "gender"
            ]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # --------------------------------------------------------
    # Investment key
    # --------------------------------------------------------

    investment_df[
        "Investment_Key"
    ] = (

        investment_df[
            "Investment_Type"
        ]

        .astype("string")

        .str.lower()

        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    return (
        respondent_df,
        investment_df
    )


# ============================================================
# 15. SAVE TABLE
# ============================================================

def save_table(
    df,
    output_file
):

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"Saved:\n"
        f"  {output_file}"
    )


# ============================================================
# 16. CREATE TRANSFORMATION SUMMARY
# ============================================================

def create_transformation_summary(
    respondent_df,
    investment_df
):

    respondents = (
        respondent_df[
            "Respondent_ID"
        ]
        .nunique()
    )

    investment_rows = len(
        investment_df
    )

    investment_types = (
        investment_df[
            "Investment_Type"
        ]
        .nunique()
    )

    summary = {

        "respondents":
            int(respondents),

        "investment_records":
            int(investment_rows),

        "investment_types":
            int(investment_types),

        "expected_records_per_respondent":
            len(
                INVESTMENT_PREFERENCE_COLUMNS
            ),

        "average_investment_records_per_respondent":
            round(
                investment_rows /
                max(respondents, 1),
                2
            )
    }

    return summary


# ============================================================
# 17. MAIN TRANSFORMATION PIPELINE
# ============================================================

def main():

    print("=" * 75)

    print(
        "INVESTMENT SURVEY — DATA TRANSFORMATION"
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_clean_data()

    print(
        f"\nClean dataset loaded:"
        f"\n  Rows    : {df.shape[0]}"
        f"\n  Columns : {df.shape[1]}"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_input(
        df
    )

    # --------------------------------------------------------
    # Create long investment table
    # --------------------------------------------------------

    investment_long = (
        create_investment_long_table(
            df
        )
    )

    # --------------------------------------------------------
    # Validate ranking
    # --------------------------------------------------------

    validate_ranking_structure(
        investment_long
    )

    # --------------------------------------------------------
    # Add business classification
    # --------------------------------------------------------

    investment_long = (
        add_preference_order(
            investment_long
        )
    )

    # --------------------------------------------------------
    # Add investment count
    # --------------------------------------------------------

    investment_long = (
        add_investment_count(
            investment_long
        )
    )

    # --------------------------------------------------------
    # Create respondent-level table
    # --------------------------------------------------------

    respondent_analysis = (
        create_respondent_analysis_table(
            df
        )
    )

    # --------------------------------------------------------
    # Create expected return table
    # --------------------------------------------------------

    expected_return = (
        create_expected_return_table(
            df
        )
    )

    # --------------------------------------------------------
    # Create analytical keys
    # --------------------------------------------------------

    (
        respondent_analysis,
        investment_long
    ) = create_analysis_keys(

        respondent_analysis,

        investment_long
    )

    # --------------------------------------------------------
    # Save investment table
    # --------------------------------------------------------

    save_table(
        investment_long,
        INVESTMENT_LONG_FILE
    )

    # --------------------------------------------------------
    # Save respondent table
    # --------------------------------------------------------

    save_table(
        respondent_analysis,
        RESPONDENT_FILE
    )

    # --------------------------------------------------------
    # Save expected return table
    # --------------------------------------------------------

    if not expected_return.empty:

        save_table(
            expected_return,
            EXPECTED_RETURN_FILE
        )

    # --------------------------------------------------------
    # Transformation summary
    # --------------------------------------------------------

    summary = (
        create_transformation_summary(
            respondent_analysis,
            investment_long
        )
    )

    # ========================================================
    # CONSOLE REPORT
    # ========================================================

    print("\n")
    print("=" * 75)

    print(
        "TRANSFORMATION COMPLETED"
    )

    print("=" * 75)

    print(
        f"\nUnique Respondents"
        f"                  : "
        f"{summary['respondents']}"
    )

    print(
        f"Investment Records"
        f"                  : "
        f"{summary['investment_records']}"
    )

    print(
        f"Investment Types"
        f"                    : "
        f"{summary['investment_types']}"
    )

    print(
        f"Expected Investment Records"
        f"         : "
        f"{summary['expected_records_per_respondent']}"
    )

    print(
        f"Average Records / Respondent"
        f"       : "
        f"{summary['average_investment_records_per_respondent']}"
    )

    print("\nInvestment Types:")

    for investment in sorted(
        investment_long[
            "Investment_Type"
        ]
        .dropna()
        .unique()
    ):

        print(
            f"  - {investment}"
        )

    print("\nOutput tables:")

    print(
        f"  1. {INVESTMENT_LONG_FILE}"
    )

    print(
        f"  2. {RESPONDENT_FILE}"
    )

    if not expected_return.empty:

        print(
            f"  3. {EXPECTED_RETURN_FILE}"
        )

    print("\nImportant analytical rule:")

    print(
        "  Rank 1 = Highest Preference"
    )

    print(
        "  Lower Average Rank = Higher Preference"
    )

    print("\n" + "=" * 75)


# ============================================================
# 18. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()