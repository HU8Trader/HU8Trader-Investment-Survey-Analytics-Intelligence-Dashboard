"""
Investment Survey Dashboard
Page: Demographics

Purpose:
    Analyze investor demographics including:

    - Total respondents
    - Average age
    - Minimum / maximum age
    - Gender distribution
    - Age-group distribution
    - Age vs Gender
    - Gender-wise average age
    - Age distribution
    - Demographic summary

Expected structure:

Python Version Investement Survey/
│
├── dashboard/
│   ├── app.py
│   ├── layout.py
│   ├── components.py
│   ├── filters.py
│   │
│   └── pages/
│       ├── executive.py
│       └── demographics.py
│
└── data/
    ├── feature/
    │   └── respondents.csv
    │
    └── analysis/
        └── age_investment_analysis.csv
"""

from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PATH CONFIGURATION
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

DASHBOARD_DIR = CURRENT_FILE.parents[1]

PROJECT_ROOT = DASHBOARD_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"

FEATURE_DIR = DATA_DIR / "feature"

ANALYSIS_DIR = DATA_DIR / "analysis"


# ============================================================
# FILE LOADING
# ============================================================

def load_csv(
    directory: Path,
    filenames: list[str],
) -> pd.DataFrame:
    """
    Try multiple possible filenames and return
    the first successfully loaded CSV.
    """

    for filename in filenames:

        path = directory / filename

        if not path.exists():
            continue

        try:

            return pd.read_csv(path)

        except Exception as exc:

            st.error(
                f"Unable to load `{filename}`.\n\n"
                f"Error: {exc}"
            )

            return pd.DataFrame()

    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_respondents() -> pd.DataFrame:
    """
    Load respondent-level feature data.
    """

    return load_csv(
        FEATURE_DIR,
        [
            "respondents.csv",
            "respondent.csv",
            "respondent_data.csv",
            "feature_respondents.csv",
        ],
    )


@st.cache_data(show_spinner=False)
def load_age_analysis() -> pd.DataFrame:
    """
    Load age-level analytical output.
    """

    return load_csv(
        ANALYSIS_DIR,
        [
            "age_investment_analysis.csv",
        ],
    )


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """
    Find a column using exact case-insensitive matching.
    """

    if df.empty:
        return None

    columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = candidate.strip().lower()

        if key in columns:

            return columns[key]

    return None


def find_column_contains(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """
    Find a column using partial matching.
    """

    if df.empty:
        return None

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        candidate = candidate.lower()

        for column_name, original_name in normalized.items():

            if candidate in column_name:

                return original_name

    return None


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_respondent_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardize respondent demographic columns.
    """

    if df.empty:
        return pd.DataFrame()

    result = df.copy()

    age_column = find_column(
        result,
        [
            "age",
            "Age",
            "Investor_Age",
        ],
    )

    gender_column = find_column(
        result,
        [
            "Gender",
            "gender",
        ],
    )

    id_column = find_column(
        result,
        [
            "Respondent_ID",
            "respondent_id",
            "ID",
            "id",
        ],
    )

    rename_map = {}

    if age_column:
        rename_map[age_column] = "Age"

    if gender_column:
        rename_map[gender_column] = "Gender"

    if id_column:
        rename_map[id_column] = "Respondent_ID"

    result = result.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    if "Age" in result.columns:

        result["Age"] = pd.to_numeric(
            result["Age"],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Gender
    # --------------------------------------------------------

    if "Gender" in result.columns:

        result["Gender"] = (
            result["Gender"]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "nan": pd.NA,
                    "None": pd.NA,
                    "": pd.NA,
                }
            )
        )

    return result


# ============================================================
# AGE GROUP CREATION
# ============================================================

def create_age_group(
    age: float | int | None,
) -> str:

    if pd.isna(age):

        return "Unknown"

    age = float(age)

    if age < 18:

        return "Below 18"

    if age <= 25:

        return "18–25"

    if age <= 35:

        return "26–35"

    if age <= 45:

        return "36–45"

    if age <= 55:

        return "46–55"

    if age <= 65:

        return "56–65"

    return "66+"


def add_age_groups(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    if "Age" not in result.columns:

        return result

    result["Age_Group"] = (
        result["Age"]
        .apply(create_age_group)
    )

    return result


# ============================================================
# KPI CALCULATIONS
# ============================================================

def total_respondents(
    df: pd.DataFrame,
) -> int:

    if df.empty:
        return 0

    if "Respondent_ID" in df.columns:

        return int(
            df["Respondent_ID"]
            .dropna()
            .nunique()
        )

    return int(len(df))


def average_age(
    df: pd.DataFrame,
) -> float | None:

    if df.empty or "Age" not in df.columns:

        return None

    values = pd.to_numeric(
        df["Age"],
        errors="coerce",
    )

    if values.dropna().empty:

        return None

    return float(
        values.mean()
    )


def minimum_age(
    df: pd.DataFrame,
) -> float | None:

    if df.empty or "Age" not in df.columns:

        return None

    values = pd.to_numeric(
        df["Age"],
        errors="coerce",
    )

    if values.dropna().empty:

        return None

    return float(
        values.min()
    )


def maximum_age(
    df: pd.DataFrame,
) -> float | None:

    if df.empty or "Age" not in df.columns:

        return None

    values = pd.to_numeric(
        df["Age"],
        errors="coerce",
    )

    if values.dropna().empty:

        return None

    return float(
        values.max()
    )


def gender_count(
    df: pd.DataFrame,
    gender: str,
) -> int:

    if df.empty or "Gender" not in df.columns:

        return 0

    values = (
        df["Gender"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return int(
        (
            values
            == gender.lower()
        ).sum()
    )


# ============================================================
# GENDER DISTRIBUTION
# ============================================================

def gender_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty or "Gender" not in df.columns:

        return pd.DataFrame()

    result = (
        df["Gender"]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
        .rename_axis("Gender")
        .reset_index(
            name="Respondents"
        )
    )

    return result


# ============================================================
# AGE GROUP DISTRIBUTION
# ============================================================

def age_group_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty or "Age_Group" not in df.columns:

        return pd.DataFrame()

    order = [
        "Below 18",
        "18–25",
        "26–35",
        "36–45",
        "46–55",
        "56–65",
        "66+",
        "Unknown",
    ]

    result = (
        df["Age_Group"]
        .value_counts()
        .reindex(
            order,
            fill_value=0,
        )
        .rename_axis("Age_Group")
        .reset_index(
            name="Respondents"
        )
    )

    return result


# ============================================================
# AGE DISTRIBUTION
# ============================================================

def age_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty or "Age" not in df.columns:

        return pd.DataFrame()

    result = (
        df["Age"]
        .dropna()
        .value_counts()
        .sort_index()
        .rename_axis("Age")
        .reset_index(
            name="Respondents"
        )
    )

    return result


# ============================================================
# GENDER × AGE GROUP
# ============================================================

def gender_age_group(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:

        return pd.DataFrame()

    required = {
        "Gender",
        "Age_Group",
    }

    if not required.issubset(
        df.columns
    ):

        return pd.DataFrame()

    result = pd.crosstab(
        df["Age_Group"],
        df["Gender"],
    )

    order = [
        "Below 18",
        "18–25",
        "26–35",
        "36–45",
        "46–55",
        "56–65",
        "66+",
        "Unknown",
    ]

    result = result.reindex(
        order,
        fill_value=0,
    )

    return result


# ============================================================
# GENDER AGE SUMMARY
# ============================================================

def gender_age_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:

        return pd.DataFrame()

    if not {
        "Gender",
        "Age",
    }.issubset(df.columns):

        return pd.DataFrame()

    result = (
        df.groupby(
            "Gender",
            dropna=True,
        )
        .agg(
            Respondents=("Gender", "size"),
            Average_Age=("Age", "mean"),
            Minimum_Age=("Age", "min"),
            Maximum_Age=("Age", "max"),
        )
        .reset_index()
    )

    return result


# ============================================================
# PAGE HEADER
# ============================================================

def render_header() -> None:

    st.title(
        "Investor Demographics"
    )

    st.caption(
        "Demographic profile of investment survey respondents."
    )

    st.divider()


# ============================================================
# KPI CARDS
# ============================================================

def render_kpis(
    df: pd.DataFrame,
) -> None:

    total = total_respondents(df)

    avg_age = average_age(df)

    min_age = minimum_age(df)

    max_age = maximum_age(df)

    male = gender_count(
        df,
        "Male",
    )

    female = gender_count(
        df,
        "Female",
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Respondents",
            f"{total:,}",
        )

    with col2:

        st.metric(
            "Average Age",
            (
                f"{avg_age:.1f}"
                if avg_age is not None
                else "N/A"
            ),
        )

    with col3:

        st.metric(
            "Minimum Age",
            (
                f"{min_age:.0f}"
                if min_age is not None
                else "N/A"
            ),
        )

    with col4:

        st.metric(
            "Maximum Age",
            (
                f"{max_age:.0f}"
                if max_age is not None
                else "N/A"
            ),
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:

        st.metric(
            "Male Investors",
            f"{male:,}",
        )

    with col6:

        st.metric(
            "Female Investors",
            f"{female:,}",
        )

    with col7:

        if total > 0:

            female_percentage = (
                female / total
            ) * 100

            st.metric(
                "Female Share",
                f"{female_percentage:.1f}%",
            )

        else:

            st.metric(
                "Female Share",
                "N/A",
            )

    with col8:

        if total > 0:

            male_percentage = (
                male / total
            ) * 100

            st.metric(
                "Male Share",
                f"{male_percentage:.1f}%",
            )

        else:

            st.metric(
                "Male Share",
                "N/A",
            )


# ============================================================
# GENDER SECTION
# ============================================================

def render_gender_section(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Gender Distribution"
    )

    data = gender_distribution(df)

    if data.empty:

        st.info(
            "Gender data is not available."
        )

        return

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.dataframe(
            data,
            width="stretch",
            hide_index=True,
        )

    with col2:

        chart = data.set_index(
            "Gender"
        )

        st.bar_chart(
            chart,
            width="stretch",
        )


# ============================================================
# AGE GROUP SECTION
# ============================================================

def render_age_group_section(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Investor Age Groups"
    )

    data = age_group_distribution(
        df
    )

    if data.empty:

        st.info(
            "Age-group data is not available."
        )

        return

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.dataframe(
            data,
            width="stretch",
            hide_index=True,
        )

    with col2:

        chart = data.set_index(
            "Age_Group"
        )

        st.bar_chart(
            chart,
            width="stretch",
        )


# ============================================================
# AGE DISTRIBUTION
# ============================================================

def render_age_distribution(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Age Distribution"
    )

    data = age_distribution(df)

    if data.empty:

        st.info(
            "Age distribution is not available."
        )

        return

    chart = data.set_index(
        "Age"
    )

    st.bar_chart(
        chart,
        width="stretch",
    )


# ============================================================
# AGE × GENDER
# ============================================================

def render_age_gender_section(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Age Group × Gender"
    )

    data = gender_age_group(
        df
    )

    if data.empty:

        st.info(
            "Age × Gender analysis is not available."
        )

        return

    st.dataframe(
        data,
        width="stretch",
    )

    st.bar_chart(
        data,
        width="stretch",
    )


# ============================================================
# GENDER AGE SUMMARY
# ============================================================

def render_gender_age_summary(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Gender-wise Age Summary"
    )

    data = gender_age_summary(
        df
    )

    if data.empty:

        st.info(
            "Gender-wise age summary is not available."
        )

        return

    data = data.copy()

    for column in [
        "Average_Age",
        "Minimum_Age",
        "Maximum_Age",
    ]:

        if column in data.columns:

            data[column] = data[column].round(
                1
            )

    st.dataframe(
        data,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# DEMOGRAPHIC INSIGHTS
# ============================================================

def render_insights(
    df: pd.DataFrame,
) -> None:

    st.subheader(
        "Demographic Insights"
    )

    if df.empty:

        st.info(
            "No demographic data is available."
        )

        return

    total = total_respondents(df)

    avg_age = average_age(df)

    gender_data = gender_distribution(df)

    age_data = age_group_distribution(df)

    if gender_data.empty:

        top_gender = "N/A"
        top_gender_count = 0

    else:

        top_gender = str(
            gender_data.iloc[0]["Gender"]
        )

        top_gender_count = int(
            gender_data.iloc[0]["Respondents"]
        )

    if age_data.empty:

        top_age_group = "N/A"
        top_age_group_count = 0

    else:

        valid_age_data = age_data[
            age_data["Age_Group"]
            != "Unknown"
        ]

        if valid_age_data.empty:

            top_age_group = "N/A"
            top_age_group_count = 0

        else:

            top_row = valid_age_data.iloc[
                valid_age_data[
                    "Respondents"
                ].argmax()
            ]

            top_age_group = str(
                top_row["Age_Group"]
            )

            top_age_group_count = int(
                top_row["Respondents"]
            )

    gender_percentage = (
        (
            top_gender_count
            / total
        )
        * 100
        if total > 0
        else 0
    )

    age_percentage = (
        (
            top_age_group_count
            / total
        )
        * 100
        if total > 0
        else 0
    )

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"**Dominant Gender**\n\n"
            f"{top_gender} represents approximately "
            f"{gender_percentage:.1f}% of respondents."
        )

    with col2:

        st.info(
            f"**Dominant Age Group**\n\n"
            f"{top_age_group} represents approximately "
            f"{age_percentage:.1f}% of respondents."
        )

    if avg_age is not None:

        st.success(
            f"**Average Investor Age:** "
            f"{avg_age:.1f} years."
        )


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render() -> None:
    """
    Main entry point used by dashboard/app.py.
    """

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    respondents = load_respondents()

    # --------------------------------------------------------
    # Validate data availability
    # --------------------------------------------------------

    if respondents.empty:

        st.error(
            "Respondent dataset could not be found."
        )

        st.code(
            str(FEATURE_DIR),
            language="text",
        )

        st.info(
            "Make sure your respondent feature CSV "
            "exists inside data/feature/."
        )

        return

    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    respondents = prepare_respondent_data(
        respondents
    )

    respondents = add_age_groups(
        respondents
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # KPI section
    # --------------------------------------------------------

    render_kpis(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Gender distribution
    # --------------------------------------------------------

    render_gender_section(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Age group distribution
    # --------------------------------------------------------

    render_age_group_section(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Age distribution
    # --------------------------------------------------------

    render_age_distribution(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Age × Gender
    # --------------------------------------------------------

    render_age_gender_section(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Gender-wise age summary
    # --------------------------------------------------------

    render_gender_age_summary(
        respondents
    )

    st.divider()

    # --------------------------------------------------------
    # Executive demographic insights
    # --------------------------------------------------------

    render_insights(
        respondents
    )


# ============================================================
# DIRECT STREAMLIT EXECUTION
# ============================================================

if __name__ == "__main__":

    st.set_page_config(
        page_title="Investor Demographics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    render()