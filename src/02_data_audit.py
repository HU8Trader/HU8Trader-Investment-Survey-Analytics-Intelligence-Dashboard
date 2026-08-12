"""
Investment Survey Analytics Project
-----------------------------------
File: 02_data_audit.py

Purpose:
    Perform a comprehensive data-quality and structural audit
    of the Investment Survey dataset.

This script DOES NOT clean or transform the data.

It identifies:
    - Dataset dimensions
    - Column names
    - Data types
    - Missing values
    - Duplicate rows
    - Unique values
    - Blank values
    - Potential numeric/text inconsistencies
    - Potential categorical columns
    - Expected-return range columns
    - Preference-ranking columns
    - Respondent ID duplication
    - Unpivot-related row multiplication
    - Potential data-quality issues

Outputs:
    data/audit/column_audit.csv
    data/audit/duplicate_rows.csv
    data/audit/audit_summary.txt
"""

from pathlib import Path
import json
import re
import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
AUDIT_DIR = PROJECT_ROOT / "data" / "audit"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FIND INPUT CSV
# ============================================================

def find_input_csv():
    """
    Locate the Investment Survey CSV file.

    Priority:
        1. investment*.csv
        2. *.csv

    Returns:
        Path object
    """

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory does not exist:\n{RAW_DATA_DIR}"
        )

    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in:\n{RAW_DATA_DIR}\n\n"
            "Place your raw Investment Survey CSV inside data/raw/"
        )

    # Prefer files containing investment
    investment_files = [
        file for file in csv_files
        if "investment" in file.name.lower()
    ]

    if investment_files:
        return investment_files[0]

    # Otherwise use first CSV
    return csv_files[0]


# ============================================================
# 3. LOAD DATA
# ============================================================

def load_data(file_path):
    """
    Load CSV without performing transformations.
    """

    print("=" * 70)
    print("INVESTMENT SURVEY — DATA AUDIT")
    print("=" * 70)

    print(f"\nInput file:")
    print(file_path)

    df = pd.read_csv(file_path)

    print("\nDataset loaded successfully.")

    return df


# ============================================================
# 4. STANDARDIZE COLUMN NAME FOR INTERNAL DETECTION
# ============================================================

def normalize_column_name(column):
    """
    Normalize column names only for detection.
    Original column names remain unchanged.
    """

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


# ============================================================
# 5. BASIC DATASET PROFILE
# ============================================================

def profile_dataset(df):

    rows, columns = df.shape

    profile = {
        "total_rows": int(rows),
        "total_columns": int(columns),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 ** 2),
            2
        ),
        "total_duplicate_rows": int(df.duplicated().sum()),
    }

    return profile


# ============================================================
# 6. COLUMN-LEVEL AUDIT
# ============================================================

def audit_columns(df):

    audit_records = []

    total_rows = len(df)

    for column in df.columns:

        series = df[column]

        null_count = int(series.isna().sum())

        blank_count = int(
            series.astype("string")
            .str.strip()
            .eq("")
            .sum()
        )

        unique_count = int(series.nunique(dropna=True))

        duplicate_count = int(
            series.duplicated().sum()
        )

        non_null_count = total_rows - null_count

        if non_null_count > 0:
            missing_percentage = round(
                (null_count / total_rows) * 100,
                2
            )
        else:
            missing_percentage = 100.0

        # Detect possible numeric values stored as text
        numeric_conversion = pd.to_numeric(
            series,
            errors="coerce"
        )

        numeric_like_percentage = round(
            (
                numeric_conversion.notna().sum()
                / max(non_null_count, 1)
            ) * 100,
            2
        )

        # Detect percentage/range values
        text_values = (
            series.dropna()
            .astype(str)
            .str.strip()
        )

        percentage_range_count = int(
            text_values.str.match(
                r"^\d+\s*%\s*-\s*\d+\s*%$"
            ).sum()
        )

        audit_records.append({

            "Column": column,

            "Data_Type": str(series.dtype),

            "Total_Rows": total_rows,

            "Non_Null": non_null_count,

            "Null_Count": null_count,

            "Missing_%": missing_percentage,

            "Blank_Count": blank_count,

            "Unique_Values": unique_count,

            "Duplicate_Values": duplicate_count,

            "Numeric_Like_%": numeric_like_percentage,

            "Expected_Return_Range_Values":
                percentage_range_count,

            "Sample_Values":
                " | ".join(
                    text_values
                    .drop_duplicates()
                    .head(5)
                    .tolist()
                )
        })

    return pd.DataFrame(audit_records)


# ============================================================
# 7. RESPONDENT ID ANALYSIS
# ============================================================

def analyze_respondent_id(df):

    normalized = {
        normalize_column_name(col): col
        for col in df.columns
    }

    possible_id_columns = [
        "respondent_id",
        "respondentid",
        "respondent",
        "id"
    ]

    respondent_column = None

    for candidate in possible_id_columns:

        if candidate in normalized:
            respondent_column = normalized[candidate]
            break

    if respondent_column is None:

        return {
            "respondent_id_found": False,
            "respondent_column": None,
            "unique_respondents": None,
            "rows": len(df),
            "duplicate_respondent_rows": None
        }

    series = df[respondent_column]

    unique_respondents = series.nunique(dropna=True)

    duplicate_rows = int(
        series.duplicated(keep=False).sum()
    )

    return {
        "respondent_id_found": True,
        "respondent_column": respondent_column,
        "unique_respondents": int(unique_respondents),
        "rows": int(len(df)),
        "duplicate_respondent_rows": duplicate_rows,
        "rows_per_respondent":
            round(len(df) / max(unique_respondents, 1), 2)
    }


# ============================================================
# 8. EXPECTED RETURN ANALYSIS
# ============================================================

def analyze_expected_return(df):

    expected_columns = []

    for column in df.columns:

        normalized = normalize_column_name(column)

        if (
            "expect" in normalized
            or "return" in normalized
        ):
            expected_columns.append(column)

    results = []

    for column in expected_columns:

        series = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        range_values = sorted(
            series[
                series.str.match(
                    r"^\d+\s*%\s*-\s*\d+\s*%$"
                )
            ].unique()
        )

        numeric_count = pd.to_numeric(
            series,
            errors="coerce"
        ).notna().sum()

        results.append({
            "column": column,
            "unique_values": int(series.nunique()),
            "range_values": range_values,
            "numeric_values_detected": int(numeric_count)
        })

    return results


# ============================================================
# 9. PREFERENCE RANK ANALYSIS
# ============================================================

def analyze_preference_columns(df):

    preference_columns = []

    for column in df.columns:

        normalized = normalize_column_name(column)

        if (
            "preference" in normalized
            or "rank" in normalized
            or "score" in normalized
        ):
            preference_columns.append(column)

    results = []

    for column in preference_columns:

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        results.append({

            "column": column,

            "numeric_values":
                int(series.notna().sum()),

            "minimum":
                float(series.min())
                if series.notna().any()
                else None,

            "maximum":
                float(series.max())
                if series.notna().any()
                else None,

            "average":
                round(float(series.mean()), 2)
                if series.notna().any()
                else None,

            "unique_numeric_values":
                int(series.nunique())
        })

    return results


# ============================================================
# 10. UNPIVOT / ROW MULTIPLICATION ANALYSIS
# ============================================================

def analyze_unpivot_structure(df):

    normalized = {
        normalize_column_name(col): col
        for col in df.columns
    }

    investment_column = None

    possible_names = [
        "investment_type",
        "investment",
        "investment_type_name",
        "avenue"
    ]

    for name in possible_names:

        if name in normalized:
            investment_column = normalized[name]
            break

    if investment_column is None:

        return {
            "investment_type_found": False,
            "investment_column": None,
            "unique_investment_types": None,
            "investment_type_values": []
        }

    values = (
        df[investment_column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    return {

        "investment_type_found": True,

        "investment_column":
            investment_column,

        "unique_investment_types":
            int(values.nunique()),

        "investment_type_values":
            sorted(values.unique().tolist()),

        "rows":
            int(len(df))
    }


# ============================================================
# 11. CATEGORICAL COLUMN ANALYSIS
# ============================================================

def analyze_categorical_columns(df):

    categorical = []

    for column in df.columns:

        series = df[column]

        unique_count = series.nunique(
            dropna=True
        )

        if (
            series.dtype == "object"
            and unique_count <= 30
        ):

            values = (
                series
                .dropna()
                .astype(str)
                .str.strip()
                .value_counts()
                .head(15)
            )

            categorical.append({

                "column": column,

                "unique_values":
                    int(unique_count),

                "top_values":
                    values.to_dict()
            })

    return categorical


# ============================================================
# 12. POTENTIAL DATA QUALITY ISSUES
# ============================================================

def identify_quality_issues(df, column_audit):

    issues = []

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_columns = column_audit[
        column_audit["Missing_%"] > 0
    ]

    for _, row in missing_columns.iterrows():

        severity = (
            "HIGH"
            if row["Missing_%"] >= 20
            else "MEDIUM"
        )

        issues.append({

            "severity": severity,

            "category": "Missing Values",

            "column": row["Column"],

            "issue":
                f"{row['Missing_%']}% values are missing."
        })

    # --------------------------------------------------------
    # Completely blank columns
    # --------------------------------------------------------

    blank_columns = column_audit[
        column_audit["Non_Null"] == 0
    ]

    for _, row in blank_columns.iterrows():

        issues.append({

            "severity": "HIGH",

            "category": "Empty Column",

            "column": row["Column"],

            "issue":
                "Column contains no usable values."
        })

    # --------------------------------------------------------
    # Numeric data stored as text
    # --------------------------------------------------------

    for _, row in column_audit.iterrows():

        if (
            row["Data_Type"] == "object"
            and row["Numeric_Like_%"] >= 90
            and row["Unique_Values"] > 1
        ):

            issues.append({

                "severity": "MEDIUM",

                "category":
                    "Potential Numeric-as-Text",

                "column":
                    row["Column"],

                "issue":
                    "Column appears to contain mostly "
                    "numeric values but is stored as text."
            })

    # --------------------------------------------------------
    # Expected-return ranges
    # --------------------------------------------------------

    expected_columns = column_audit[
        column_audit[
            "Expected_Return_Range_Values"
        ] > 0
    ]

    for _, row in expected_columns.iterrows():

        issues.append({

            "severity": "INFO",

            "category":
                "Expected Return Range",

            "column":
                row["Column"],

            "issue":
                "Expected return is stored as text "
                "ranges such as 10%-20%, 20%-30%, etc. "
                "It should not be averaged directly."
        })

    # --------------------------------------------------------
    # Duplicate complete rows
    # --------------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        issues.append({

            "severity": "MEDIUM",

            "category":
                "Duplicate Rows",

            "column":
                "DATASET",

            "issue":
                f"{duplicate_count} completely "
                "duplicated rows detected."
        })

    return issues


# ============================================================
# 13. SAVE DUPLICATE ROWS
# ============================================================

def save_duplicate_rows(df):

    duplicates = df[
        df.duplicated(
            keep=False
        )
    ].copy()

    output_file = (
        AUDIT_DIR /
        "duplicate_rows.csv"
    )

    if not duplicates.empty:

        duplicates.to_csv(
            output_file,
            index=False
        )

    else:

        # Create an empty file with same columns
        duplicates.to_csv(
            output_file,
            index=False
        )

    return output_file


# ============================================================
# 14. CREATE TEXT SUMMARY
# ============================================================

def create_summary(
    file_path,
    profile,
    column_audit,
    respondent_analysis,
    expected_analysis,
    preference_analysis,
    unpivot_analysis,
    categorical_analysis,
    quality_issues
):

    output_file = (
        AUDIT_DIR /
        "audit_summary.txt"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "=" * 80 +
            "\n"
        )

        file.write(
            "INVESTMENT SURVEY — DATA AUDIT REPORT\n"
        )

        file.write(
            "=" * 80 +
            "\n\n"
        )

        # ----------------------------------------------------
        # Dataset overview
        # ----------------------------------------------------

        file.write(
            "1. DATASET OVERVIEW\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        file.write(
            f"Input File: {file_path.name}\n"
        )

        file.write(
            f"Rows: {profile['total_rows']}\n"
        )

        file.write(
            f"Columns: {profile['total_columns']}\n"
        )

        file.write(
            f"Memory Usage: "
            f"{profile['memory_usage_mb']} MB\n"
        )

        file.write(
            f"Duplicate Rows: "
            f"{profile['total_duplicate_rows']}\n\n"
        )

        # ----------------------------------------------------
        # Column list
        # ----------------------------------------------------

        file.write(
            "2. COLUMN INVENTORY\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        for index, column in enumerate(
            column_audit["Column"],
            start=1
        ):

            file.write(
                f"{index}. {column}\n"
            )

        file.write("\n")

        # ----------------------------------------------------
        # Respondent analysis
        # ----------------------------------------------------

        file.write(
            "3. RESPONDENT ANALYSIS\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        file.write(
            json.dumps(
                respondent_analysis,
                indent=4
            )
        )

        file.write("\n\n")

        # ----------------------------------------------------
        # Expected return
        # ----------------------------------------------------

        file.write(
            "4. EXPECTED RETURN ANALYSIS\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        file.write(
            json.dumps(
                expected_analysis,
                indent=4
            )
        )

        file.write("\n\n")

        # ----------------------------------------------------
        # Preference ranking
        # ----------------------------------------------------

        file.write(
            "5. PREFERENCE / RANK ANALYSIS\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        file.write(
            json.dumps(
                preference_analysis,
                indent=4
            )
        )

        file.write("\n\n")

        # ----------------------------------------------------
        # Unpivot
        # ----------------------------------------------------

        file.write(
            "6. UNPIVOT STRUCTURE\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        file.write(
            json.dumps(
                unpivot_analysis,
                indent=4
            )
        )

        file.write("\n\n")

        # ----------------------------------------------------
        # Quality issues
        # ----------------------------------------------------

        file.write(
            "7. DATA QUALITY ISSUES\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        if not quality_issues:

            file.write(
                "No major quality issues detected.\n"
            )

        else:

            for number, issue in enumerate(
                quality_issues,
                start=1
            ):

                file.write(
                    f"\n{number}. "
                    f"[{issue['severity']}] "
                    f"{issue['category']}\n"
                )

                file.write(
                    f"   Column: "
                    f"{issue['column']}\n"
                )

                file.write(
                    f"   Issue: "
                    f"{issue['issue']}\n"
                )

        file.write("\n")

        # ----------------------------------------------------
        # Categorical columns
        # ----------------------------------------------------

        file.write(
            "8. CATEGORICAL COLUMN SUMMARY\n"
        )

        file.write(
            "-" * 80 +
            "\n"
        )

        for item in categorical_analysis:

            file.write(
                f"\nColumn: "
                f"{item['column']}\n"
            )

            file.write(
                f"Unique Values: "
                f"{item['unique_values']}\n"
            )

            for value, count in item[
                "top_values"
            ].items():

                file.write(
                    f"    {value}: {count}\n"
                )

    return output_file


# ============================================================
# 15. MAIN AUDIT PIPELINE
# ============================================================

def main():

    try:

        # ----------------------------------------------------
        # Locate data
        # ----------------------------------------------------

        input_file = find_input_csv()

        # ----------------------------------------------------
        # Load
        # ----------------------------------------------------

        df = load_data(
            input_file
        )

        # ----------------------------------------------------
        # Basic profile
        # ----------------------------------------------------

        profile = profile_dataset(
            df
        )

        # ----------------------------------------------------
        # Column audit
        # ----------------------------------------------------

        column_audit = audit_columns(
            df
        )

        column_audit_file = (
            AUDIT_DIR /
            "column_audit.csv"
        )

        column_audit.to_csv(
            column_audit_file,
            index=False
        )

        # ----------------------------------------------------
        # Respondent analysis
        # ----------------------------------------------------

        respondent_analysis = (
            analyze_respondent_id(df)
        )

        # ----------------------------------------------------
        # Expected return analysis
        # ----------------------------------------------------

        expected_analysis = (
            analyze_expected_return(df)
        )

        # ----------------------------------------------------
        # Preference analysis
        # ----------------------------------------------------

        preference_analysis = (
            analyze_preference_columns(df)
        )

        # ----------------------------------------------------
        # Unpivot analysis
        # ----------------------------------------------------

        unpivot_analysis = (
            analyze_unpivot_structure(df)
        )

        # ----------------------------------------------------
        # Categorical analysis
        # ----------------------------------------------------

        categorical_analysis = (
            analyze_categorical_columns(df)
        )

        # ----------------------------------------------------
        # Quality issues
        # ----------------------------------------------------

        quality_issues = (
            identify_quality_issues(
                df,
                column_audit
            )
        )

        # ----------------------------------------------------
        # Duplicate rows
        # ----------------------------------------------------

        duplicate_file = (
            save_duplicate_rows(df)
        )

        # ----------------------------------------------------
        # Summary report
        # ----------------------------------------------------

        summary_file = create_summary(

            input_file,

            profile,

            column_audit,

            respondent_analysis,

            expected_analysis,

            preference_analysis,

            unpivot_analysis,

            categorical_analysis,

            quality_issues
        )

        # ====================================================
        # CONSOLE REPORT
        # ====================================================

        print("\n")
        print("=" * 70)
        print("DATA AUDIT COMPLETED")
        print("=" * 70)

        print(
            f"\nRows                  : "
            f"{profile['total_rows']}"
        )

        print(
            f"Columns               : "
            f"{profile['total_columns']}"
        )

        print(
            f"Duplicate Rows        : "
            f"{profile['total_duplicate_rows']}"
        )

        print(
            f"Missing Columns       : "
            f"{sum(column_audit['Missing_%'] > 0)}"
        )

        print(
            f"Potential Issues      : "
            f"{len(quality_issues)}"
        )

        print(
            f"\nRespondent ID Found   : "
            f"{respondent_analysis['respondent_id_found']}"
        )

        if respondent_analysis[
            "respondent_id_found"
        ]:

            print(
                f"Unique Respondents    : "
                f"{respondent_analysis['unique_respondents']}"
            )

            print(
                f"Rows per Respondent   : "
                f"{respondent_analysis['rows_per_respondent']}"
            )

        print(
            f"\nInvestment Type Found : "
            f"{unpivot_analysis['investment_type_found']}"
        )

        if unpivot_analysis[
            "investment_type_found"
        ]:

            print(
                "Investment Types     : "
                f"{', '.join(unpivot_analysis['investment_type_values'])}"
            )

        print("\nAudit files created:")

        print(
            f"  1. {column_audit_file}"
        )

        print(
            f"  2. {duplicate_file}"
        )

        print(
            f"  3. {summary_file}"
        )

        print("\n" + "=" * 70)

    except Exception as error:

        print("\n")
        print("=" * 70)
        print("DATA AUDIT FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        print(
            "\nCheck that your CSV exists inside:"
        )

        print(
            RAW_DATA_DIR
        )

        raise


# ============================================================
# 16. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()