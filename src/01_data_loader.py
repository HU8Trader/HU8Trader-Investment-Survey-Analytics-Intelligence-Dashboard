from pathlib import Path
from typing import Optional

import pandas as pd


# ============================================================
# 2. PROJECT PATH CONFIGURATION
# ============================================================

# This file is located inside:
#
# investment-survey-python/ 
# └── src/
#     └── 01_data_loader.py
#
# Therefore:
#   .parent       -> src/
#   .parent.parent -> project root/

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

DATA_FILE = RAW_DATA_DIR / "investment.csv"


# ============================================================
# 3. EXPECTED SOURCE SCHEMA
# ============================================================

# These are the ORIGINAL column names from the raw CSV.
#
# Do NOT rename them here.
# Column standardization will happen later in:
#
#     03_data_cleaning.py

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
    "Source",
]


# ============================================================
# 4. FILE VALIDATION
# ============================================================

def validate_file_exists(file_path: Path) -> None:
    """
    Validate that the requested CSV file exists.

    Parameters
    ----------
    file_path : Path
        Path to the raw CSV file.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            "\n"
            "Raw dataset was not found.\n"
            f"Expected location:\n{file_path}\n\n"
            "Please make sure that investment.csv is stored inside:\n"
            "data/raw/\n"
        )

    if not file_path.is_file():
        raise FileNotFoundError(
            "\n"
            f"The path exists but is not a file:\n{file_path}\n"
        )


# ============================================================
# 5. SCHEMA VALIDATION
# ============================================================

def validate_schema(
    dataframe: pd.DataFrame,
    expected_columns: Optional[list[str]] = None
) -> None:
    """
    Validate the raw CSV schema.

    This function checks whether the expected source columns
    exist in the loaded DataFrame.

    It does NOT:
        - rename columns
        - remove columns
        - modify values

    Parameters
    ----------
    dataframe : pd.DataFrame
        Loaded raw DataFrame.

    expected_columns : list[str], optional
        Expected source column names.

    Raises
    ------
    ValueError
        If expected columns are missing.
    """

    if expected_columns is None:
        expected_columns = EXPECTED_COLUMNS

    actual_columns = list(dataframe.columns)

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
    ]

    if missing_columns:
        raise ValueError(
            "\n"
            "Dataset schema validation failed.\n\n"
            "Missing expected columns:\n"
            + "\n".join(f"  - {column}" for column in missing_columns)
            + "\n"
        )

    if unexpected_columns:
        print(
            "\nWARNING: Additional columns were detected in the dataset:"
        )

        for column in unexpected_columns:
            print(f"  - {column}")

        print(
            "\nThe additional columns will NOT be removed.\n"
            "The raw dataset will remain unchanged.\n"
        )


# ============================================================
# 6. LOAD RAW DATASET
# ============================================================

def load_raw_data(
    file_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load the raw Investment Survey CSV dataset.

    Parameters
    ----------
    file_path : Path, optional
        Custom path to the CSV file.
        If omitted, the default project path is used.

    Returns
    -------
    pd.DataFrame
        Raw Investment Survey dataset.

    Notes
    -----
    The returned DataFrame is intentionally kept unchanged.
    No cleaning or transformation is performed here.
    """

    if file_path is None:
        file_path = DATA_FILE

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    validate_file_exists(file_path)

    # --------------------------------------------------------
    # Load CSV
    # --------------------------------------------------------

    try:
        dataframe = pd.read_csv(file_path)

    except UnicodeDecodeError:
        # Fallback for files that are not UTF-8 encoded.
        dataframe = pd.read_csv(
            file_path,
            encoding="latin1"
        )

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            f"The CSV file is empty:\n{file_path}"
        ) from error

    except pd.errors.ParserError as error:
        raise ValueError(
            "Pandas could not parse the CSV file.\n"
            f"File: {file_path}\n"
            "Please check the CSV structure."
        ) from error

    # --------------------------------------------------------
    # Validate schema
    # --------------------------------------------------------

    validate_schema(dataframe)

    # --------------------------------------------------------
    # Loading summary
    # --------------------------------------------------------

    print("=" * 70)
    print("INVESTMENT SURVEY — RAW DATA LOADER")
    print("=" * 70)

    print(f"\nDataset path:")
    print(f"  {file_path}")

    print(f"\nDataset successfully loaded.")

    print(f"\nRows    : {dataframe.shape[0]}")
    print(f"Columns : {dataframe.shape[1]}")

    print("\nSchema validation:")
    print("  ✓ Expected source columns detected")

    print("\nData integrity principle:")
    print("  ✓ Raw dataset has NOT been modified")

    print("\n" + "=" * 70)

    return dataframe


# ============================================================
# 7. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    # Load the raw dataset
    df = load_raw_data()

    # --------------------------------------------------------
    # Display basic information
    # --------------------------------------------------------

    print("\nFIRST 5 ROWS")
    print("-" * 70)

    print(df.head().to_string(index=False))

    print("\nCOLUMN LIST")
    print("-" * 70)

    for number, column in enumerate(df.columns, start=1):
        print(f"{number:02d}. {column}")

    print("\nDATA TYPES")
    print("-" * 70)

    print(df.dtypes.to_string())

    print("\nRAW DATA LOADING COMPLETED SUCCESSFULLY.")