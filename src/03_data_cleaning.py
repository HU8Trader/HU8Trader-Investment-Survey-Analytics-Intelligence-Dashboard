"""
Investment Survey Analytics Project
------------------------------------

File:
    03_data_cleaning.py

Purpose:
    Clean the raw Investment Survey dataset while preserving
    analytical meaning and respondent-level granularity.

IMPORTANT:
    This module performs CLEANING only.

    It does NOT:
        - Unpivot investment columns
        - Create investment_type
        - Create analytical dimensions
        - Calculate KPIs
        - Calculate DAX-equivalent business metrics
        - Build dashboards

Those responsibilities belong to later modules.

Cleaning principles:
    1. Preserve the original business meaning.
    2. Do not silently delete information.
    3. Preserve categorical responses.
    4. Create a stable Respondent_ID.
    5. Standardize text.
    6. Standardize numeric columns.
    7. Handle blanks consistently.
    8. Preserve Expected Return as a categorical range.
    9. Validate investment preference rankings.
    10. Save a clean respondent-level dataset.
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

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. INPUT / OUTPUT FILE
# ============================================================

INPUT_FILE = RAW_DATA_DIR / "investment.csv"

OUTPUT_FILE = (
    PROCESSED_DATA_DIR /
    "investment_cleaned.csv"
)


# ============================================================
# 4. SOURCE COLUMN DEFINITIONS
# ============================================================

# These are the columns from your original Investment Survey
# dataset.
#
# We deliberately keep their names at this stage.
#
# Business-friendly analytical names will be created later.

EXPECTED_COLUMNS = [

    "gender",

    "age",

    "Investment_Avenues",

    "Mutual_Funds",

    "Equity_Market",

    "Debentures",

    "Government_Bonds",

    "Fixed_Deposits",

    "PPF",

    "Gold",

    "Stock_Marktet",

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


# ============================================================
# 5. INVESTMENT PREFERENCE COLUMNS
# ============================================================

# These columns contain the respondent's investment
# preference ranking.
#
# IMPORTANT BUSINESS RULE:
#
#       Rank 1 = Highest Preference
#       Rank 7 = Lowest Preference
#
# Therefore:
#
#       LOWER AVERAGE RANK = BETTER PREFERENCE
#
# This rule will be explicitly preserved for later
# analytical calculations.

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
# 6. EXPECTED RETURN RANGE VALUES
# ============================================================

# Your dataset contains Expected Return as TEXT ranges.
#
# Examples:
#
#     10%-20%
#     20%-30%
#     30%-40%
#
# It is NOT a numeric percentage.
#
# Therefore we DO NOT convert it into a single numeric
# percentage here.
#
# Later analysis can use:
#
#     Most Common Expected Return Range
#
# rather than:
#
#     Average Expected Return
#
# unless a specific midpoint assumption is explicitly
# introduced.

EXPECTED_RETURN_PATTERN = re.compile(
    r"^\s*\d+\s*%\s*-\s*\d+\s*%\s*$"
)


# ============================================================
# 7. HELPER: CLEAN TEXT
# ============================================================

def clean_text(value):
    """
    Standardize textual survey responses.

    Operations:
        - Convert blank-like values to pd.NA
        - Remove leading/trailing spaces
        - Collapse repeated internal spaces
        - Preserve original wording/case as much as possible
    """

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value == "":
        return pd.NA

    # Convert multiple spaces to one
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# 8. HELPER: NORMALIZE CATEGORY
# ============================================================

def normalize_category(value):
    """
    Standardize categorical survey values.

    This function intentionally does NOT aggressively rename
    categories because survey wording is business information.

    Example:
        ' Mutual Fund '
            ->
        'Mutual Fund'
    """

    value = clean_text(value)

    if pd.isna(value):
        return pd.NA

    return value


# ============================================================
# 9. LOAD RAW DATA
# ============================================================

def load_raw_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "\nRaw Investment Survey CSV was not found.\n\n"
            f"Expected location:\n{INPUT_FILE}\n\n"
            "Place the original CSV inside:\n"
            "data/raw/"
        )

    try:

        df = pd.read_csv(
            INPUT_FILE
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="latin1"
        )

    return df


# ============================================================
# 10. VALIDATE SOURCE COLUMNS
# ============================================================

def validate_source_columns(df):

    missing_columns = [

        column

        for column in EXPECTED_COLUMNS

        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nRequired source columns are missing:\n"
            +
            "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
        )


# ============================================================
# 11. STANDARDIZE COLUMN NAMES
# ============================================================

def standardize_column_names(df):

    df = df.copy()

    df.columns = [

        str(column).strip()

        for column in df.columns
    ]

    return df


# ============================================================
# 12. STANDARDIZE TEXT COLUMNS
# ============================================================

def clean_text_columns(df):

    df = df.copy()

    for column in df.columns:

        # Preference columns should remain numeric.
        if column in INVESTMENT_PREFERENCE_COLUMNS:
            continue

        # Age should remain numeric.
        if column == "age":
            continue

        df[column] = (
            df[column]
            .apply(clean_text)
        )

    return df


# ============================================================
# 13. CLEAN AGE
# ============================================================

def clean_age(df):

    df = df.copy()

    if "age" not in df.columns:
        return df

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

    # Invalid ages are treated as missing.
    #
    # We do NOT delete the respondent here.
    #
    # Later validation decides whether the record should
    # be excluded from a particular age-based analysis.

    invalid_age = (

        df["age"].notna()

        & (
            (df["age"] < 0)
            | (df["age"] > 120)
        )
    )

    df.loc[
        invalid_age,
        "age"
    ] = pd.NA

    return df


# ============================================================
# 14. CLEAN INVESTMENT PREFERENCE RANKS
# ============================================================

def clean_investment_preferences(df):

    df = df.copy()

    for column in INVESTMENT_PREFERENCE_COLUMNS:

        if column not in df.columns:
            continue

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Valid ranks in your survey are expected to be
        # between 1 and 7.

        invalid_rank = (

            df[column].notna()

            & (
                (df[column] < 1)
                | (df[column] > 7)
            )
        )

        df.loc[
            invalid_rank,
            column
        ] = pd.NA

    return df


# ============================================================
# 15. CLEAN EXPECTED RETURN
# ============================================================

def clean_expected_return(df):

    df = df.copy()

    if "Expect" not in df.columns:
        return df

    df["Expect"] = (
        df["Expect"]
        .apply(clean_text)
    )

    # Validate expected-return format.
    #
    # We DO NOT convert:
    #
    #     10%-20%
    #
    # into:
    #
    #     15
    #
    # because that would introduce a new assumption.

    invalid_return_values = []

    for value in df["Expect"].dropna().unique():

        if not EXPECTED_RETURN_PATTERN.match(
            str(value)
        ):

            invalid_return_values.append(
                value
            )

    if invalid_return_values:

        print(
            "\nWARNING:"
            "\nUnexpected Expected Return values detected:"
        )

        for value in invalid_return_values:

            print(
                f"  - {value}"
            )

    return df


# ============================================================
# 16. CREATE RESPONDENT ID
# ============================================================

def create_respondent_id(df):

    df = df.copy()

    # Your raw dataset does not contain a dedicated
    # Respondent_ID.
    #
    # Each raw row represents one survey respondent.
    #
    # Therefore we create a stable sequential identifier.

    df.insert(
        0,
        "Respondent_ID",
        range(
            1,
            len(df) + 1
        )
    )

    return df


# ============================================================
# 17. CHECK DUPLICATE RESPONDENTS
# ============================================================

def check_duplicate_respondents(df):

    if "Respondent_ID" not in df.columns:
        return

    duplicate_ids = (
        df["Respondent_ID"]
        .duplicated()
        .sum()
    )

    if duplicate_ids > 0:

        raise ValueError(
            f"Duplicate Respondent_ID values detected: "
            f"{duplicate_ids}"
        )


# ============================================================
# 18. HANDLE COMPLETELY DUPLICATE ROWS
# ============================================================

def handle_duplicate_rows(df):

    df = df.copy()

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        print(
            f"\nWARNING: "
            f"{duplicate_count} completely duplicated "
            f"rows detected."
        )

        # Important:
        #
        # We do NOT automatically delete duplicates.
        #
        # Because survey duplication may be a data-quality
        # issue that requires investigation.
        #
        # However, if the same Respondent_ID appears twice,
        # that is a separate problem.

        print(
            "Duplicate rows will be preserved for auditability."
        )

    return df


# ============================================================
# 19. HANDLE BLANK STRINGS
# ============================================================

def replace_blank_strings(df):

    df = df.copy()

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .replace(
                    r"^\s*$",
                    pd.NA,
                    regex=True
                )
            )

    return df


# ============================================================
# 20. CREATE CLEANING SUMMARY
# ============================================================

def create_cleaning_summary(
    raw_df,
    clean_df
):

    summary = {

        "raw_rows":
            int(len(raw_df)),

        "clean_rows":
            int(len(clean_df)),

        "raw_columns":
            int(len(raw_df.columns)),

        "clean_columns":
            int(len(clean_df.columns)),

        "rows_removed":
            int(len(raw_df) - len(clean_df)),

        "columns_removed":
            int(
                len(raw_df.columns)
                -
                len(clean_df.columns)
            ),

        "raw_missing_values":
            int(
                raw_df.isna()
                .sum()
                .sum()
            ),

        "clean_missing_values":
            int(
                clean_df.isna()
                .sum()
                .sum()
            ),

        "clean_duplicate_rows":
            int(
                clean_df.duplicated()
                .sum()
            )
    }

    return summary


# ============================================================
# 21. SAVE CLEAN DATASET
# ============================================================

def save_clean_dataset(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nClean dataset saved to:\n"
        f"{OUTPUT_FILE}"
    )


# ============================================================
# 22. MAIN CLEANING PIPELINE
# ============================================================

def main():

    print("=" * 75)

    print(
        "INVESTMENT SURVEY — DATA CLEANING PIPELINE"
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    raw_df = load_raw_data()

    print(
        f"\nRaw dataset:"
        f"\n  Rows    : {raw_df.shape[0]}"
        f"\n  Columns : {raw_df.shape[1]}"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_source_columns(
        raw_df
    )

    # --------------------------------------------------------
    # Standardize column names
    # --------------------------------------------------------

    df = standardize_column_names(
        raw_df
    )

    # --------------------------------------------------------
    # Blank values
    # --------------------------------------------------------

    df = replace_blank_strings(
        df
    )

    # --------------------------------------------------------
    # Text cleaning
    # --------------------------------------------------------

    df = clean_text_columns(
        df
    )

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    df = clean_age(
        df
    )

    # --------------------------------------------------------
    # Investment preference ranks
    # --------------------------------------------------------

    df = clean_investment_preferences(
        df
    )

    # --------------------------------------------------------
    # Expected return
    # --------------------------------------------------------

    df = clean_expected_return(
        df
    )

    # --------------------------------------------------------
    # Duplicate handling
    # --------------------------------------------------------

    df = handle_duplicate_rows(
        df
    )

    # --------------------------------------------------------
    # Respondent ID
    # --------------------------------------------------------

    df = create_respondent_id(
        df
    )

    # --------------------------------------------------------
    # Validate respondent IDs
    # --------------------------------------------------------

    check_duplicate_respondents(
        df
    )

    # --------------------------------------------------------
    # Cleaning summary
    # --------------------------------------------------------

    summary = create_cleaning_summary(
        raw_df,
        df
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_clean_dataset(
        df
    )

    # --------------------------------------------------------
    # Console report
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("CLEANING COMPLETED")
    print("=" * 75)

    print(
        f"\nRows before cleaning : "
        f"{summary['raw_rows']}"
    )

    print(
        f"Rows after cleaning  : "
        f"{summary['clean_rows']}"
    )

    print(
        f"Rows removed         : "
        f"{summary['rows_removed']}"
    )

    print(
        f"\nColumns before       : "
        f"{summary['raw_columns']}"
    )

    print(
        f"Columns after        : "
        f"{summary['clean_columns']}"
    )

    print(
        f"\nMissing values before: "
        f"{summary['raw_missing_values']}"
    )

    print(
        f"Missing values after : "
        f"{summary['clean_missing_values']}"
    )

    print(
        f"\nDuplicate rows       : "
        f"{summary['clean_duplicate_rows']}"
    )

    print(
        "\nImportant:"
        "\n  ✓ Investment columns remain wide."
        "\n  ✓ No unpivoting performed."
        "\n  ✓ Expected Return remains categorical."
        "\n  ✓ Preference rank meaning preserved."
        "\n  ✓ Respondent-level grain preserved."
    )

    print("\n" + "=" * 75)


# ============================================================
# 23. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()