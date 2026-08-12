"""
================================================================================
INVESTMENT SURVEY — FINAL PROCESSED DATA EXPORT
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
08_validation.py
        ↓
09_export_processed_data.py

Purpose
-------
Create the final BI-ready delivery layer.

Final delivery includes:

1. Clean respondent-level data
2. Clean investment-level data
3. Business metrics
4. Investment preference analysis
5. Gender analysis
6. Age analysis
7. Objective analysis
8. Purpose analysis
9. Decision-factor analysis
10. Duration analysis
11. Expected-return analysis
12. Savings-objective analysis
13. Information-source analysis
14. Monitoring-frequency analysis
15. Gender preference gap
16. Executive insights
17. Analytical recommendations
18. Validation report
19. Export grain validation
20. Final export manifest
21. Final export summary

IMPORTANT DATA-GRAIN RULE
-------------------------

RESPONDENT TABLE
----------------
One row = one respondent.

INVESTMENT TABLE
----------------
One row = one respondent × investment type.

Therefore:

    COUNTROWS(investment_df)

must NOT be interpreted as respondent count.

For respondent counts use:

    investment_df["Respondent_ID"].nunique()

BUSINESS RULES
--------------

1. Do not modify validated analytical results.

2. Preserve business-grain definitions.

3. Preserve categorical expected-return ranges.

4. Do not create artificial average expected returns.

5. Preserve Preference Rank logic:

       1 = Highest Preference
       7 = Lowest Preference

6. Lower Average Preference Rank means stronger preference.

7. Export CSV files using UTF-8 with BOM.

8. Create an export manifest.

9. Create an export summary.

10. Fail loudly when critical datasets are missing.

11. Business metrics are expected from 06_business_metrics.py.
    If the file is missing, the exporter will NOT invent analytical
    metrics. It will export an empty business_metrics.csv and clearly
    mark the issue in the export summary.

================================================================================
"""


# ==============================================================================
# 1. IMPORTS
# ==============================================================================

from pathlib import Path
from datetime import datetime
import hashlib

import pandas as pd


# ==============================================================================
# 2. PROJECT PATHS
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

FEATURES_DIR = DATA_DIR / "features"
METRICS_DIR = DATA_DIR / "metrics"
ANALYSIS_DIR = DATA_DIR / "analysis"
VALIDATION_DIR = DATA_DIR / "validation"

PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = PROCESSED_DIR / "final"

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================================================================
# 3. INPUT FILE DEFINITIONS
# ==============================================================================

INPUT_FILES = {

    # --------------------------------------------------------------------------
    # Feature Layer
    # --------------------------------------------------------------------------

    "respondent_features":
        FEATURES_DIR / "respondent_features.csv",

    "investment_features":
        FEATURES_DIR / "investment_features.csv",

    # --------------------------------------------------------------------------
    # Metrics Layer
    # --------------------------------------------------------------------------

    "business_metrics":
        METRICS_DIR / "business_metrics.csv",

    # --------------------------------------------------------------------------
    # Analysis Layer
    # --------------------------------------------------------------------------

    "investment_analysis":
        ANALYSIS_DIR / "investment_preference_analysis.csv",

    "gender_analysis":
        ANALYSIS_DIR / "gender_investment_analysis.csv",

    "age_analysis":
        ANALYSIS_DIR / "age_investment_analysis.csv",

    "objective_analysis":
        ANALYSIS_DIR / "objective_investment_analysis.csv",

    "female_analysis":
        ANALYSIS_DIR / "female_investment_preference.csv",

    "young_analysis":
        ANALYSIS_DIR / "young_investor_preference.csv",

    "bond_analysis":
        ANALYSIS_DIR / "bond_preference_analysis.csv",

    "gender_preference_summary":
        ANALYSIS_DIR / "gender_preference_summary.csv",

    "age_preference_summary":
        ANALYSIS_DIR / "age_preference_summary.csv",

    "objective_preference_summary":
        ANALYSIS_DIR / "objective_preference_summary.csv",

    "purpose_analysis":
        ANALYSIS_DIR / "purpose_investment_analysis.csv",

    "factor_analysis":
        ANALYSIS_DIR / "factor_investment_analysis.csv",

    "duration_analysis":
        ANALYSIS_DIR / "duration_investment_analysis.csv",

    "expected_return_analysis":
        ANALYSIS_DIR / "expected_return_analysis.csv",

    "savings_analysis":
        ANALYSIS_DIR / "savings_investment_analysis.csv",

    "source_analysis":
        ANALYSIS_DIR / "source_investment_analysis.csv",

    "monitoring_analysis":
        ANALYSIS_DIR / "monitoring_investment_analysis.csv",

    "gender_gap":
        ANALYSIS_DIR / "gender_preference_gap.csv",

    "executive_insights":
        ANALYSIS_DIR / "executive_analytical_insights.csv",

    "recommendations":
        ANALYSIS_DIR / "analytical_recommendations.csv",

    "analysis_summary":
        ANALYSIS_DIR / "analysis_summary.csv",

    # --------------------------------------------------------------------------
    # Validation Layer
    # --------------------------------------------------------------------------

    "validation_report":
        VALIDATION_DIR / "validation_report.csv",
}


# ==============================================================================
# 4. OUTPUT FILE DEFINITIONS
# ==============================================================================

OUTPUT_FILES = {

    "respondent":
        EXPORT_DIR / "dim_respondent.csv",

    "investment":
        EXPORT_DIR / "fact_investment_preference.csv",

    "business_metrics":
        EXPORT_DIR / "business_metrics.csv",

    "investment_analysis":
        EXPORT_DIR / "investment_preference_analysis.csv",

    "gender_analysis":
        EXPORT_DIR / "gender_investment_analysis.csv",

    "age_analysis":
        EXPORT_DIR / "age_investment_analysis.csv",

    "objective_analysis":
        EXPORT_DIR / "objective_investment_analysis.csv",

    "female_analysis":
        EXPORT_DIR / "female_investment_preference.csv",

    "young_analysis":
        EXPORT_DIR / "young_investor_preference.csv",

    "bond_analysis":
        EXPORT_DIR / "bond_preference_analysis.csv",

    "gender_preference_summary":
        EXPORT_DIR / "gender_preference_summary.csv",

    "age_preference_summary":
        EXPORT_DIR / "age_preference_summary.csv",

    "objective_preference_summary":
        EXPORT_DIR / "objective_preference_summary.csv",

    "purpose_analysis":
        EXPORT_DIR / "purpose_investment_analysis.csv",

    "factor_analysis":
        EXPORT_DIR / "factor_investment_analysis.csv",

    "duration_analysis":
        EXPORT_DIR / "duration_investment_analysis.csv",

    "expected_return_analysis":
        EXPORT_DIR / "expected_return_analysis.csv",

    "savings_analysis":
        EXPORT_DIR / "savings_investment_analysis.csv",

    "source_analysis":
        EXPORT_DIR / "source_investment_analysis.csv",

    "monitoring_analysis":
        EXPORT_DIR / "monitoring_investment_analysis.csv",

    "gender_gap":
        EXPORT_DIR / "gender_preference_gap.csv",

    "executive_insights":
        EXPORT_DIR / "executive_analytical_insights.csv",

    "recommendations":
        EXPORT_DIR / "analytical_recommendations.csv",

    "analysis_summary":
        EXPORT_DIR / "analysis_summary.csv",

    "validation_report":
        EXPORT_DIR / "validation_report.csv",

    "export_grain_validation":
        EXPORT_DIR / "export_grain_validation.csv",

    "export_manifest":
        EXPORT_DIR / "export_manifest.csv",

    "export_summary":
        EXPORT_DIR / "export_summary.csv",
}


# ==============================================================================
# 5. CONFIGURATION
# ==============================================================================

EXPORT_ENCODING = "utf-8-sig"

# These datasets are absolutely required for the final BI layer.
CRITICAL_INPUTS = [
    "respondent_features",
    "investment_features",
    "validation_report",
]

# These analytical files are optional.
OPTIONAL_INPUTS = [
    "business_metrics",

    "investment_analysis",
    "gender_analysis",
    "age_analysis",
    "objective_analysis",

    "female_analysis",
    "young_analysis",
    "bond_analysis",

    "gender_preference_summary",
    "age_preference_summary",
    "objective_preference_summary",

    "purpose_analysis",
    "factor_analysis",
    "duration_analysis",

    "expected_return_analysis",

    "savings_analysis",
    "source_analysis",
    "monitoring_analysis",

    "gender_gap",

    "executive_insights",
    "recommendations",

    "analysis_summary",
]


# ==============================================================================
# 6. CONSOLE UTILITIES
# ==============================================================================

def print_section(title):
    """Print a formatted console section."""

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_warning(message):
    """Print a formatted warning."""

    print(f"  ! WARNING: {message}")


def print_success(message):
    """Print a formatted success message."""

    print(f"  ✓ {message}")


# ==============================================================================
# 7. CSV LOADING
# ==============================================================================

def load_csv(path):
    """
    Load a CSV file.

    Raises:
        FileNotFoundError:
            When the file does not exist.

        RuntimeError:
            When pandas cannot read the file.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"\nMissing critical input file:\n{path}"
        )

    try:

        dataframe = pd.read_csv(
            path
        )

    except Exception as error:

        raise RuntimeError(
            f"\nUnable to read CSV:\n"
            f"{path}\n\n"
            f"Error: {error}"
        ) from error

    return dataframe


def safe_load_csv(path):
    """
    Load a CSV if available.

    Missing or unreadable optional files return an empty DataFrame.
    """

    if not path.exists():

        print_warning(
            f"Optional input file not found: {path}"
        )

        return pd.DataFrame()

    try:

        dataframe = pd.read_csv(
            path
        )

        return dataframe

    except Exception as error:

        print_warning(
            f"Could not read {path.name}: {error}"
        )

        return pd.DataFrame()


# ==============================================================================
# 8. BUSINESS METRICS SEARCH
# ==============================================================================

def locate_business_metrics():
    """
    Search for business_metrics.csv in several likely locations.

    This solves the common pipeline problem where 06_business_metrics.py
    creates the file in a slightly different folder or filename.

    Returns:
        Path or None
    """

    candidates = [

        # Expected location
        METRICS_DIR / "business_metrics.csv",

        # Common alternate locations
        ANALYSIS_DIR / "business_metrics.csv",

        FEATURES_DIR / "business_metrics.csv",

        DATA_DIR / "business_metrics.csv",

        PROCESSED_DIR / "business_metrics.csv",

        # Possible naming variants
        METRICS_DIR / "business_metric.csv",

        METRICS_DIR / "business_metrics_summary.csv",

        METRICS_DIR / "business_kpis.csv",

        ANALYSIS_DIR / "business_metrics_summary.csv",
    ]

    # Remove duplicates while preserving order.
    unique_candidates = []

    for path in candidates:

        if path not in unique_candidates:

            unique_candidates.append(path)

    for path in unique_candidates:

        if path.exists():

            print_success(
                f"Business metrics found: {path}"
            )

            return path

    return None


# ==============================================================================
# 9. COLUMN NORMALIZATION
# ==============================================================================

def normalize_column_names(dataframe):
    """
    Standardize column names.

    Meaning and values are preserved.
    """

    if dataframe.empty:

        return dataframe.copy()

    result = dataframe.copy()

    result.columns = [

        str(column)
        .strip()
        .replace(" ", "_")
        .replace("-", "_")

        for column in result.columns
    ]

    return result


# ==============================================================================
# 10. LOAD CRITICAL DATA
# ==============================================================================

def load_critical_data():
    """
    Load datasets that are required for the final delivery layer.
    """

    print_section(
        "LOADING CRITICAL DATA"
    )

    data = {}

    for key in CRITICAL_INPUTS:

        path = INPUT_FILES[key]

        print(
            f"Loading {key:<30} ..."
        )

        data[key] = load_csv(
            path
        )

        print_success(
            f"{len(data[key]):,} rows"
        )

    return data


# ==============================================================================
# 11. LOAD OPTIONAL DATA
# ==============================================================================

def load_optional_data():
    """
    Load optional metrics and analytical datasets.
    """

    print_section(
        "LOADING OPTIONAL ANALYTICAL DATA"
    )

    data = {}

    for key in OPTIONAL_INPUTS:

        # Business metrics has special path resolution.
        if key == "business_metrics":

            business_metrics_path = (
                locate_business_metrics()
            )

            if business_metrics_path is None:

                print_warning(
                    "business_metrics.csv was not found."
                )

                print_warning(
                    "The exporter will NOT create artificial "
                    "business metrics."
                )

                print_warning(
                    "Run 06_business_metrics.py and verify its output."
                )

                data[key] = pd.DataFrame()

            else:

                data[key] = safe_load_csv(
                    business_metrics_path
                )

        else:

            path = INPUT_FILES[key]

            data[key] = safe_load_csv(
                path
            )

        print(
            f"  {key:<32} "
            f"{len(data[key]):>8,} rows"
        )

    return data


# ==============================================================================
# 12. PREPARE RESPONDENT DATASET
# ==============================================================================

def prepare_respondent_export(dataframe):
    """
    Prepare final respondent-level dimension.

    Grain:
        One row = one respondent.
    """

    if dataframe.empty:

        return pd.DataFrame()

    result = normalize_column_names(
        dataframe
    )

    # Remove exact duplicates.
    result = result.drop_duplicates()

    # --------------------------------------------------------------------------
    # Detect respondent ID.
    # --------------------------------------------------------------------------

    id_candidates = [

        "Respondent_ID",
        "respondent_id",
        "Response_ID",
        "response_id",
    ]

    id_column = next(
        (
            column
            for column in id_candidates
            if column in result.columns
        ),
        None
    )

    # --------------------------------------------------------------------------
    # Enforce one row per respondent.
    # --------------------------------------------------------------------------

    if id_column is not None:

        result = result.drop_duplicates(
            subset=[id_column],
            keep="first"
        )

        # Rename to enterprise-standard naming.
        if id_column != "Respondent_ID":

            result = result.rename(
                columns={
                    id_column: "Respondent_ID"
                }
            )

    return result.reset_index(
        drop=True
    )


# ==============================================================================
# 13. PREPARE INVESTMENT FACT DATASET
# ==============================================================================

def prepare_investment_export(dataframe):
    """
    Prepare final investment-level fact table.

    Grain:
        One row = one respondent × investment type.

    Preference Rank:
        1 = Highest Preference
        7 = Lowest Preference.
    """

    if dataframe.empty:

        return pd.DataFrame()

    result = normalize_column_names(
        dataframe
    )

    # Remove exact duplicates only.
    result = result.drop_duplicates()

    # --------------------------------------------------------------------------
    # Standardize respondent ID.
    # --------------------------------------------------------------------------

    id_candidates = [
        "Respondent_ID",
        "respondent_id",
        "Response_ID",
        "response_id",
    ]

    id_column = next(
        (
            column
            for column in id_candidates
            if column in result.columns
        ),
        None
    )

    if id_column is not None and id_column != "Respondent_ID":

        result = result.rename(
            columns={
                id_column: "Respondent_ID"
            }
        )

    # --------------------------------------------------------------------------
    # Standardize investment type column if necessary.
    # --------------------------------------------------------------------------

    investment_candidates = [
        "Investment_Type",
        "investment_type",
        "Investment",
        "investment",
    ]

    investment_column = next(
        (
            column
            for column in investment_candidates
            if column in result.columns
        ),
        None
    )

    if (
        investment_column is not None
        and investment_column != "Investment_Type"
    ):

        result = result.rename(
            columns={
                investment_column: "Investment_Type"
            }
        )

    # --------------------------------------------------------------------------
    # Numeric preference fields.
    # --------------------------------------------------------------------------

    for column in [
        "Preference_Rank",
        "Preference_Score",
    ]:

        if column in result.columns:

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce"
            )

    # --------------------------------------------------------------------------
    # Preserve expected return as categorical.
    # --------------------------------------------------------------------------

    expected_return_columns = [

        "Expected_Return_Range",
        "Expected_Return",
        "expected_return",
    ]

    expected_column = next(
        (
            column
            for column in expected_return_columns
            if column in result.columns
        ),
        None
    )

    if expected_column is not None:

        result[expected_column] = (
            result[expected_column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------------------------
    # Sort by respondent and preference rank.
    # --------------------------------------------------------------------------

    sort_columns = []

    if "Respondent_ID" in result.columns:

        sort_columns.append(
            "Respondent_ID"
        )

    if "Preference_Rank" in result.columns:

        sort_columns.append(
            "Preference_Rank"
        )

    if sort_columns:

        result = result.sort_values(
            sort_columns,
            kind="stable"
        )

    return result.reset_index(
        drop=True
    )


# ==============================================================================
# 14. VALIDATE RESPONDENT GRAIN
# ==============================================================================

def validate_respondent_grain(respondent_df):
    """
    Validate:

        One row = one respondent.
    """

    if respondent_df.empty:

        return {
            "Check":
                "Respondent Grain",

            "Status":
                "FAIL",

            "Details":
                "Respondent dataset is empty.",
        }

    if "Respondent_ID" not in respondent_df.columns:

        return {
            "Check":
                "Respondent Grain",

            "Status":
                "FAIL",

            "Details":
                "Respondent_ID column not found.",
        }

    duplicate_count = (
        respondent_df["Respondent_ID"]
        .duplicated()
        .sum()
    )

    null_count = (
        respondent_df["Respondent_ID"]
        .isna()
        .sum()
    )

    if duplicate_count == 0 and null_count == 0:

        return {
            "Check":
                "Respondent Grain",

            "Status":
                "PASS",

            "Details":
                "One row per Respondent_ID.",
        }

    return {
        "Check":
            "Respondent Grain",

        "Status":
            "FAIL",

        "Details":
            (
                f"Duplicate IDs: {duplicate_count:,}; "
                f"Null IDs: {null_count:,}."
            ),
    }


# ==============================================================================
# 15. VALIDATE INVESTMENT GRAIN
# ==============================================================================

def validate_investment_grain(investment_df):
    """
    Validate:

        One row = one respondent × investment type.
    """

    if investment_df.empty:

        return {
            "Check":
                "Investment Grain",

            "Status":
                "FAIL",

            "Details":
                "Investment dataset is empty.",
        }

    required_columns = [
        "Respondent_ID",
        "Investment_Type",
    ]

    missing_columns = [

        column
        for column in required_columns
        if column not in investment_df.columns
    ]

    if missing_columns:

        return {
            "Check":
                "Investment Grain",

            "Status":
                "FAIL",

            "Details":
                (
                    "Missing columns: "
                    + ", ".join(missing_columns)
                ),
        }

    duplicate_count = (
        investment_df
        .duplicated(
            subset=required_columns
        )
        .sum()
    )

    null_respondent = (
        investment_df["Respondent_ID"]
        .isna()
        .sum()
    )

    null_investment = (
        investment_df["Investment_Type"]
        .isna()
        .sum()
    )

    if (
        duplicate_count == 0
        and null_respondent == 0
        and null_investment == 0
    ):

        return {
            "Check":
                "Investment Grain",

            "Status":
                "PASS",

            "Details":
                (
                    "One row per Respondent_ID × Investment_Type."
                ),
        }

    return {
        "Check":
            "Investment Grain",

        "Status":
            "FAIL",

        "Details":
            (
                f"Duplicate pairs: {duplicate_count:,}; "
                f"Null respondent IDs: {null_respondent:,}; "
                f"Null investment types: {null_investment:,}."
            ),
    }


# ==============================================================================
# 16. VALIDATE PREFERENCE RANK
# ==============================================================================

def validate_preference_rank(investment_df):
    """
    Validate Preference Rank business rule.

    1 = Highest Preference
    7 = Lowest Preference
    """

    if investment_df.empty:

        return {
            "Check":
                "Preference Rank Logic",

            "Status":
                "FAIL",

            "Details":
                "Investment dataset is empty.",
        }

    if "Preference_Rank" not in investment_df.columns:

        return {
            "Check":
                "Preference Rank Logic",

            "Status":
                "WARNING",

            "Details":
                "Preference_Rank column not found.",
        }

    rank_series = investment_df[
        "Preference_Rank"
    ].dropna()

    if rank_series.empty:

        return {
            "Check":
                "Preference Rank Logic",

            "Status":
                "WARNING",

            "Details":
                "No Preference_Rank values available.",
        }

    invalid_values = rank_series[
        ~rank_series.isin(
            range(1, 8)
        )
    ]

    if invalid_values.empty:

        return {
            "Check":
                "Preference Rank Logic",

            "Status":
                "PASS",

            "Details":
                (
                    "Preference Rank follows "
                    "1 = Highest and 7 = Lowest."
                ),
        }

    return {
        "Check":
            "Preference Rank Logic",

        "Status":
            "FAIL",

        "Details":
            (
                f"Invalid rank values detected: "
                f"{invalid_values.unique().tolist()}"
            ),
    }


# ==============================================================================
# 17. VALIDATE EXPECTED RETURN
# ==============================================================================

def validate_expected_return(investment_df):
    """
    Ensure expected return remains categorical.

    No artificial average is created.
    """

    if investment_df.empty:

        return {
            "Check":
                "Expected Return Representation",

            "Status":
                "FAIL",

            "Details":
                "Investment dataset is empty.",
        }

    candidates = [
        "Expected_Return_Range",
        "Expected_Return",
        "expected_return",
    ]

    column = next(
        (
            item
            for item in candidates
            if item in investment_df.columns
        ),
        None
    )

    if column is None:

        return {
            "Check":
                "Expected Return Representation",

            "Status":
                "WARNING",

            "Details":
                "Expected return column not found.",
        }

    dtype = str(
        investment_df[column].dtype
    )

    return {
        "Check":
            "Expected Return Representation",

        "Status":
            "PASS",

        "Details":
            (
                f"{column} preserved as categorical/text data. "
                f"No artificial average calculated. "
                f"Detected dtype: {dtype}."
            ),
    }


# ==============================================================================
# 18. VALIDATE EXPORT DATA
# ==============================================================================

def validate_export_data(
    respondent_df,
    investment_df
):
    """
    Run all final export-level validations.
    """

    print_section(
        "VALIDATING FINAL EXPORT DATA"
    )

    checks = [

        validate_respondent_grain(
            respondent_df
        ),

        validate_investment_grain(
            investment_df
        ),

        validate_preference_rank(
            investment_df
        ),

        validate_expected_return(
            investment_df
        ),
    ]

    validation_df = pd.DataFrame(
        checks
    )

    print(
        validation_df.to_string(
            index=False
        )
    )

    return validation_df


# ==============================================================================
# 19. EXPORT DATASET
# ==============================================================================

def export_dataset(
    dataframe,
    key
):
    """
    Export DataFrame as UTF-8 BOM CSV.
    """

    if key not in OUTPUT_FILES:

        raise KeyError(
            f"Unknown output key: {key}"
        )

    path = OUTPUT_FILES[key]

    if dataframe is None:

        dataframe = pd.DataFrame()

    dataframe.to_csv(
        path,
        index=False,
        encoding=EXPORT_ENCODING
    )

    print(
        f"  ✓ {path.name:<45}"
        f"{len(dataframe):>8,} rows"
    )

    return path


# ==============================================================================
# 20. SHA-256 FILE HASH
# ==============================================================================

def calculate_file_hash(path):
    """
    Calculate SHA-256 hash.
    """

    sha256 = hashlib.sha256()

    with open(
        path,
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b""
        ):

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ==============================================================================
# 21. BUILD EXPORT MANIFEST
# ==============================================================================

def build_export_manifest(
    exported_files
):
    """
    Build a metadata manifest for every exported dataset.
    """

    records = []

    export_timestamp = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    for key, path in exported_files.items():

        if path is None:
            continue

        if not path.exists():
            continue

        try:

            dataframe = pd.read_csv(
                path
            )

            rows = len(dataframe)

            columns = len(
                dataframe.columns
            )

        except Exception:

            rows = 0
            columns = 0

        records.append({

            "Dataset_Key":
                key,

            "File_Name":
                path.name,

            "File_Path":
                str(path),

            "Rows":
                rows,

            "Columns":
                columns,

            "File_Size_KB":
                round(
                    path.stat().st_size / 1024,
                    2
                ),

            "SHA256":
                calculate_file_hash(
                    path
                ),

            "Export_Timestamp":
                export_timestamp,

            "Encoding":
                EXPORT_ENCODING,
        })

    return pd.DataFrame(
        records
    )


# ==============================================================================
# 22. BUILD EXPORT SUMMARY
# ==============================================================================

def build_export_summary(
    respondent_df,
    investment_df,
    exported_files,
    business_metrics_df,
    validation_df
):
    """
    Create final export summary.
    """

    # --------------------------------------------------------------------------
    # Respondent count
    # --------------------------------------------------------------------------

    if "Respondent_ID" in respondent_df.columns:

        unique_respondents = (
            respondent_df[
                "Respondent_ID"
            ]
            .nunique()
        )

    else:

        unique_respondents = 0

    # --------------------------------------------------------------------------
    # Investment types
    # --------------------------------------------------------------------------

    if "Investment_Type" in investment_df.columns:

        investment_types = (
            investment_df[
                "Investment_Type"
            ]
            .nunique()
        )

    else:

        investment_types = 0

    # --------------------------------------------------------------------------
    # Validation status
    # --------------------------------------------------------------------------

    if validation_df.empty:

        validation_status = "UNKNOWN"

    elif (
        validation_df["Status"]
        .eq("FAIL")
        .any()
    ):

        validation_status = "FAIL"

    elif (
        validation_df["Status"]
        .eq("WARNING")
        .any()
    ):

        validation_status = "WARNING"

    else:

        validation_status = "PASS"

    # --------------------------------------------------------------------------
    # Business metrics status
    # --------------------------------------------------------------------------

    if business_metrics_df.empty:

        business_metrics_status = (
            "MISSING — RUN 06_business_metrics.py"
        )

    else:

        business_metrics_status = "AVAILABLE"

    # --------------------------------------------------------------------------
    # Final summary
    # --------------------------------------------------------------------------

    summary = {

        "Export_Timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Unique_Respondents":
            unique_respondents,

        "Respondent_Rows":
            len(respondent_df),

        "Investment_Rows":
            len(investment_df),

        "Investment_Types":
            investment_types,

        "Datasets_Exported":
            len(exported_files),

        "Business_Metrics_Status":
            business_metrics_status,

        "Validation_Status":
            validation_status,

        "Export_Directory":
            str(EXPORT_DIR),

        "Encoding":
            EXPORT_ENCODING,

        "Preference_Rule":
            (
                "1 = Highest Preference; "
                "7 = Lowest Preference; "
                "Lower Average Preference Rank = "
                "Stronger Preference"
            ),

        "Expected_Return_Rule":
            (
                "Expected return ranges preserved "
                "as categorical values; "
                "no artificial average calculated."
            ),
    }

    return pd.DataFrame(
        [summary]
    )


# ==============================================================================
# 23. MAIN PIPELINE
# ==============================================================================

def main():

    print("=" * 80)

    print(
        "INVESTMENT SURVEY — FINAL PROCESSED DATA EXPORT"
    )

    print("=" * 80)

    print(
        "\nProject root:"
    )

    print(
        PROJECT_ROOT
    )

    print(
        "\nExport directory:"
    )

    print(
        EXPORT_DIR
    )

    # ==========================================================================
    # STEP 1 — LOAD CRITICAL DATA
    # ==========================================================================

    required_data = (
        load_critical_data()
    )

    # ==========================================================================
    # STEP 2 — LOAD OPTIONAL DATA
    # ==========================================================================

    optional_data = (
        load_optional_data()
    )

    # ==========================================================================
    # STEP 3 — PREPARE RESPONDENT DATA
    # ==========================================================================

    print_section(
        "PREPARING RESPONDENT DATA"
    )

    respondent_export = (
        prepare_respondent_export(
            required_data[
                "respondent_features"
            ]
        )
    )

    print(
        f"  Respondent rows : "
        f"{len(respondent_export):,}"
    )

    # ==========================================================================
    # STEP 4 — PREPARE INVESTMENT DATA
    # ==========================================================================

    print_section(
        "PREPARING INVESTMENT DATA"
    )

    investment_export = (
        prepare_investment_export(
            required_data[
                "investment_features"
            ]
        )
    )

    print(
        f"  Investment rows : "
        f"{len(investment_export):,}"
    )

    # ==========================================================================
    # STEP 5 — VALIDATE FINAL DATA
    # ==========================================================================

    validation_df = (
        validate_export_data(
            respondent_export,
            investment_export
        )
    )

    # ==========================================================================
    # STEP 6 — EXPORT CORE BI TABLES
    # ==========================================================================

    print_section(
        "EXPORTING CORE BI DATASETS"
    )

    exported_files = {}

    exported_files["respondent"] = (
        export_dataset(
            respondent_export,
            "respondent"
        )
    )

    exported_files["investment"] = (
        export_dataset(
            investment_export,
            "investment"
        )
    )

    # ==========================================================================
    # STEP 7 — EXPORT BUSINESS METRICS
    # ==========================================================================

    print_section(
        "EXPORTING BUSINESS METRICS"
    )

    exported_files["business_metrics"] = (
        export_dataset(
            optional_data[
                "business_metrics"
            ],
            "business_metrics"
        )
    )

    # ==========================================================================
    # STEP 8 — EXPORT ANALYTICAL DATASETS
    # ==========================================================================

    print_section(
        "EXPORTING ANALYTICAL DATASETS"
    )

    analysis_keys = [

        "investment_analysis",

        "gender_analysis",

        "age_analysis",

        "objective_analysis",

        "female_analysis",

        "young_analysis",

        "bond_analysis",

        "gender_preference_summary",

        "age_preference_summary",

        "objective_preference_summary",

        "purpose_analysis",

        "factor_analysis",

        "duration_analysis",

        "expected_return_analysis",

        "savings_analysis",

        "source_analysis",

        "monitoring_analysis",

        "gender_gap",

        "executive_insights",

        "recommendations",

        "analysis_summary",
    ]

    for key in analysis_keys:

        exported_files[key] = (
            export_dataset(
                optional_data[key],
                key
            )
        )

    # ==========================================================================
    # STEP 9 — EXPORT ORIGINAL VALIDATION REPORT
    # ==========================================================================

    print_section(
        "EXPORTING VALIDATION REPORT"
    )

    exported_files["validation_report"] = (
        export_dataset(
            required_data[
                "validation_report"
            ],
            "validation_report"
        )
    )

    # ==========================================================================
    # STEP 10 — EXPORT FINAL GRAIN VALIDATION
    # ==========================================================================

    print_section(
        "EXPORTING EXPORT GRAIN VALIDATION"
    )

    grain_validation_path = (
        OUTPUT_FILES[
            "export_grain_validation"
        ]
    )

    validation_df.to_csv(
        grain_validation_path,
        index=False,
        encoding=EXPORT_ENCODING
    )

    exported_files[
        "export_grain_validation"
    ] = grain_validation_path

    print_success(
        grain_validation_path.name
    )

    # ==========================================================================
    # STEP 11 — BUILD EXPORT MANIFEST
    # ==========================================================================

    print_section(
        "BUILDING EXPORT MANIFEST"
    )

    manifest = (
        build_export_manifest(
            exported_files
        )
    )

    manifest_path = (
        OUTPUT_FILES[
            "export_manifest"
        ]
    )

    manifest.to_csv(
        manifest_path,
        index=False,
        encoding=EXPORT_ENCODING
    )

    print_success(
        manifest_path.name
    )

    # ==========================================================================
    # STEP 12 — BUILD EXPORT SUMMARY
    # ==========================================================================

    print_section(
        "BUILDING EXPORT SUMMARY"
    )

    summary = (
        build_export_summary(
            respondent_export,
            investment_export,
            exported_files,
            optional_data[
                "business_metrics"
            ],
            validation_df
        )
    )

    summary_path = (
        OUTPUT_FILES[
            "export_summary"
        ]
    )

    summary.to_csv(
        summary_path,
        index=False,
        encoding=EXPORT_ENCODING
    )

    print_success(
        summary_path.name
    )

    # ==========================================================================
    # STEP 13 — FINAL REPORT
    # ==========================================================================

    print_section(
        "FINAL EXPORT REPORT"
    )

    if "Respondent_ID" in respondent_export.columns:

        unique_respondents = (
            respondent_export[
                "Respondent_ID"
            ]
            .nunique()
        )

    else:

        unique_respondents = 0

    if "Investment_Type" in investment_export.columns:

        investment_types = (
            investment_export[
                "Investment_Type"
            ]
            .nunique()
        )

    else:

        investment_types = 0

    print(
        f"\nUnique Respondents      : "
        f"{unique_respondents:,}"
    )

    print(
        f"Respondent Rows        : "
        f"{len(respondent_export):,}"
    )

    print(
        f"Investment Rows        : "
        f"{len(investment_export):,}"
    )

    print(
        f"Investment Types       : "
        f"{investment_types:,}"
    )

    print(
        f"Datasets Exported      : "
        f"{len(exported_files):,}"
    )

    # --------------------------------------------------------------------------
    # Business metrics status
    # --------------------------------------------------------------------------

    if optional_data[
        "business_metrics"
    ].empty:

        print(
            "\nBusiness Metrics       : "
            "NOT FOUND"
        )

        print(
            "  → Run 06_business_metrics.py "
            "to generate the analytical metrics."
        )

    else:

        print(
            "\nBusiness Metrics       : "
            "AVAILABLE"
        )

    # --------------------------------------------------------------------------
    # Validation status
    # --------------------------------------------------------------------------

    if (
        validation_df["Status"]
        .eq("FAIL")
        .any()
    ):

        print(
            "\nFinal Validation       : FAIL"
        )

        print_warning(
            "One or more final export validation "
            "checks failed."
        )

    elif (
        validation_df["Status"]
        .eq("WARNING")
        .any()
    ):

        print(
            "\nFinal Validation       : WARNING"
        )

    else:

        print(
            "\nFinal Validation       : PASS"
        )

    # --------------------------------------------------------------------------
    # Business rules
    # --------------------------------------------------------------------------

    print(
        "\nPreference Rule:"
    )

    print(
        "  1 = Highest Preference"
    )

    print(
        "  7 = Lowest Preference"
    )

    print(
        "  Lower Average Preference Rank "
        "= Stronger Preference"
    )

    print(
        "\nExpected Return:"
    )

    print(
        "  Categorical ranges preserved."
    )

    print(
        "  No artificial average expected return created."
    )

    # --------------------------------------------------------------------------
    # Final location
    # --------------------------------------------------------------------------

    print(
        "\nFinal BI-ready Export Directory:"
    )

    print(
        EXPORT_DIR
    )

    # ==========================================================================
    # STEP 14 — COMPLETION
    # ==========================================================================

    print("\n")
    print("=" * 80)

    print(
        "09_export_processed_data.py "
        "COMPLETED"
    )

    print("=" * 80)

    # --------------------------------------------------------------------------
    # Important warning
    # --------------------------------------------------------------------------

    if optional_data[
        "business_metrics"
    ].empty:

        print(
            "\nIMPORTANT:"
        )

        print(
            "business_metrics.csv was not available."
        )

        print(
            "No artificial business metrics were created."
        )

        print(
            "Run 06_business_metrics.py and then "
            "run this exporter again."
        )

    print(
        "\nAll available BI-ready datasets are located at:"
    )

    print(
        EXPORT_DIR
    )


# ==============================================================================
# 24. ENTRY POINT
# ==============================================================================

if __name__ == "__main__":

    main()